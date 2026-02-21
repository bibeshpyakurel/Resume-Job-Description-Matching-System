from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str | Path) -> tuple[str, list[str]]:
    """Extract text from a PDF file.

    Returns:
        tuple[str, list[str]]: Extracted text and warning messages.

    This function handles unreadable PDFs gracefully by returning empty text
    plus warning messages instead of raising runtime errors.
    """
    path = Path(pdf_path)
    warnings: list[str] = []

    if not path.exists():
        warnings.append(f"File not found: {path}")
        return "", warnings

    if path.suffix.lower() != ".pdf":
        warnings.append(f"Unsupported file type (expected .pdf): {path}")
        return "", warnings

    try:
        reader = PdfReader(str(path))
    except Exception as exc:
        warnings.append(f"Failed to open PDF '{path.name}': {exc}")
        return "", warnings

    pages_text: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        try:
            pages_text.append(page.extract_text() or "")
        except Exception as exc:
            warnings.append(f"Failed to extract page {index} in '{path.name}': {exc}")

    text = "\n".join(chunk for chunk in pages_text if chunk).strip()
    if not text:
        warnings.append(f"No extractable text found in '{path.name}'")

    return text, warnings
