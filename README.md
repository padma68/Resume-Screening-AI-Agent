

## 1. Project Title

AI Resume Screening Agent

---

## 2. Project Overview

The AI Resume Screening Agent automates the resume screening process by comparing multiple resumes against a Job Description (JD). It extracts candidate information such as skills, work experience, education, certifications, and projects, computes a relevance score using Natural Language Processing (NLP), ranks candidates based on their suitability, and generates downloadable CSV and JSON reports with explainable scoring.

The project was built to reduce manual resume screening, improve consistency in candidate evaluation, and help recruiters quickly identify the best candidates.


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


## Live Demo

**Web Application Live:**  
[https://resume-screening-ai-agent-2.onrender.com/]

**Resume Screening AI Agent Video Link**  
[https://drive.google.com/file/d/1h96v1KSXnSmo1kEVYSZSwzsOr6p9yOgn/view?usp=sharing]

### Main Capabilities

- Parse resumes in PDF, DOCX, and TXT formats
- Extract skills, education, work experience, certifications, and projects
- Analyze Job Descriptions
- Compute resume relevance using TF-IDF and Cosine Similarity
- Rank candidates based on weighted scoring
- Generate explainable ranking results
- Process 10+ resumes in a single execution
- Export ranked results in CSV and JSON formats
F
---

## 3. Features

- Upload a Job Description
- Upload multiple resumes
- Parse PDF, DOCX, and TXT resumes
- Extract skills, education, experience, certifications, and projects
- NLP-based resume matching
- Candidate ranking
- Explainable scoring
- Batch processing (10+ resumes)
- Export CSV
- Export JSON
- Web interface using Flask

---

## 4. Tech Stack

### Backend

- Python
- Flask

### AI / NLP

- Groq API
- scikit-learn

### Resume Parsing

- PyPDF
- python-docx

### Environment

- python-dotenv

### Testing

- pytest

---

## 5. Project Structure


## Project structure

```
resume-screening-agent/
├── server.py                   # Flask API + serves the frontend (python server.py)
├── static/
│   └── index.html               # hand-built frontend (case-file UI, calls the API)
├── main.py                     # CLI entry point
├── generate_report.py          # static HTML snapshot of a past result
├── requirements.txt
├── .env.example                # copy to .env to configure an LLM key
├── data/
│   ├── job_description.txt     # sample JD (Backend Engineer, ML Platform)
│   └── resumes/                # 11 sample resumes (.pdf, .docx, .txt mixed)
├── output/                     # generated CSV/JSON land here
├── src/
│   ├── parser.py                # file → raw text (.pdf/.docx/.txt)
│   ├── extractor.py             # raw text → structured fields (LLM + fallback)
│   ├── scorer.py                # structured fields → sub-scores → final score
│   ├── ranker.py                # ties it together, ranks, builds reasoning
│   └── llm_client.py            #  # Groq LLM client for structured resume extraction
└── tests/
    └── test_scorer.py            # unit tests for the scoring math
```

---

## 6. Installation

```bash
git clone <repository-url>

cd resume-screening-agent

 pip install -r requirements.txt

```

---

## 7. Environment Variables

Create a `.env` file from `.env.example`.

```env
GROQ_API_KEY=your_api_key
LLM_PROVIDER=groq
```

The project can still run without an API key using TF-IDF similarity. The API key enables enhanced extraction using Groq.

---

## 8. Running the Project

### Run the Web Application

```bash
python server.py
```

Open your browser:

```
http://localhost:5000
```

### OR

### Run from the Command Line

```bash
python main.py --jd data/job_description.txt --resumes data/resumes --output output
```

---

## 9. API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/health | Check application status |
| POST | /api/screen | Upload JD and resumes for screening |

---

## 10. Sample Input

Job Description

```
data/job_description.txt
```

Sample Resumes

```
data/resumes/
```

Include at least 10 sample resumes.

---

## 11. Sample Output

```
output/

ranked_candidates.csv

ranked_candidates.json
```

The CSV contains ranked candidate information for easy viewing, while the JSON provides structured output for integration with other applications.

---

## 12. Scoring Method

```
Final Score

35% Skill Match

30% TF-IDF Similarity

20% Experience

15% Education
```

TF-IDF vectorization converts the Job Description and resumes into numerical vectors. Cosine Similarity measures how closely each resume matches the Job Description. Additional weighted scores are assigned based on skills, experience, and education to produce the final candidate ranking.

---

## 13. Expected Capabilities

- Parse PDF, DOCX, and TXT resumes
- Extract resume information
- Compare resumes with the Job Description
- Rank candidates
- Process 10+ resumes
- Export CSV and JSON reports

---

## 14. Tradeoff Notes

### Why this approach?

- Flask provides a lightweight web framework for deployment.
- TF-IDF offers fast and explainable text similarity.
- Groq API enhances resume field extraction using an LLM.
- Rule-based extraction ensures the application remains functional without external APIs.

### Future Improvements

- OCR support
- Sentence Transformer embeddings
- LinkedIn integration
- GitHub profile analysis
- AI interview question generation
- Fine-tuned recruitment model

---

## 15. Agent-Specific Deliverables

### Job Description

```
data/job_description.txt
```

### Sample Resumes

```
data/resumes/
```

### Ranked Output

```
output/ranked_candidates.csv

output/ranked_candidates.json
```

### Scoring Explanation

Each candidate receives an overall score based on weighted skill matching, semantic similarity, experience, and education. Every sub-score is included to provide transparent and explainable ranking.

---

## 16. Screenshots

Include screenshots of:

- Dashboard
- Upload Page
- Processing Screen
- Ranking Results
- Candidate Details

---

## 17. Testing

Run:

```bash
pytest tests/
```

The test suite validates resume parsing, score calculation, ranking logic, and output generation.

---

Web Application Live: [https://resume-screening-ai-agent-2.onrender.com/]

Resume Screening AI Agent Video Link [https://drive.google.com/file/d/1h96v1KSXnSmo1kEVYSZSwzsOr6p9yOgn/view?usp=sharing]


## 19. Author

Padma Malladi
