"""
Resume Parser — extracts raw text from PDF, DOCX, DOC, and TXT files.
"""
import os
import re


def parse_resume(file_path: str, ext: str) -> str:
    """Return plain text extracted from a resume file."""
    ext = ext.lower()
    try:
        if ext == "pdf":
            return _parse_pdf(file_path)
        elif ext in ("docx", "doc"):
            return _parse_docx(file_path)
        elif ext == "txt":
            return _parse_txt(file_path)
        else:
            return ""
    except Exception as e:
        print(f"[Parser] Error parsing {file_path}: {e}")
        return ""


def _parse_pdf(path: str) -> str:
    """Try pdfplumber first, fall back to pdfminer."""
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception:
        pass
    # Fallback: pdfminer.six
    try:
        from pdfminer.high_level import extract_text as pm_extract
        text = pm_extract(path)
        if text.strip():
            return text
    except Exception:
        pass
    return text


def _parse_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs]
        # Also extract from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.append(cell.text)
        return "\n".join(paragraphs)
    except Exception as e:
        print(f"[Parser] DOCX error: {e}")
        return ""


def _parse_txt(path: str) -> str:
    encodings = ["utf-8", "utf-16", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    return ""
