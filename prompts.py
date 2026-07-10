"""
prompts.py
----------
All prompt templates live here, separated from UI and API code.
This is the "prompt engineering" heart of the project - each function
builds a carefully worded prompt string for a specific task or strategy.
"""

# ---------------------------------------------------------------------------
# 1. Article Generator
# ---------------------------------------------------------------------------
def article_prompt(topic: str) -> str:
    return f"""You are an experienced news journalist writing for a reputable daily newspaper.

Write a complete, factually neutral news article about the following topic:
"{topic}"

Requirements:
- Start with a strong lead paragraph answering who/what/when/where/why.
- Use an inverted-pyramid structure (most important information first).
- Keep the tone objective and professional, with no personal opinions.
- Length: 300-400 words.
- Do not fabricate quotes from named real people; use general attributions
  like "officials said" if needed.
"""


# ---------------------------------------------------------------------------
# 2. Headline Generator
# ---------------------------------------------------------------------------
HEADLINE_STYLES = [
    "Breaking News headline",
    "SEO headline",
    "Newspaper headline",
    "Social Media headline",
    "Professional headline",
]


def headline_prompt(topic: str, style: str) -> str:
    return f"""Write ONE {style} for a news story about: "{topic}"

Guidelines for a {style}:
- Breaking News headline: urgent, short, uses present tense.
- SEO headline: includes likely search keywords, under 60 characters.
- Newspaper headline: concise, punchy, print-style.
- Social Media headline: attention-grabbing, can include an emoji.
- Professional headline: formal, clear, no clickbait.

Return only the headline text, nothing else.
"""


# ---------------------------------------------------------------------------
# 3. Article Summarizer
# ---------------------------------------------------------------------------
def summarizer_prompt(article_text: str, length: str) -> str:
    length_instruction = {
        "100 words": "Summarize the article in about 100 words.",
        "50 words": "Summarize the article in about 50 words.",
        "One sentence": "Summarize the article in exactly one clear sentence.",
    }[length]

    return f"""{length_instruction}
Preserve the key facts and do not add new information.

Article:
\"\"\"
{article_text}
\"\"\"
"""


# ---------------------------------------------------------------------------
# 4. Tone Changer
# ---------------------------------------------------------------------------
TONE_OPTIONS = [
    "Formal",
    "Professional",
    "Friendly",
    "Simple English",
    "Breaking News",
    "Editorial",
]


def tone_change_prompt(content: str, tone: str) -> str:
    return f"""Rewrite the following content in a {tone} tone.
Keep the meaning and facts identical - only change the style, word choice,
and sentence structure to match the {tone} tone.

Original content:
\"\"\"
{content}
\"\"\"
"""


# ---------------------------------------------------------------------------
# 5. Social Media Content Generator
# ---------------------------------------------------------------------------
SOCIAL_PLATFORMS = ["Twitter/X post", "LinkedIn post", "Facebook post", "Instagram caption"]


def social_media_prompt(topic: str, platform: str) -> str:
    platform_rules = {
        "Twitter/X post": "under 280 characters, punchy, may include 1-2 relevant hashtags",
        "LinkedIn post": "professional tone, 3-5 sentences, thought-leadership style, optional hashtags",
        "Facebook post": "conversational, 2-4 sentences, inviting engagement/comments",
        "Instagram caption": "engaging, can include emojis and 3-5 hashtags at the end",
    }[platform]

    return f"""Write a {platform} announcing this news topic: "{topic}"

Style rules for this platform: {platform_rules}
Return only the post text.
"""


# ---------------------------------------------------------------------------
# 6. SEO Keyword Generator
# ---------------------------------------------------------------------------
def seo_prompt(topic: str) -> str:
    return f"""You are an SEO specialist for a news website.
For the news topic: "{topic}", generate:

1. Primary keyword (1 phrase)
2. Secondary keywords (5 phrases, comma-separated)
3. Meta description (max 155 characters, compelling and keyword-rich)
4. Tags (8 short tags, comma-separated)

Format your response with clear labeled sections exactly as:
Primary Keyword:
Secondary Keywords:
Meta Description:
Tags:
"""


# ---------------------------------------------------------------------------
# 7. Grammar & Style Improvement
# ---------------------------------------------------------------------------
def grammar_prompt(content: str) -> str:
    return f"""Proofread and improve the following text.
Fix grammar, punctuation, and sentence structure issues.
Improve readability and flow while keeping the original meaning and facts unchanged.
Return only the corrected text (no explanations).

Text:
\"\"\"
{content}
\"\"\"
"""


# ---------------------------------------------------------------------------
# 8. Prompt Engineering Lab
# ---------------------------------------------------------------------------
def zero_shot_prompt(topic: str) -> str:
    """Simplest strategy: just ask directly, no extra context or examples."""
    return f"Write a news article about: {topic}"


def role_prompt(topic: str) -> str:
    """Adds a persona/role to steer tone and authority."""
    return f"""You are a senior editor at a respected national daily newspaper.
Write a clear, unbiased, well-structured news article about: {topic}
Maintain journalistic neutrality and cite general sources where relevant
(e.g. "according to officials").
"""


def few_shot_prompt(topic: str) -> str:
    """Provides example input/output pairs before the real task."""
    return f"""Here are examples of short news article openings:

Example 1
Topic: New airport terminal opens
Article: The city's international airport unveiled its new terminal today, \
adding capacity for an additional 5 million passengers annually. Officials \
said the expansion reflects growing demand for regional air travel.

Example 2
Topic: Local school wins national award
Article: A local high school was recognized with a national excellence \
award this week for its innovative STEM program, which has doubled \
student participation in science fairs over the past two years.

Now write a similar style news article opening (3-4 sentences) for this topic:
Topic: {topic}
Article:"""


def chain_prompt_step1_facts(topic: str) -> str:
    """Step 1 of chain prompting: extract/generate plausible key facts."""
    return f"""List 5 plausible key facts (bullet points) that a news article
about "{topic}" would typically need to cover (who, what, when, where, why/impact).
Do not write the article yet, only the facts."""


def chain_prompt_step2_outline(topic: str, facts: str) -> str:
    """Step 2: turn facts into a structured outline."""
    return f"""Using these facts:
{facts}

Create a short news article outline for the topic "{topic}" with these sections:
1. Lead paragraph focus
2. Body paragraph(s) focus
3. Closing/impact paragraph focus
"""


def chain_prompt_step3_article(topic: str, outline: str) -> str:
    """Step 3: expand the outline into a full article."""
    return f"""Using this outline:
{outline}

Write a complete, well-structured news article (300-350 words) about "{topic}".
Keep a neutral, professional journalistic tone.
"""


def chain_prompt_step4_headline(article: str) -> str:
    """Step 4: generate a headline from the finished article."""
    return f"""Write one strong, concise newspaper headline for this article:

\"\"\"
{article}
\"\"\"

Return only the headline.
"""
