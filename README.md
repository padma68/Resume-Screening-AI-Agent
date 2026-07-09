# Resume Screening Agent

Ranks a folder of resumes against a job description and outputs an ordered,
explainable shortlist as CSV and JSON.

The AI Resume Screening Agent automates the resume screening process by comparing multiple resumes against a Job Description (JD). It extracts candidate information, computes a relevance score using Natural Language Processing (NLP), ranks candidates based on their suitability, and generates downloadable CSV and JSON reports with explainable scoring.

---

## What it does

```
Job Description  ─┐
                   ├─► Extract structured fields (skills, min years, education)
Resumes (10+)    ──┘        │
   (.pdf/.docx/.txt)        ▼
                    Score each resume against the JD on 4 axes:
                      - skill overlap (required vs nice-to-have)
                      - TF-IDF text similarity (overall topical fit)
                      - experience vs minimum years required
                      - education level vs requirement
                             │
                             ▼
                    Weighted final score (0–100) + human-readable reasoning
                             │
                             ▼
                 ranked_candidates.csv / .json (sorted, best first)
```
#Features
'''
List the major features.

Example:

Upload a Job Description
Upload multiple resumes
Parse PDF, DOCX, and TXT resumes
Extract skills, education, experience, certifications, and projects
NLP-based resume matching
Candidate ranking
Explainable scoring
Batch processing (10+ resumes)
Export CSV
Export JSON
'''
