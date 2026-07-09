"""
Unit tests for scorer.py. These don't need an LLM API key - they test the
deterministic math directly, which is the part that most needs to be correct
and reproducible.

Run with: pytest tests/
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scorer import text_similarity, skill_match, experience_score, education_score, compute_final_score


def test_text_similarity_identical_text_is_high():
    jd = "Python backend engineer with FastAPI and PostgreSQL experience"
    resume = "Python backend engineer with FastAPI and PostgreSQL experience"
    assert text_similarity(resume, jd) > 0.9


def test_text_similarity_unrelated_text_is_low():
    jd = "Python backend engineer with FastAPI and PostgreSQL experience"
    resume = "Professional chef specializing in French pastry and baking"
    assert text_similarity(resume, jd) < 0.2


def test_skill_match_full_overlap():
    result = skill_match(
        resume_skills=["Python", "FastAPI", "Docker"],
        required=["Python", "FastAPI", "Docker"],
        nice_to_have=[],
    )
    assert result["score"] == 1.0
    assert result["missing_required"] == []


def test_skill_match_partial_overlap():
    result = skill_match(
        resume_skills=["Python"],
        required=["Python", "FastAPI"],
        nice_to_have=[],
    )
    assert 0 < result["score"] < 1.0
    assert "fastapi" in result["missing_required"]


def test_skill_match_no_requirements_returns_zero_not_error():
    result = skill_match(resume_skills=["Python"], required=[], nice_to_have=[])
    assert result["score"] == 0.0


def test_experience_score_meets_requirement():
    assert experience_score(candidate_years=5, min_years_required=3) == 1.0


def test_experience_score_below_requirement():
    score = experience_score(candidate_years=1, min_years_required=4)
    assert score == 0.25


def test_experience_score_no_requirement():
    assert experience_score(candidate_years=0, min_years_required=0) == 1.0


def test_education_score_meets_requirement():
    assert education_score("Master's", "Bachelor's degree required") == 1.0


def test_education_score_below_requirement():
    score = education_score("Diploma", "Master's degree required")
    assert score < 1.0


def test_compute_final_score_is_weighted_average_scaled_to_100():
    sub_scores = {
        "skill_score": 1.0,
        "similarity_score": 1.0,
        "experience_score": 1.0,
        "education_score": 1.0,
    }
    assert compute_final_score(sub_scores) == 100.0


def test_compute_final_score_zero_everything():
    sub_scores = {
        "skill_score": 0.0,
        "similarity_score": 0.0,
        "experience_score": 0.0,
        "education_score": 0.0,
    }
    assert compute_final_score(sub_scores) == 0.0
