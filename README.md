# Resume Screening Agent

Ranks a folder of resumes against a job description and outputs an ordered,
explainable shortlist as CSV and JSON.

Built for the Rooman Technologies 24-Hour AI Agent Challenge (Junior AI
Research Associate — Resume Screening Agent track).

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

## Quick start

```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd resume-screening-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) configure an LLM key for higher-accuracy field extraction
cp .env.example .env
# edit GROQ_API_KEY depending on your provider
# set LLM_PROVIDER=groq in .env

# 4. Run it on the included sample data
python main.py --jd data/job_description.txt --resumes data/resumes --output output
```

That's it — no API key is required to get a working result. See
[Two-tier extraction](#two-tier-extraction-llm--heuristic-fallback) below for
why.

### Output

- `output/ranked_candidates.csv` — one row per candidate, ranked best-first
- `output/ranked_candidates.json` — same data, structured for programmatic use

Each row includes the final score, every sub-score, matched/missing required
skills, and a plain-English reasoning string.

## Expected capabilities

This Resume Screening Agent is built to meet a professional intermediate
use case:

- Parse resumes in `.pdf`, `.docx`, and `.txt` formats
- Extract structured resume fields: skills, total experience, education level,
  and education field
- Parse a job description and identify required and preferred skills,
  minimum years of experience, and education requirements
- Compute a relevance score using a hybrid model:
  - required/nice-to-have skill matching
  - TF-IDF cosine similarity for overall JD-to-resume topical overlap
  - experience against the JD minimum
  - education level against the JD requirement
- Rank candidates and return an ordered shortlist with reasoning
- Handle 10+ resumes in a single run via CLI or the live web API

## Agent deliverables

This project already supports the expected deliverables for an AI resume
screening agent:

- A sample job description in `data/job_description.txt`
- A sample candidate resume folder in `data/resumes/`
- Ranked output written to `output/ranked_candidates.csv` and
  `output/ranked_candidates.json`
- A scoring method and reasoning output that can be explained clearly

## Scoring method

The final relevance score is a weighted combination of four explainable axes:

```text
final_score = 0.35 × skill_match_score
            + 0.30 × TF-IDF similarity
            + 0.20 × experience_score
            + 0.15 × education_score
```

- `skill_match_score` rewards required skills strongly and preferred skills
  secondarily
- `TF-IDF similarity` captures overall textual alignment between the resume and
  the JD
- `experience_score` gives full credit when the candidate meets or exceeds the
  minimum years required, otherwise scales proportionally
- `education_score` compares candidate education level to the JD's requirement

The agent stores every sub-score so the shortlist is auditable and reproducible.

## Run it as a live web app (recommended for demoing)

```bash
python server.py
```

Then open **http://localhost:5000** in your browser.

This is a real backend with an actual HTTP API — not a component-library
demo. `server.py` is a Flask app exposing:

- `GET /api/health` — reports which NLP/LLM engine is actually active right
  now (TF-IDF similarity is always on; the LLM extraction line only lights
  up green if a key is configured)
- `POST /api/screen` — accepts a JD (pasted text or uploaded file) and a
  batch of resume files, runs the full pipeline, and returns ranked JSON

The page at `/` (`static/index.html`) is a hand-built frontend — no
Streamlit, no component kit — styled as a case-intake desk: each resume
becomes a numbered case file, stamped with a verdict (Strong match / Review
/ Weak match) based on its score, with an expandable dossier showing the
skill breakdown and reasoning. Drag-and-drop or click to upload; clicking
**Open the case** calls `/api/screen` live and renders the ranked board.

This is a genuine live execution of the agent, not a static display of a
past result — every click of "Open the case" re-executes the full pipeline
(`src/parser.py` → `src/extractor.py` → `src/scorer.py` → `src/ranker.py`)
against whatever you just uploaded, right in front of you.

## Run it from the command line

```bash
python main.py --jd data/job_description.txt --resumes data/resumes --output output
```

Useful for batch runs, scripting, or if you'd rather not use a browser.
Produces the same CSV/JSON described above.

### View a past result as a static webpage

```bash
python generate_report.py
```

This turns an already-generated `output/ranked_candidates.json` into
`output/report.html` — a shareable, self-contained snapshot (no server
needed) of one run's results. Useful for sending a result to someone without
asking them to run anything. The live app above is the one that actually
*runs* the agent; this just displays a result you already have.

### Run the tests

```bash
pytest tests/
```

12 unit tests cover the scoring math directly (no API key or network needed) —
this is the part of the system that most needs to be deterministic and correct.

---

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
│   └── llm_client.py            # thin OpenAI wrapper
└── tests/
    └── test_scorer.py            # unit tests for the scoring math
```

---

## Design choices

### Hybrid scoring, not a single black-box number

```
final_score = 0.35 × skill_match_score
            + 0.30 × TF-IDF text_similarity_score
            + 0.20 × experience_score
            + 0.15 × education_score
```

I did **not** just ask the LLM "rate this resume 0–100," for three reasons:

1. **Reproducibility.** An LLM asked to output a single score can give a
   different number on a re-run of the same input. A hiring decision-support
   tool should give the same answer for the same inputs every time.
2. **Auditability.** A recruiter (or a reviewer of this project) needs to see
   *why* candidate A beat candidate B, not just trust a number. Every
   sub-score is stored and shown.
3. **The right tool for each sub-problem.** Skill overlap and years-of-experience
   are precise, countable comparisons — they shouldn't be left to a fuzzy
   similarity metric. TF-IDF cosine similarity, on the other hand, is a real,
   deterministic NLP method that captures overall topical overlap between the
   full resume and the JD (catching relevant context that isn't in the
   explicit skills list). Combining both gives a score that's both
   holistic and explainable.




### Deterministic reasoning, not LLM-generated explanations

The `reasoning` column is built directly from the computed sub-scores (which
skills matched/were missing, whether experience/education met the bar) —
it is **not** a separate "explain this score" LLM call. This guarantees the
explanation always matches the actual math behind the score, with zero risk
of the model hallucinating a justification that doesn't line up with the
number next to it.

### Provider-agnostic LLM client

`llm_client.py` uses the `LLM_PROVIDER` env var to select between OpenAI and Groq. The brief allows "any model, any framework" — this keeps the extraction step configurable while supporting both providers in this repository.

---

## Tradeoffs & what I'd improve with more time

- **TF-IDF vs. embeddings.** TF-IDF cosine similarity was chosen over
  sentence-embedding similarity (e.g. `sentence-transformers`) because it's
  fully offline, has zero model-download dependency, and is deterministic —
  which matters a lot for a 24-hour submission a reviewer needs to run
  quickly and reliably. With more time, I'd add dense embedding similarity
  as a second signal alongside TF-IDF, since it would catch semantically
  related-but-differently-worded skills (e.g. "productionizing models" ≈
  "MLOps") that pure bag-of-words similarity misses.
- **Skill normalization.** Skill matching currently relies on the LLM (or
  fallback keyword list) to normalize skill names consistently. A resume
  that says "Postgres" vs a JD that says "PostgreSQL" is handled by the LLM
  in the primary path, but the heuristic fallback path is stricter about
  exact substring matches. A shared skills taxonomy/alias table would make
  the fallback path more robust too.
- **Experience estimation from dates.** The fallback heuristic estimates
  years of experience by summing date ranges found in the text, which can
  overcount overlapping roles or undercount when a resume doesn't list dates
  in a `YYYY-YYYY` format. The LLM path handles this much better by reading
  the resume holistically.
- **Education parsing is coarse.** It buckets into
  Diploma/Bachelor's/Master's/PhD only, with no weighting for field of study
  relevance (e.g. a Master's in Fine Arts vs Computer Science both score as
  "Master's"). With more time I'd extract and compare field of study too.
- **No dedup/near-duplicate detection.** If the same candidate submits two
  slightly different resume versions, both would be scored and ranked
  independently rather than flagged as duplicates.
- **Batch LLM calls.** Currently each resume triggers its own LLM extraction
  call. For larger batches (100s of resumes), batching multiple resumes into
  fewer calls would reduce cost and latency.

## Sample data

- `data/job_description.txt` — a Backend Engineer (ML Platform) role, chosen
  because it has a clear mix of required skills, nice-to-have skills, a
  numeric experience range, and an education requirement — enough surface
  area to meaningfully exercise every scoring axis.
- `data/resumes/` — 11 sample resumes spanning `.docx`, `.pdf`, and `.txt`
  formats, with deliberately varied skill overlap and experience levels so
  the ranking is meaningful rather than trivial.

