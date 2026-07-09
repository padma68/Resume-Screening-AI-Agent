"""
parser.py
Extracts raw text from resumes in PDF, DOCX, or plain-text format.

Design choice: we keep this dumb on purpose. It only turns a file into text.
All "understanding" (skills, experience, education) happens later in
extractor.py using the LLM. This keeps parsing robust and format-specific
bugs isolated from the actual scoring logic.
"""

from pathlib import Path

from pypdf import PdfReader
from docx import Document


class UnsupportedFileType(Exception):
    pass


def extract_text(file_path: str) -> str:
    """Extract raw text from a resume file. Supports .pdf, .docx, .txt."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix == ".docx":
        return _extract_docx(path)
    elif suffix in (".txt", ".text"):
        return _extract_txt(path)
    else:
        raise UnsupportedFileType(
            f"Unsupported file type '{suffix}' for {path.name}. "
            f"Supported: .pdf, .docx, .txt"
        )


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def _extract_docx(path: Path) -> str:
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs).strip()


def _extract_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def load_resumes(folder: str) -> dict[str, str]:
    """Load all supported resume files in a folder. Returns {filename: raw_text}."""
    folder_path = Path(folder)
    supported = {".pdf", ".docx", ".txt", ".text"}
    resumes = {}
    for file in sorted(folder_path.iterdir()):
        if file.suffix.lower() in supported:
            try:
                resumes[file.name] = extract_text(str(file))
            except Exception as e:
                print(f"  [WARN] Skipping {file.name}: {e}")
    return resumes
