# 📰 AI Newsroom Assistant

**🔗 Live demo:** [Try it live →](https://ai---newsroom--assistant-ogzwau8wqq6qhpkuuxyu9n.streamlit.app/)

An AI-powered content generation platform for journalists, writers, and editors, built with **Python**, **Streamlit**, and the **Gemini API**. It demonstrates practical prompt engineering — Zero-shot, Role Prompting, Few-shot Prompting, and Chain Prompting — across 8 real newsroom tools.

## Features

| # | Tool | What it does |
|---|------|---------------|
| 1 | Article Generator | Full news article from a topic |
| 2 | Headline Generator | Breaking News / SEO / Newspaper / Social Media / Professional headlines |
| 3 | Article Summarizer | Condense an article to 100 words / 50 words / one sentence |
| 4 | Tone Changer | Rewrite content as Formal, Friendly, Editorial, etc. |
| 5 | Social Media Generator | Twitter/X, LinkedIn, Facebook, Instagram posts |
| 6 | SEO Keyword Generator | Primary/secondary keywords, meta description, tags |
| 7 | Grammar & Style Improvement | Proofread and polish text |
| 8 | Prompt Engineering Lab ⭐ | Compare Zero-shot / Role / Few-shot / Chain prompting on the same topic |

## Project structure

```
ai_newsroom_assistant/
├── app.py                          # Streamlit UI - main entry point
├── prompts.py                      # All prompt templates (the "prompt engineering")
├── gemini_client.py                # Gemini API wrapper (auth, retries, caching)
├── requirements.txt                # Python dependencies
├── .env.example                    # Template for your local API key
├── .streamlit/secrets.toml.example # Template for Streamlit Cloud deployment
└── .gitignore
```

## 1. Prerequisites

- Python 3.9+
- A free Gemini API key from **https://aistudio.google.com/app/apikey**

## 2. Setup

```bash
# 1. Go into the project folder
cd ai_newsroom_assistant

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# then open .env and paste your key:
# GEMINI_API_KEY=AIza...your_real_key...
```

## 3. Run the app

```bash
streamlit run app.py
```

Streamlit will print a local URL, typically:

```
Local URL: http://localhost:8501
```

Open that URL in your browser. Pick a tool from the left sidebar, fill in the inputs, and click Generate.

## 4. Deploying to Streamlit Community Cloud (optional)

1. Push this folder to a GitHub repository (the `.gitignore` already keeps your real `.env` / `secrets.toml` out of git).
2. Go to https://share.streamlit.io, connect the repo, and set the main file to `app.py`.
3. In the app's **Settings → Secrets**, paste:
   ```
   GEMINI_API_KEY = "your_real_key"
   ```
4. Deploy. `gemini_client.py` automatically checks `st.secrets` first, so no code changes are needed.

## 5. How the prompt engineering is organized

All prompt-building logic lives in `prompts.py`, completely separate from the UI (`app.py`) and the API call logic (`gemini_client.py`). This separation makes it easy to:

- Tweak a prompt without touching UI code.
- Explain in an interview exactly why each prompt is worded the way it is.
- Add new strategies (e.g. self-consistency, tree-of-thought) later without restructuring the app.

The **Prompt Engineering Lab** tab is the centerpiece: it lets you run the same topic through four different strategies and see how the wording of the prompt changes the output quality:

- **Zero-shot** — a bare instruction, no extra context.
- **Role Prompting** — assigns the model a persona ("senior editor") to steer tone/authority.
- **Few-shot Prompting** — shows the model 2 worked examples before asking it to generate.
- **Chain Prompting** — breaks article writing into 4 sequential model calls (facts → outline → article → headline), each call using the previous call's output.

## 6. Troubleshooting

- **"No Gemini API key found"** — make sure `.env` exists (not just `.env.example`) and contains a valid `GEMINI_API_KEY`, then restart `streamlit run app.py`.
- **429 / rate limit errors** — the free Gemini tier has request limits; wait a moment and retry, or lower the "Max output length" slider.
- **Empty output** — try increasing the temperature slightly or shortening your input text.

## 7. Possible future enhancements

- Multi-language support (English & Tamil)
- Voice-to-Article generation
- AI fact-checking pass
- Image generation for news
- PDF export of generated content
- User authentication + article history database
