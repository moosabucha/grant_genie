from openai import OpenAI
import os
import random


def generate_feedback(profile_text, grant, is_alternative=False):
    """
    Generate personalized feedback for each grant.
    - If API key exists: Real ChatGPT feedback
    - If no API key: Smart unique feedback based on profile + grant content
    """

    api_key = os.environ.get("OPENAI_API_KEY")

    grant_title = grant.get("title", "this grant")
    grant_body = grant.get("body", "UKRI")
    grant_score = grant.get("score", 0)
    grant_text = grant.get("text", "")
    profile_short = profile_text[:500]

    # Real ChatGPT if API key exists
    if api_key:
        try:
            client = OpenAI(api_key=api_key)

            if is_alternative:
                system_msg = """You are a research funding advisor.
A grant scored below 40% match but may still be worth considering.
Write 2-3 sentences explaining:
1. Why it partially relates to the researcher
2. How they could develop their profile to fit this grant better
Be encouraging, specific and never generic."""
            else:
                system_msg = """You are a research funding advisor.
Write 2-3 sentences explaining why this grant is a strong match.
Mention specific keywords, research areas or skills from the profile.
Be specific — never give a generic response."""

            user_msg = f"""Researcher Profile: {profile_short}

Grant Title: {grant_title}
Funded by: {grant_body}
Match Score: {grant_score}%
Grant Description: {grant_text[:300]}

Write personalized feedback for this researcher."""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=200,
                temperature=0.85,
            )
            return response.choices[0].message.content.strip()

        except Exception:
            pass  # Fall through to smart feedback

    # Smart Feedback without API key
    return _smart_feedback(
        profile_short, grant_title, grant_body, grant_score, grant_text, is_alternative
    )


def _extract_keywords(text):
    stop_words = {
        "this",
        "that",
        "with",
        "from",
        "have",
        "been",
        "will",
        "your",
        "their",
        "which",
        "would",
        "about",
        "also",
        "into",
        "more",
        "some",
        "than",
        "then",
        "them",
        "they",
        "were",
        "when",
        "what",
        "where",
        "could",
        "should",
        "shall",
        "make",
        "made",
        "such",
        "each",
        "both",
        "used",
        "using",
        "these",
        "those",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "under",
        "while",
        "within",
        # Common academic words to ignore
        "research",
        "researcher",
        "university",
        "study",
        "studies",
        "project",
        "projects",
        "provide",
        "provides",
        "provided",
        "develop",
        "develops",
        "development",
        "based",
        "approach",
        "including",
        "novel",
        "using",
        "apply",
        "applied",
        "work",
        "enable",
        "enables",
        "innovative",
        "information",
        "primary",
        "areas",
        "results",
        "methods",
        "method",
        "analysis",
        "data",
        # Names — ignore short proper nouns
        "sarah",
        "mitchell",
        "doctor",
        "professor",
        "lecturer",
        "senior",
        "junior",
        "early",
        "career",
        "centre",
        "college",
    }

    # Focus on research domain keywords only
    domain_keywords = [
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "neural network",
        "computer vision",
        "natural language",
        "healthcare",
        "medical",
        "clinical",
        "cancer",
        "disease",
        "climate",
        "carbon",
        "sustainability",
        "renewable",
        "energy",
        "cybersecurity",
        "blockchain",
        "encryption",
        "network",
        "robotics",
        "engineering",
        "quantum",
        "physics",
        "biology",
        "genomics",
        "drug",
        "therapy",
        "vaccine",
        "biomedical",
        "data science",
        "statistics",
        "modelling",
        "simulation",
        "social",
        "policy",
        "education",
        "equality",
        "community",
    ]

    text_lower = text.lower()

    # First try to find domain keywords
    found_domain = [kw for kw in domain_keywords if kw in text_lower]

    if found_domain:
        return found_domain[:5]

    # Fallback — extract words but filter better
    words = text.lower().split()
    keywords = [
        w.strip(".,()[]{}:;\"'-")
        for w in words
        if len(w) > 5
        and w.lower() not in stop_words
        and w.isalpha()
        and not w[0].isupper()  # Skip proper nouns
    ]

    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique.append(kw)
    return unique[:5]


def _find_common_keywords(profile_text, grant_text):
    """Find keywords that appear in both profile and grant."""
    profile_kws = set(_extract_keywords(profile_text))
    grant_kws = set(_extract_keywords(grant_text))
    common = list(profile_kws & grant_kws)
    return common[:4] if common else []


def _smart_feedback(profile, title, funder, score, grant_text, is_alternative):
    """Generate unique, realistic feedback based on actual content."""

    common_kws = _find_common_keywords(profile, grant_text)
    profile_kws = _extract_keywords(profile)[:5]
    grant_kws = _extract_keywords(grant_text)[:5]

    # Format keyword strings
    if common_kws:
        shared = ", ".join(common_kws[:2])
    else:
        shared = profile_kws[0] if profile_kws else "your research area"

    profile_focus = profile_kws[0] if profile_kws else "your research expertise"
    grant_focus = ", ".join(grant_kws[:2]) if grant_kws else "the grant objectives"
    grant_focus2 = grant_kws[0] if grant_kws else "this research area"

    if is_alternative:
        templates = [
            f"This {funder} opportunity in {grant_focus} scored {score}% against your profile. "
            f"Although below the 40% threshold, the overlap with {shared} suggests potential "
            f"relevance if you expand your work in {grant_focus2}.",
            f"With {score}% alignment, '{title}' sits in the alternative pool. "
            f"Your strength in {profile_focus} has partial relevance to {grant_focus}, "
            f"making this worth revisiting as your research evolves.",
            f"This {funder} grant focuses on {grant_focus}, which partially connects "
            f"to your expertise in {shared}. At {score}%, consider this as a future "
            f"collaborative opportunity or secondary application.",
            f"The {score}% match reflects a partial connection between your work in "
            f"{profile_focus} and this grant's focus on {grant_focus}. "
            f"Monitor future rounds of this {funder} opportunity as your profile develops.",
            f"'{title}' scored {score}% — just below the primary threshold. "
            f"Your background in {shared} overlaps with {grant_focus2}, "
            f"suggesting this {funder} grant could become more relevant with targeted research.",
            f"Although {score}% places this grant in the alternative pool, "
            f"your expertise in {profile_focus} aligns with elements of {grant_focus}. "
            f"This {funder} opportunity is worth keeping on your radar for future applications.",
        ]
    else:
        templates = [
            f"Your expertise in {profile_focus} directly aligns with this {funder} grant's "
            f"focus on {grant_focus}, achieving a strong {score}% match. "
            f"The overlap in {shared} makes this a priority application.",
            f"With {score}% alignment, '{title}' is a strong match for your profile. "
            f"Your work in {shared} closely mirrors the grant's objectives in {grant_focus}, "
            f"positioning you as a competitive candidate.",
            f"This {funder} opportunity scores {score}% against your profile, "
            f"driven by your background in {profile_focus}. "
            f"The grant's emphasis on {grant_focus} directly complements your research goals.",
            f"Your documented skills in {shared} place you in an excellent position "
            f"for this {funder} grant focusing on {grant_focus}. "
            f"At {score}% match, this is a recommended priority application.",
            f"The {score}% match reflects strong compatibility between your research in "
            f"{profile_focus} and '{title}' from {funder}. "
            f"Your focus on {shared} addresses the core objectives of this funding call.",
            f"'{title}' from {funder} achieves {score}% alignment with your profile "
            f"due to your expertise in {shared}. "
            f"This grant's focus on {grant_focus} makes it an ideal funding opportunity.",
        ]

    # Different index calculation — uses title length + score for more variety
    unique_key = len(title) + int(score * 10) + len(grant_focus) + len(profile_focus)
    index = unique_key % len(templates)
    return templates[index]
