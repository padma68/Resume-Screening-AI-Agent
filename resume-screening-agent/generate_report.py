#!/usr/bin/env python3
"""
generate_report.py
Turns output/ranked_candidates.json into a single, self-contained HTML page
you can open directly in a browser - no server, no internet connection
needed (all data is embedded in the file itself).

Usage:
    python generate_report.py --input output/ranked_candidates.json --output output/report.html
"""

import argparse
import json
from pathlib import Path

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Resume Screening Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #F5F6F8;
    --panel: #FFFFFF;
    --ink: #1B2333;
    --ink-soft: #5B6474;
    --line: #E3E6EB;
    --accent: #0E7C7B;
    --accent-soft: #E4F3F1;
    --warn: #C7623E;
    --warn-soft: #FBEAE3;
    --track: #EDEFF2;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: 'IBM Plex Sans', system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  header {
    padding: 48px 40px 28px;
    border-bottom: 1px solid var(--line);
    background: var(--panel);
  }
  .eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 10px;
  }
  h1 {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 34px;
    margin: 0 0 6px;
    letter-spacing: -0.01em;
  }
  .meta {
    color: var(--ink-soft);
    font-size: 14.5px;
    display: flex;
    gap: 22px;
    margin-top: 14px;
    flex-wrap: wrap;
  }
  .meta strong { color: var(--ink); font-family: 'IBM Plex Mono', monospace; }

  .controls {
    max-width: 1180px;
    margin: 24px auto 0;
    padding: 0 40px;
    display: flex;
    gap: 12px;
    align-items: center;
  }
  #search {
    flex: 1;
    padding: 11px 14px;
    border: 1px solid var(--line);
    border-radius: 8px;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 14px;
    background: var(--panel);
    color: var(--ink);
  }
  #search:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
  .count { font-size: 13px; color: var(--ink-soft); white-space: nowrap; }

  main { max-width: 1180px; margin: 20px auto 60px; padding: 0 40px; }

  .card {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 12px;
    margin-bottom: 14px;
    overflow: hidden;
    transition: box-shadow 0.15s ease;
  }
  .card:hover { box-shadow: 0 4px 18px rgba(27,35,51,0.06); }

  .row {
    display: grid;
    grid-template-columns: 44px 1fr 130px 220px;
    align-items: center;
    gap: 18px;
    padding: 18px 20px;
    cursor: pointer;
  }
  .rank {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 15px;
    color: var(--ink-soft);
  }
  .row.top-3 .rank { color: var(--accent); }

  .cand-name { font-weight: 600; font-size: 15.5px; }
  .cand-file {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: var(--ink-soft);
    margin-top: 2px;
  }

  .score-block { text-align: right; }
  .score-num {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 22px;
  }
  .score-label { font-size: 11px; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.06em; }

  .stack-bar {
    height: 8px;
    border-radius: 4px;
    background: var(--track);
    overflow: hidden;
    display: flex;
  }
  .stack-bar > span { height: 100%; }
  .seg-skill { background: var(--accent); }
  .seg-sim   { background: #63B3AE; }
  .seg-exp   { background: #A9CFC9; }
  .seg-edu   { background: #D6E8E4; }

  .details {
    display: none;
    padding: 0 20px 20px;
    border-top: 1px solid var(--line);
  }
  .details.open { display: block; }

  .sub-scores {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 16px 0;
  }
  .sub-score {
    background: var(--bg);
    border-radius: 8px;
    padding: 10px 12px;
  }
  .sub-score .num { font-family: 'IBM Plex Mono', monospace; font-weight: 600; font-size: 17px; }
  .sub-score .label { font-size: 11.5px; color: var(--ink-soft); margin-top: 2px; }

  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
  .chip {
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 100px;
    font-family: 'IBM Plex Mono', monospace;
  }
  .chip.matched { background: var(--accent-soft); color: var(--accent); }
  .chip.missing { background: var(--warn-soft); color: var(--warn); }

  .section-label {
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--ink-soft);
    margin: 14px 0 4px;
  }
  .reasoning {
    font-size: 14px;
    line-height: 1.55;
    color: var(--ink);
    background: var(--bg);
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 6px;
  }
  .chevron { transition: transform 0.15s ease; color: var(--ink-soft); }
  .row.expanded .chevron { transform: rotate(90deg); }

  footer {
    max-width: 1180px;
    margin: 0 auto 60px;
    padding: 0 40px;
    font-size: 12.5px;
    color: var(--ink-soft);
  }
  @media (max-width: 720px) {
    .row { grid-template-columns: 32px 1fr 90px; }
    .stack-bar { display: none; }
    .sub-scores { grid-template-columns: repeat(2, 1fr); }
  }
</style>
</head>
<body>

<header>
  <div class="eyebrow">Resume Screening Agent &middot; Ranked Shortlist</div>
  <h1>__JD_TITLE__</h1>
  <div class="meta">
    <span><strong>__CANDIDATE_COUNT__</strong> candidates screened</span>
    <span>Scoring: <strong>35%</strong> skills &middot; <strong>30%</strong> similarity &middot; <strong>20%</strong> experience &middot; <strong>15%</strong> education</span>
  </div>
</header>

<div class="controls">
  <input id="search" type="text" placeholder="Search by filename or skill...">
  <span class="count" id="count"></span>
</div>

<main id="results"></main>

<footer>Generated locally from ranked_candidates.json &middot; scores are computed deterministically (TF-IDF similarity + skill overlap + experience/education comparison), not by an LLM.</footer>

<script>
const DATA = __DATA_JSON__;

const results = document.getElementById('results');
const searchInput = document.getElementById('search');
const countEl = document.getElementById('count');

function chip(text, kind) {
  return text ? `<span class="chip ${kind}">${text}</span>` : '';
}

function renderRow(r, idx) {
  const matched = (r.matched_required_skills || '').split(',').map(s => s.trim()).filter(Boolean);
  const missing = (r.missing_required_skills || '').split(',').map(s => s.trim()).filter(Boolean);
  const topClass = idx < 3 ? 'top-3' : '';

  return `
  <div class="card">
    <div class="row ${topClass}" onclick="toggle(${idx})" id="row-${idx}">
      <div class="rank">#${r.rank}</div>
      <div>
        <div class="cand-name">${r.filename}</div>
        <div class="cand-file">${r.years_experience} yrs experience</div>
        <div class="stack-bar" style="margin-top:8px; max-width:260px;">
          <span class="seg-skill" style="width:${r.skill_score * 0.35}%"></span>
          <span class="seg-sim" style="width:${r.similarity_score * 0.30}%"></span>
          <span class="seg-exp" style="width:${r.experience_score * 0.20}%"></span>
          <span class="seg-edu" style="width:${r.education_score * 0.15}%"></span>
        </div>
      </div>
      <div class="score-block">
        <div class="score-num">${r.final_score}</div>
        <div class="score-label">final score</div>
      </div>
      <div style="text-align:right; color: var(--ink-soft); font-size: 13px;">
        Details <span class="chevron">&#8250;</span>
      </div>
    </div>
    <div class="details" id="details-${idx}">
      <div class="sub-scores">
        <div class="sub-score"><div class="num">${r.skill_score}</div><div class="label">Skill match</div></div>
        <div class="sub-score"><div class="num">${r.similarity_score}</div><div class="label">Text similarity</div></div>
        <div class="sub-score"><div class="num">${r.experience_score}</div><div class="label">Experience</div></div>
        <div class="sub-score"><div class="num">${r.education_score}</div><div class="label">Education</div></div>
      </div>
      <div class="section-label">Matched required skills</div>
      <div class="chips">${matched.length ? matched.map(s => chip(s, 'matched')).join('') : '<span class="chip missing">none</span>'}</div>
      <div class="section-label">Missing required skills</div>
      <div class="chips">${missing.length ? missing.map(s => chip(s, 'missing')).join('') : '<span class="chip matched">none - meets all required skills</span>'}</div>
      <div class="section-label">Reasoning</div>
      <div class="reasoning">${r.reasoning}</div>
    </div>
  </div>`;
}

function toggle(idx) {
  document.getElementById(`details-${idx}`).classList.toggle('open');
  document.getElementById(`row-${idx}`).classList.toggle('expanded');
}

function render(filterText) {
  const filtered = DATA.filter(r => {
    if (!filterText) return true;
    const hay = (r.filename + ' ' + r.matched_required_skills + ' ' + r.missing_required_skills).toLowerCase();
    return hay.includes(filterText.toLowerCase());
  });
  results.innerHTML = filtered.map((r, i) => renderRow(r, DATA.indexOf(r))).join('');
  countEl.textContent = `Showing ${filtered.length} of ${DATA.length}`;
}

searchInput.addEventListener('input', (e) => render(e.target.value));
render('');
</script>

</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate an HTML report from ranked_candidates.json")
    parser.add_argument("--input", default="output/ranked_candidates.json", help="Path to ranked_candidates.json")
    parser.add_argument("--output", default="output/report.html", help="Path to write the HTML report")
    parser.add_argument("--jd-title", default="Backend Engineer - Machine Learning Platform",
                         help="Job title shown in the report header")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Could not find {input_path}. Run main.py first to generate ranked_candidates.json.")

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    html = TEMPLATE.replace("__DATA_JSON__", json.dumps(data))
    html = html.replace("__CANDIDATE_COUNT__", str(len(data)))
    html = html.replace("__JD_TITLE__", args.jd_title)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Report written to {output_path}")
    print(f"Open it in your browser: file://{output_path.resolve()}")


if __name__ == "__main__":
    main()
