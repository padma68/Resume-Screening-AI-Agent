#!/usr/bin/env python3
"""
Resume Screening Agent
Ranks a folder of resumes against a job description and outputs a scored,
explainable shortlist as CSV and JSON.

Usage:
    python main.py --jd data/job_description.txt --resumes data/resumes --output output/

See README.md for setup and configuration.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.parser import load_resumes, extract_text
from src.ranker import rank_resumes

load_dotenv()  # picks up .env if present; harmless no-op otherwise


def parse_args():
    parser = argparse.ArgumentParser(description="Resume Screening Agent")
    parser.add_argument("--jd", required=True, help="Path to job description (.txt/.pdf/.docx)")
    parser.add_argument("--resumes", required=True, help="Path to folder of resumes")
    parser.add_argument("--output", default="output", help="Output folder for results")
    return parser.parse_args()


def write_csv(results: list[dict], path: Path):
    fieldnames = [
        "rank", "filename", "final_score", "skill_score", "similarity_score",
        "experience_score", "education_score", "years_experience",
        "matched_required_skills", "missing_required_skills", "reasoning",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


def write_json(results: list[dict], path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def main():
    args = parse_args()

    jd_path = Path(args.jd)
    if not jd_path.exists():
        print(f"Job description not found: {jd_path}", file=sys.stderr)
        sys.exit(1)

    resumes_path = Path(args.resumes)
    if not resumes_path.is_dir():
        print(f"Resumes folder not found: {resumes_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Loading job description from {jd_path}...")
    jd_text = extract_text(str(jd_path))

    print(f"Loading resumes from {resumes_path}...")
    resumes = load_resumes(str(resumes_path))
    print(f"Loaded {len(resumes)} resume(s).\n")

    if not resumes:
        print("No supported resume files found (.pdf, .docx, .txt).", file=sys.stderr)
        sys.exit(1)

    results = rank_resumes(resumes, jd_text)

    csv_path = output_path / "ranked_candidates.csv"
    json_path = output_path / "ranked_candidates.json"
    write_csv(results, csv_path)
    write_json(results, json_path)

    print(f"\nDone. Ranked {len(results)} candidates.")
    print(f"CSV:  {csv_path}")
    print(f"JSON: {json_path}\n")

    print("Top 5 candidates:")
    print(f"{'Rank':<5}{'Score':<8}{'Filename'}")
    for r in results[:5]:
        print(f"{r['rank']:<5}{r['final_score']:<8}{r['filename']}")


if __name__ == "__main__":
    main()
