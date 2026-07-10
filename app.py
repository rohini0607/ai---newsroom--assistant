"""
app.py
------
AI Newsroom Assistant - main Streamlit application.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd

import prompts
from gemini_client import generate_content, configure_gemini

st.set_page_config(
    page_title="AI Newsroom Assistant",
    page_icon="📰",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.title("📰 AI Newsroom Assistant")
st.sidebar.caption("Generative AI + Prompt Engineering for journalists")

api_key_ok = configure_gemini()
if api_key_ok:
    st.sidebar.success("Gemini API key detected ✅")
else:
    st.sidebar.error(
        "No Gemini API key found.\n\n"
        "Add GEMINI_API_KEY to a `.env` file (see `.env.example`) "
        "or to Streamlit secrets."
    )

feature = st.sidebar.radio(
    "Choose a tool",
    [
        "1. Article Generator",
        "2. Headline Generator",
        "3. Article Summarizer",
        "4. Tone Changer",
        "5. Social Media Generator",
        "6. SEO Keyword Generator",
        "7. Grammar & Style Improvement",
        "8. Prompt Engineering Lab ⭐",
    ],
)

with st.sidebar.expander("⚙️ Generation settings"):
    temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.7, 0.05)
    max_tokens = st.slider("Max output length (tokens)", 128, 2048, 1024, 128)


def run_generation(prompt_text: str, spinner_text: str = "Generating with Gemini...") -> str:
    """Shared helper: call the model and surface errors nicely in the UI."""
    with st.spinner(spinner_text):
        try:
            return generate_content(
                prompt_text, temperature=temperature, max_output_tokens=max_tokens
            )
        except Exception as exc:  # noqa: BLE001
            st.error(str(exc))
            return ""


# ---------------------------------------------------------------------------
# 1. Article Generator
# ---------------------------------------------------------------------------
if feature.startswith("1."):
    st.header("📝 Article Generator")
    topic = st.text_input("News topic", placeholder="e.g. Chennai Metro launches new route")
    if st.button("Generate Article", type="primary", disabled=not topic):
        result = run_generation(prompts.article_prompt(topic))
        if result:
            st.subheader("Generated Article")
            st.write(result)
            st.download_button("Download as .txt", result, file_name="article.txt")

# ---------------------------------------------------------------------------
# 2. Headline Generator
# ---------------------------------------------------------------------------
elif feature.startswith("2."):
    st.header("🏷️ Headline Generator")
    topic = st.text_input("News topic", placeholder="e.g. India's new AI policy announced")
    styles = st.multiselect(
        "Headline styles to generate", prompts.HEADLINE_STYLES, default=prompts.HEADLINE_STYLES
    )
    if st.button("Generate Headlines", type="primary", disabled=not (topic and styles)):
        rows = []
        for style in styles:
            headline = run_generation(
                prompts.headline_prompt(topic, style), spinner_text=f"Writing {style}..."
            )
            if headline:
                rows.append({"Style": style, "Headline": headline})
        if rows:
            st.subheader("Generated Headlines")
            st.table(pd.DataFrame(rows))

# ---------------------------------------------------------------------------
# 3. Article Summarizer
# ---------------------------------------------------------------------------
elif feature.startswith("3."):
    st.header("✂️ Article Summarizer")
    article_text = st.text_area("Paste the full article here", height=250)
    length = st.selectbox("Summary length", ["100 words", "50 words", "One sentence"])
    if st.button("Summarize", type="primary", disabled=not article_text):
        result = run_generation(prompts.summarizer_prompt(article_text, length))
        if result:
            st.subheader("Summary")
            st.write(result)

# ---------------------------------------------------------------------------
# 4. Tone Changer
# ---------------------------------------------------------------------------
elif feature.startswith("4."):
    st.header("🎭 Tone Changer")
    content = st.text_area("Paste content to rewrite", height=200)
    tone = st.selectbox("Target tone", prompts.TONE_OPTIONS)
    if st.button("Rewrite", type="primary", disabled=not content):
        result = run_generation(prompts.tone_change_prompt(content, tone))
        if result:
            st.subheader(f"Rewritten ({tone})")
            st.write(result)

# ---------------------------------------------------------------------------
# 5. Social Media Content Generator
# ---------------------------------------------------------------------------
elif feature.startswith("5."):
    st.header("📱 Social Media Content Generator")
    topic = st.text_input("News topic", placeholder="e.g. New metro route launched in Chennai")
    platforms = st.multiselect(
        "Platforms", prompts.SOCIAL_PLATFORMS, default=prompts.SOCIAL_PLATFORMS
    )
    if st.button("Generate Posts", type="primary", disabled=not (topic and platforms)):
        for platform in platforms:
            post = run_generation(
                prompts.social_media_prompt(topic, platform), spinner_text=f"Writing {platform}..."
            )
            if post:
                st.subheader(platform)
                st.write(post)

# ---------------------------------------------------------------------------
# 6. SEO Keyword Generator
# ---------------------------------------------------------------------------
elif feature.startswith("6."):
    st.header("🔍 SEO Keyword Generator")
    topic = st.text_input("News topic", placeholder="e.g. Union Budget 2026 highlights")
    if st.button("Generate SEO Content", type="primary", disabled=not topic):
        result = run_generation(prompts.seo_prompt(topic))
        if result:
            st.subheader("SEO Output")
            st.text(result)

# ---------------------------------------------------------------------------
# 7. Grammar & Style Improvement
# ---------------------------------------------------------------------------
elif feature.startswith("7."):
    st.header("✅ Grammar & Style Improvement")
    content = st.text_area("Paste text to improve", height=200)
    if st.button("Improve Text", type="primary", disabled=not content):
        result = run_generation(prompts.grammar_prompt(content))
        if result:
            st.subheader("Improved Text")
            st.write(result)

# ---------------------------------------------------------------------------
# 8. Prompt Engineering Lab
# ---------------------------------------------------------------------------
elif feature.startswith("8."):
    st.header("⭐ Prompt Engineering Lab")
    st.caption(
        "Compare how different prompting strategies affect the same news topic."
    )
    topic = st.text_input("News topic", placeholder="e.g. India's AI mission")

    strategy = st.radio(
        "Strategy",
        ["Zero-shot", "Role Prompting", "Few-shot Prompting", "Chain Prompting"],
        horizontal=True,
    )

    if strategy == "Zero-shot":
        st.code(prompts.zero_shot_prompt("{topic}"), language="text")
        if st.button("Run Zero-shot", type="primary", disabled=not topic):
            result = run_generation(prompts.zero_shot_prompt(topic))
            if result:
                st.write(result)

    elif strategy == "Role Prompting":
        st.code(prompts.role_prompt("{topic}"), language="text")
        if st.button("Run Role Prompting", type="primary", disabled=not topic):
            result = run_generation(prompts.role_prompt(topic))
            if result:
                st.write(result)

    elif strategy == "Few-shot Prompting":
        st.code(prompts.few_shot_prompt("{topic}"), language="text")
        if st.button("Run Few-shot Prompting", type="primary", disabled=not topic):
            result = run_generation(prompts.few_shot_prompt(topic))
            if result:
                st.write(result)

    elif strategy == "Chain Prompting":
        st.write("This strategy runs 4 model calls in sequence, each building on the last:")
        st.write("**Step 1: Generate facts → Step 2: Create outline → "
                 "Step 3: Generate article → Step 4: Generate headline**")
        if st.button("Run Chain Prompting", type="primary", disabled=not topic):
            facts = run_generation(prompts.chain_prompt_step1_facts(topic), "Step 1/4: Generating facts...")
            if facts:
                st.markdown("**Step 1 - Facts**")
                st.write(facts)

                outline = run_generation(
                    prompts.chain_prompt_step2_outline(topic, facts), "Step 2/4: Creating outline..."
                )
                st.markdown("**Step 2 - Outline**")
                st.write(outline)

                article = run_generation(
                    prompts.chain_prompt_step3_article(topic, outline), "Step 3/4: Writing article..."
                )
                st.markdown("**Step 3 - Article**")
                st.write(article)

                headline = run_generation(
                    prompts.chain_prompt_step4_headline(article), "Step 4/4: Writing headline..."
                )
                st.markdown("**Step 4 - Headline**")
                st.success(headline)

st.sidebar.divider()
st.sidebar.caption("Built with Streamlit + Gemini API")
