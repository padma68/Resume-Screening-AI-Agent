"""
extractor.py
Uses the LLM to turn unstructured text (resume or JD) into structured JSON:
skills, years of experience, education level/field.

Why the LLM does this instead of regex: resumes are written in wildly
inconsistent formats ("5 yrs", "2019-Present", "Senior x3 years"). An LLM
generalizes across phrasing far better than hand-written regex, and this is
exactly the kind of "understand unstructured text" task LLMs are good at.

If no API key is configured, we fall back to a simple keyword/regex-based
extractor so the pipeline still runs end-to-end for a quick demo (with
noticeably lower accuracy - this tradeoff is documented in the README).
"""

import json
import os
import re

from src.llm_client import get_completion

RESUME_EXTRACTION_PROMPT = """You are an information-extraction engine for a resume \
screening system. Read the resume text below and return ONLY a JSON object \
(no markdown fences, no commentary) with this exact shape:

{{
  "skills": ["skill1", "skill2", ...],
  "years_experience": <number, total professional experience, estimate from dates if not stated>,
  "education_level": "Bachelor's" | "Master's" | "PhD" | "Diploma" | "None",
  "education_field": "<field of study, e.g. Computer Science>"
}}

Rules:
- List skills as they would appear in a job description (normalize casing, e.g. "Python" not "python").
- Include technical skills, tools, frameworks, and languages only - not soft skills.
- If years of experience isn't stated explicitly, estimate from the date ranges of jobs listed.
- Return ONLY the JSON object.

Resume text:
---
{text}
---
"""

JD_EXTRACTION_PROMPT = """You are an information-extraction engine for a resume \
screening system. Read the job description below and return ONLY a JSON object \
(no markdown fences, no commentary) with this exact shape:

{{
  "required_skills": ["skill1", "skill2", ...],
  "nice_to_have_skills": ["skill1", ...],
  "min_years_experience": <number, minimum years required, 0 if not specified>,
  "education_requirement": "<e.g. Bachelor's in Computer Science or related field>"
}}

Rules:
- Separate must-have/required skills from nice-to-have/preferred skills based on how the JD frames them.
- Return ONLY the JSON object.

Job description text:
---
{text}
---
"""


def _parse_json_response(raw: str) -> dict:
    """LLMs sometimes wrap JSON in fences or add stray text - clean before parsing."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I).strip()
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.I).strip()

    if not cleaned:
        raise ValueError("Empty model response")

    # Try to extract the first balanced JSON object from the model output.
    start = cleaned.find("{")
    if start != -1:
        brace_depth = 0
        in_string = False
        escape = False
        end = None
        for idx, char in enumerate(cleaned[start:], start=start):
            if escape:
                escape = False
                continue
            if char == "\\":
                escape = True
                continue
            if char == '"':
                in_string = not in_string
            elif not in_string:
                if char == "{":
                    brace_depth += 1
                elif char == "}":
                    brace_depth -= 1
                    if brace_depth == 0:
                        end = idx
                        break
        if end is not None:
            candidate = cleaned[start:end + 1].strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

    # Fallback: try the entire cleaned text once more before failing.
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON from model response: {e}; raw response: {raw!r}"
        ) from e


def extract_resume_fields(resume_text: str) -> dict:
    try:
        prompt = RESUME_EXTRACTION_PROMPT.format(text=resume_text[:6000])
        raw = get_completion(
            system_prompt="You extract structured data from resumes. Output only valid JSON.",
            user_prompt=prompt,
        )
        fields = _parse_json_response(raw)
        fields["_extraction_mode"] = "LLM-assisted extraction"
        return fields
    except Exception as e:
        print(f"  [WARN] LLM extraction failed ({e}); falling back to heuristic extraction.")
        fields = _fallback_resume_extraction(resume_text)
        fields["_extraction_mode"] = "Heuristic fallback"
        fields["_extraction_error"] = str(e)
        return fields


def extract_jd_fields(jd_text: str) -> dict:
    try:
        prompt = JD_EXTRACTION_PROMPT.format(text=jd_text[:6000])
        raw = get_completion(
            system_prompt="You extract structured data from job descriptions. Output only valid JSON.",
            user_prompt=prompt,
        )
        fields = _parse_json_response(raw)
        fields["_extraction_mode"] = "LLM-assisted extraction"
        return fields
    except Exception as e:
        print(f"  [WARN] LLM extraction failed ({e}); falling back to heuristic extraction.")
        fields = _fallback_jd_extraction(jd_text)
        fields["_extraction_mode"] = "Heuristic fallback"
        fields["_extraction_error"] = str(e)
        return fields


# ---------------------------------------------------------------------------
# Fallback heuristics (used only if the LLM call fails or no API key is set)
# ---------------------------------------------------------------------------

_COMMON_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "Kotlin", "SQL", "PostgreSQL",
    "MySQL", "MongoDB", "Redis", "FastAPI", "Flask", "Django", "Django REST Framework",
    "Node.js", "Express", "React", "Docker", "Kubernetes", "AWS", "GCP", "Azure",
    "Terraform", "Kafka", "RabbitMQ", "SQS", "PyTorch", "TensorFlow", "scikit-learn",
    "Git", "CI/CD", "Jenkins", "GitHub Actions", "Prometheus", "Grafana",
    "Data Structures & Algorithms", "Spring Boot", "Tableau", "Power BI", "Excel",
]


def _fallback_resume_extraction(text: str) -> dict:
    found_skills = [s for s in _COMMON_SKILLS if s.lower() in text.lower()]
    if re.search(r"\b(fresher|fresh graduate|entry[- ]level|recent graduate|new grad|graduate trainee)\b", text, re.I):
        years = 0.0
    else:
        years = _estimate_years(text)
    education_level = "Bachelor's" if re.search(r"b\.?tech|b\.?e\.?|bachelor", text, re.I) else "Other"
    return {
        "skills": found_skills,
        "years_experience": years,
        "education_level": education_level,
        "education_field": "Unknown",
    }


def _fallback_jd_extraction(text: str) -> dict:
    found_skills = [s for s in _COMMON_SKILLS if s.lower() in text.lower()]
    years_match = re.search(r"(\d+)\s*-\s*(\d+)\s*years", text)
    min_years = int(years_match.group(1)) if years_match else 0
    return {
        "required_skills": found_skills,
        "nice_to_have_skills": [],
        "min_years_experience": min_years,
        "education_requirement": "Bachelor's degree",
    }


def _estimate_years(text: str) -> float:
    """Very rough: sum up year ranges like 2020-2022, 2022-Present."""
    ranges = re.findall(r"(20\d{2})\s*[-–]\s*(20\d{2}|Present)", text)
    total = 0
    for start, end in ranges:
        end_year = 2026 if "present" in end.lower() else int(end)
        total += max(0, end_year - int(start))
    return float(total) if total else 0.0
