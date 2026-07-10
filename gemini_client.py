"""
gemini_client.py
-----------------
Thin wrapper around the Google Gemini API (google-generativeai SDK).

Keeping all model-calling logic in one place makes it easy to:
- swap models later
- add retries / caching
- unit test prompt logic without hitting the real API
"""

import os
import time
import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors as genai_errors
from dotenv import load_dotenv

load_dotenv()

# Google keeps retiring specific model snapshots (gemini-1.5-flash, then
# gemini-2.5-flash for new API keys, etc). Rather than hardcode one name that
# will eventually 404 again, we try a *list* of current models in order and
# fall through to the next one if a model is unavailable. "gemini-flash-latest"
# is an alias Google keeps pointed at whatever the current Flash model is, so
# it's first.
_env_model = os.getenv("GEMINI_MODEL", "").strip()
FALLBACK_MODELS = [m for m in [
    _env_model,          # honor an explicit override in .env, if set
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
] if m]
DEFAULT_MODEL = FALLBACK_MODELS[0]


def _get_api_key() -> str:
    """
    Look for the API key in this order:
    1. Streamlit secrets (st.secrets) - used when deployed on Streamlit Cloud
    2. Environment variable / .env file - used for local development
    """
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass  # st.secrets is unavailable (e.g. no secrets.toml locally) - that's fine

    return os.getenv("GEMINI_API_KEY", "")


def configure_gemini() -> bool:
    """Check whether an API key is available. Returns True if a key was found."""
    return bool(_get_api_key())


@st.cache_resource(show_spinner=False)
def get_client():
    """Cache the client object so we don't re-initialize it on every rerun."""
    return genai.Client(api_key=_get_api_key())


def _is_model_unavailable_error(exc: Exception) -> bool:
    """True if the error means 'this model name doesn't exist / was retired'
    (as opposed to a rate limit, network blip, or bad prompt)."""
    message = str(exc).lower()
    return (
        isinstance(exc, genai_errors.APIError)
        and getattr(exc, "code", None) == 404
    ) or "not_found" in message or "no longer available" in message or "not found" in message


def generate_content(
    prompt: str,
    model_name: str | None = None,
    temperature: float = 0.7,
    max_output_tokens: int = 1024,
    retries: int = 2,
) -> str:
    """
    Send a prompt to Gemini and return the generated text.
    - Retries transient failures (rate limits, network errors) with backoff.
    - If a model name itself is unavailable/retired, automatically moves on
      to the next model in FALLBACK_MODELS instead of failing outright.
    """
    if not configure_gemini():
        raise RuntimeError(
            "No Gemini API key found. Add GEMINI_API_KEY to your .env file "
            "(local) or to Streamlit secrets (deployed app)."
        )

    client = get_client()
    base_kwargs = dict(temperature=temperature, max_output_tokens=max_output_tokens)
    # Newer Gemini Flash models "think" before answering, and that thinking
    # eats into max_output_tokens - which was cutting our articles off
    # mid-sentence. None of our newsroom tasks need deep reasoning, so we try
    # to turn thinking off first and give the full budget to the visible
    # output. A few models don't support disabling it, so we fall back to a
    # plain config (no thinking_config) for those instead of giving up.
    configs_to_try = [
        types.GenerateContentConfig(
            **base_kwargs, thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
        types.GenerateContentConfig(**base_kwargs),
    ]

    def _call(candidate_model: str, config):
        """Try one (model, config) pair with retries.
        Returns (text, skip_model) - text is None on failure, and
        skip_model is True if the whole model (not just this config) is a
        lost cause, so the caller shouldn't bother trying other configs on it.
        """
        for attempt in range(retries + 1):
            try:
                response = client.models.generate_content(
                    model=candidate_model, contents=prompt, config=config
                )
                text = (response.text or "").strip()
                if not text:
                    raise ValueError("Model returned an empty response.")
                return text, False
            except Exception as exc:  # noqa: BLE001
                nonlocal last_error
                last_error = exc
                if _is_model_unavailable_error(exc):
                    return None, True  # this model name is dead - skip it entirely
                if "thinking" in str(exc).lower():
                    return None, False  # just this config is unsupported - try next config
                if attempt < retries:
                    time.sleep(1.5 * (attempt + 1))
        return None, False

    models_to_try = [model_name] if model_name else FALLBACK_MODELS
    last_error = None

    for candidate_model in models_to_try:
        for config in configs_to_try:
            result, skip_model = _call(candidate_model, config)
            if result is not None:
                return result
            if skip_model:
                break  # try the next model instead of the next config

    raise RuntimeError(
        f"Gemini request failed on every model tried ({models_to_try}). "
        f"Last error: {last_error}"
    ) from last_error