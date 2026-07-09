
# AI Resume Screening Agent

## Project Overview

The **AI Resume Screening Agent** automates the initial resume screening process by analyzing multiple resumes against a given Job Description (JD). It extracts candidate information such as **skills, work experience, education, certifications, and projects** from resumes in **PDF, DOCX, and TXT** formats.

Using **TF-IDF vectorization** and **Cosine Similarity** (scikit-learn), the agent compares each resume with the Job Description to compute a relevance score. Candidates are then ranked from highest to lowest suitability, along with reasoning explaining why they received their score.

The project was built to reduce manual effort in recruitment, improve consistency in resume evaluation, and help recruiters quickly identify the most relevant candidates.

## Main Capabilities

- Parse PDF, DOCX and TXT resumes
- Extract skills, experience, education, certifications and projects
- Analyze Job Descriptions
- Compute NLP similarity using TF-IDF + Cosine Similarity
- Rank 10+ resumes in a single run
- Export results as CSV and JSON
- Provide reasoning for each candidate's ranking

---

# Features

- Upload Job Description
- Upload Multiple Resumes
- Resume Parsing
- Skill Extraction
- Experience Extraction
- Education Extraction
- NLP Similarity Matching
- Candidate Ranking
- AI Reasoning
- CSV Export
- JSON Export

---

# Tech Stack

## Backend
- Python
- Flask

## AI / NLP
- Groq API
- scikit-learn

## Resume Parsing
- PyPDF
- python-docx

## Environment
- python-dotenv

## Testing
- pytest

---

# Requirements

```text
pypdf==5.9.0
python-docx==1.2.0
scikit-learn==1.8.0
groq==1.5.0
pytest==9.1.1
python-dotenv==1.2.2
flask==3.1.3
```

---

# Installation

```bash
git clone https://github.com/yourusername/resume-screening-agent.git

cd resume-screening-agent

pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

```env
GROQ_API_KEY=your_api_key_here
```

---

# Run

```bash
python app.py
```

or

```bash
flask run
```

---

# Project Structure

```text
resume-screening-agent/
├── README.md
├── requirements.txt
├── app.py
├── parser/
├── scoring/
├── utils/
├── templates/
├── static/
├── sample_data/
├── docs/
├── screenshots/
└── tests/
```

---

# Sample Input

```
sample_data/
├── job_description/
│   ├── software_engineer.pdf
│   └── data_analyst.pdf
│
└── resumes/
    ├── resume1.pdf
    ├── resume2.pdf
    ├── ...
    └── resume10.pdf
```

---

# Sample Output

```
sample_data/expected_output/

ranked_candidates.csv

ranked_candidates.json
```

Example:

| Rank | Candidate | Score | Recommendation |
|------|-----------|------:|----------------|
| 1 | John Smith | 94 | Strong Hire |
| 2 | Sarah Wilson | 90 | Hire |
| 3 | David Brown | 85 | Consider |

---

# Scoring Method

| Criteria | Weight |
|----------|-------:|
| Skills Match | 40% |
| Experience | 25% |
| Education | 15% |
| Projects | 10% |
| Certifications | 5% |
| Resume Quality | 5% |

The system extracts structured information from resumes and compares it with the Job Description. TF-IDF vectorization converts text into numerical vectors, and Cosine Similarity measures semantic relevance. The similarity score is combined with weighted scores for skills, education, and experience to generate the final ranking.

---

# Tradeoffs

## Current Limitations

- Scanned PDFs are not supported.
- Images are ignored.
- English resumes only.
- Keyword-based extraction may miss uncommon terminology.
- GitHub and LinkedIn profiles are not analyzed.

## Future Improvements

- OCR support
- Sentence Transformer embeddings
- GitHub profile analysis
- LinkedIn integration
- Interview question generation
- Multi-language support

---

# Deliverables

- Software Engineer Job Description
- Data Analyst Job Description
- 10+ Sample Resumes
- Ranked CSV Output
- Ranked JSON Output
- Scoring Method Documentation
- Screenshots
- Runnable Flask Application

---

# Screenshots

- Dashboard
- Upload Page
- Processing Screen
- Candidate Ranking
- Candidate Details

(Add screenshots after completing the project.)

---

# License

MIT License

---

# Author

Padma Malladi
