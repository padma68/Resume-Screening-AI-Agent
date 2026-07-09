"""
ranker.py
Ties parsing -> extraction -> scoring together, ranks candidates, and builds
a human-readable reasoning string for each one.

Reasoning is generated deterministically from the computed sub-scores (not by
asking the LLM to "explain the ranking" after the fact). This guarantees the
explanation always matches the actual math behind the score - no risk of the
LLM hallucinating a justification that doesn't match the number.
"""

from src.extractor import extract_resume_fields, extract_jd_fields
from src.scorer import (
    text_similarity,
    skill_match,
    experience_score,
    education_score,
    compute_final_score,
)


def build_reasoning(name: str, skill_result: dict, exp_score: float, edu_score: float,
                     candidate_years: float, min_years: float) -> str:
    parts = []

    if skill_result["matched_required"]:
        parts.append(
            f"Matches {len(skill_result['matched_required'])} required skill(s): "
            f"{', '.join(skill_result['matched_required'])}"
        )
    if skill_result["missing_required"]:
        parts.append(
            f"Missing required skill(s): {', '.join(skill_result['missing_required'])}"
        )
    if skill_result["matched_nice_to_have"]:
        parts.append(
            f"Also has nice-to-have: {', '.join(skill_result['matched_nice_to_have'])}"
        )

    if min_years > 0:
        if candidate_years >= min_years:
            parts.append(f"Meets experience requirement ({candidate_years:.0f}y vs {min_years:.0f}y required)")
        else:
            parts.append(f"Below experience requirement ({candidate_years:.0f}y vs {min_years:.0f}y required)")

    if edu_score < 1.0:
        parts.append("Education level below stated requirement")

    return "; ".join(parts) if parts else "No strong signals found relative to JD."


def rank_resumes(resumes: dict[str, str], jd_text: str, verbose: bool = True, on_progress=None) -> list[dict]:
    """
    on_progress, if given, is called as on_progress(filename, stage) at each
    step, where stage is one of: "jd_parsed", "llm_extracting",
    "llm_extracted", "nlp_scoring", "scored". filename is None for the
    JD-level stage. This lets a UI (see app.py) show which stage - LLM
    extraction vs NLP scoring - is active for which file, live.
    """
    if verbose:
        print("Extracting structured fields from job description...")
    if on_progress:
        on_progress(None, "jd_parsed")
    jd_fields = extract_jd_fields(jd_text)

    results = []
    for filename, resume_text in resumes.items():
        if verbose:
            print(f"Processing {filename}...")
        if on_progress:
            on_progress(filename, "llm_extracting")

        resume_fields = extract_resume_fields(resume_text)

        if on_progress:
            on_progress(filename, "nlp_scoring")

        sim_score = text_similarity(resume_text, jd_text)
        skill_result = skill_match(
            resume_fields.get("skills", []),
            jd_fields.get("required_skills", []),
            jd_fields.get("nice_to_have_skills", []),
        )
        exp_score = experience_score(
            resume_fields.get("years_experience", 0),
            jd_fields.get("min_years_experience", 0),
        )
        edu_score = education_score(
            resume_fields.get("education_level", "Other"),
            jd_fields.get("education_requirement", ""),
        )

        sub_scores = {
            "skill_score": skill_result["score"],
            "similarity_score": sim_score,
            "experience_score": exp_score,
            "education_score": edu_score,
        }
        final_score = compute_final_score(sub_scores)

        reasoning = build_reasoning(
            filename, skill_result, exp_score, edu_score,
            resume_fields.get("years_experience", 0),
            jd_fields.get("min_years_experience", 0),
        )

        results.append({
            "filename": filename,
            "final_score": final_score,
            "skill_score": round(skill_result["score"] * 100, 2),
            "similarity_score": round(sim_score * 100, 2),
            "experience_score": round(exp_score * 100, 2),
            "education_score": round(edu_score * 100, 2),
            "years_experience": resume_fields.get("years_experience", 0),
            "resume_extraction_mode": resume_fields.get("_extraction_mode", "Unknown"),
            "resume_extraction_error": resume_fields.get("_extraction_error", ""),
            "matched_required_skills": ", ".join(skill_result["matched_required"]),
            "missing_required_skills": ", ".join(skill_result["missing_required"]),
            "matched_nice_to_have_skills": ", ".join(skill_result["matched_nice_to_have"]),
            "reasoning": reasoning,
        })

        if on_progress:
            on_progress(filename, "scored")

    results.sort(key=lambda r: r["final_score"], reverse=True)
    for i, r in enumerate(results, start=1):
        r["rank"] = i

    if on_progress:
        on_progress(None, "ranked")

    return results
