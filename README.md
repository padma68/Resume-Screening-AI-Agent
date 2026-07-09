cat > README.md << 'EOF'
# AI Resume Screening Agent

## Project Overview

The AI Resume Screening Agent is an intelligent recruitment assistant that automates the initial resume screening process by analyzing multiple resumes against a given Job Description (JD). The system extracts candidate information such as skills, work experience, education, certifications, and projects from resumes in PDF, DOCX, and TXT formats.

Using Natural Language Processing (NLP) with TF-IDF vectorization and Cosine Similarity, the agent compares each resume with the Job Description to calculate a relevance score. Based on this analysis, candidates are ranked from highest to lowest suitability, with a detailed explanation of the scoring.

The project was developed to simplify and accelerate the recruitment process by reducing manual resume screening, improving consistency in candidate evaluation, and helping recruiters identify the most suitable applicants efficiently.

## Main Capabilities

- Parse resumes in PDF, DOCX, and TXT formats.
- Extract skills, education, experience, certifications, and projects.
- Analyze Job Descriptions and identify required qualifications.
- Compute resume-to-job relevance using NLP similarity.
- Rank candidates based on weighted scoring.
- Generate explanations for candidate rankings.
- Process 10 or more resumes in a single run.
- Export ranked results in CSV and JSON formats.
- Provide a simple Flask-based web interface for uploading resumes and viewing results.

EOF
