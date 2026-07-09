"""
scorer.py
Computes a relevance score for each resume against the JD.

Design choice - hybrid scoring, not a single black-box number:

  final_score = 0.35 * skill_match_score
              + 0.30 * text_similarity_score   (TF-IDF cosine similarity)
              + 0.20 * experience_score
              + 0.15 * education_score

Why hybrid instead of "just ask the LLM to give a score 0-100"?
1. LLM-only scoring is not reproducible - same resume can get different
   scores on different runs, and it's a black box with no auditable reasoning.
2. TF-IDF cosine similarity is a genuine, deterministic NLP similarity method
   (bag-of-words + inverse document frequency weighting) that catches overall
   topical overlap between resume and JD, not just skill-list matching.
3. Skill overlap (from the LLM-extracted structured fields) catches the
   specific must-haves a pure text-similarity score can miss or over/under-weight.
4. Experience and education are compared numerically/categorically, not via
   fuzzy text similarity, because "5 years" vs "3-6 years required" is a
   precise comparison, not a similarity comparison.

Every sub-score is stored, so the final CSV/JSON output is fully explainable -
a reviewer can see exactly why one candidate ranked above another.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def text_similarity(resume_text: str, jd_text: str) -> float:
    """TF-IDF cosine similarity between full resume text and full JD text, 0-1."""
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
    sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(sim), 4)


def skill_match(resume_skills: list[str], required: list[str], nice_to_have: list[str]) -> dict:
    """Weighted overlap: required skills matter 3x as much as nice-to-have."""
    resume_skills_lower = {s.lower().strip() for s in resume_skills}
    required_lower = {s.lower().strip() for s in required}
    nice_lower = {s.lower().strip() for s in nice_to_have}

    matched_required = required_lower & resume_skills_lower
    matched_nice = nice_lower & resume_skills_lower
    missing_required = required_lower - resume_skills_lower

    max_points = len(required_lower) * 3 + len(nice_lower) * 1
    earned_points = len(matched_required) * 3 + len(matched_nice) * 1
    score = (earned_points / max_points) if max_points > 0 else 0.0

    return {
        "score": round(score, 4),
        "matched_required": sorted(matched_required),
        "matched_nice_to_have": sorted(matched_nice),
        "missing_required": sorted(missing_required),
    }


def experience_score(candidate_years: float, min_years_required: float) -> float:
    """1.0 if meets/exceeds requirement, scaled down proportionally if below."""
    if min_years_required <= 0:
        return 1.0
    if candidate_years >= min_years_required:
        # small bonus cap - don't let 20 years vs 3 required blow out the score
        return 1.0
    return round(max(0.0, candidate_years / min_years_required), 4)


def education_score(candidate_level: str, requirement: str) -> float:
    """Simple ordinal comparison: Diploma < Bachelor's < Master's < PhD."""
    order = {"none": 0, "diploma": 1, "other": 1, "bachelor's": 2, "master's": 3, "phd": 4}
    cand = order.get((candidate_level or "").lower(), 1)
    # crude parse of requirement string for a minimum level
    req_text = (requirement or "").lower()
    if "phd" in req_text:
        req = 4
    elif "master" in req_text:
        req = 3
    elif "bachelor" in req_text:
        req = 2
    else:
        req = 1
    return 1.0 if cand >= req else round(cand / req, 4)


def compute_final_score(sub_scores: dict, weights: dict | None = None) -> float:
    weights = weights or {"skills": 0.35, "similarity": 0.30, "experience": 0.20, "education": 0.15}
    final = (
        weights["skills"] * sub_scores["skill_score"]
        + weights["similarity"] * sub_scores["similarity_score"]
        + weights["experience"] * sub_scores["experience_score"]
        + weights["education"] * sub_scores["education_score"]
    )
    return round(final * 100, 2)  # scale to 0-100 for readability
