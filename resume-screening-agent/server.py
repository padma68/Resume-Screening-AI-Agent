"""
server.py
A real backend API for the Resume Screening Agent, plus a served frontend.

Unlike a script you run once, this exposes an actual HTTP API:

    GET  /api/health   -> engine status (which LLM is configured, if any)
    POST /api/screen   -> upload a JD + resumes, get back a ranked JSON list

The frontend at "/" is a hand-built single page (static/index.html) that
calls this API with fetch() - no framework, no component library, so the
visual design isn't constrained to any UI kit's default look.

Run with:
    python server.py
Then open:
    http://localhost:5000
"""

import os
import tempfile
import traceback
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

from src.extractor import extract_jd_fields
from src.parser import extract_text
from src.ranker import rank_resumes

load_dotenv()  # load .env so server can read OpenAI config

app = Flask(__name__, static_folder="static", static_url_path="")


def save_and_extract(file_storage) -> str:
    """
    Persist an uploaded file to a real temp file, fully close it, THEN read
    it back with extract_text(). Reading a file that's still open for
    writing is unsafe (locked on Windows, possibly unflushed elsewhere) -
    this is the same class of bug that broke the earlier Streamlit version,
    fixed the same way here: write -> flush -> close -> read -> delete.
    """
    suffix = Path(file_storage.filename).suffix
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file_storage.save(tmp)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = tmp.name
        text = extract_text(tmp_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    if not text or not text.strip():
        raise ValueError(
            "No extractable text found (likely a scanned/image-only PDF "
            "with no text layer)."
        )
    return text


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health")
def health():
    """Reports which NLP/LLM engine is actually active, so the UI can show it honestly."""
    provider = os.environ.get("LLM_PROVIDER", "openai").lower()
    key_present = bool(os.environ.get("OPENAI_API_KEY") or os.environ.get("GROQ_API_KEY"))
    return jsonify({
        "status": "ok",
        "similarity_method": "TF-IDF cosine similarity (scikit-learn)",
        "llm_provider": provider if key_present else None,
        "llm_configured": key_present,
        "extraction_mode": (
            f"LLM-assisted extraction ({provider})" if key_present
            else "Heuristic NLP fallback (no API key configured)"
        ),
    })


@app.route("/api/screen", methods=["POST"])
def screen():
    try:
        jd_text = (request.form.get("jd_text") or "").strip()
        jd_file = request.files.get("jd_file")
        if jd_file and jd_file.filename:
            jd_text = save_and_extract(jd_file)

        if not jd_text:
            return jsonify({"error": "No job description provided. Paste text or upload a JD file."}), 400

        resume_files = [f for f in request.files.getlist("resumes") if f.filename]
        if not resume_files:
            return jsonify({"error": "No resumes uploaded. Add at least one resume file."}), 400

        resumes, failed = {}, []
        for f in resume_files:
            try:
                resumes[f.filename] = save_and_extract(f)
            except Exception as e:
                failed.append({"filename": f.filename, "error": str(e)})

        if not resumes:
            return jsonify({"error": "None of the uploaded resumes could be read.", "failed": failed}), 400

        jd_fields = extract_jd_fields(jd_text)
        results = rank_resumes(resumes, jd_text, verbose=False)
        return jsonify({
            "results": results,
            "failed": failed,
            "count": len(results),
            "jd_fields": jd_fields,
            "jd_extraction_mode": jd_fields.get("_extraction_mode", "Unknown"),
            "jd_extraction_error": jd_fields.get("_extraction_error", ""),
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Internal error: {e}"}), 500


if __name__ == "__main__":
    print("Resume Screening Agent API")
    print("  UI:      http://localhost:5000")
    print("  Health:  http://localhost:5000/api/health")
    app.run(debug=True, port=5000)
