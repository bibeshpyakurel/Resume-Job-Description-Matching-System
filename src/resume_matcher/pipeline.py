from __future__ import annotations

from pathlib import Path

from .extraction import extract_text_from_pdf
from .models import ExplainabilityReport, MatchResult
from .preprocessing import NormalizationMode, extract_keywords
from .scoring import compute_scores


def _build_rationale(overlap: float, cosine: float, missing_count: int) -> str:
    if overlap >= 75 and cosine >= 70:
        return "Strong alignment: most required skills are present with high keyword similarity."
    if overlap >= 50:
        return (
            "Moderate alignment: core skills are present, but some requirements are missing. "
            f"Missing keywords: {missing_count}."
        )
    return (
        "Low alignment: several required keywords are missing and overall similarity is limited. "
        f"Missing keywords: {missing_count}."
    )


def _build_explainability(
    jd_keywords: set[str],
    resume_keywords: set[str],
    overlap: float,
    cosine: float,
    top_k: int = 10,
) -> ExplainabilityReport:
    overlapping = sorted(jd_keywords & resume_keywords)
    missing = sorted(jd_keywords - resume_keywords)
    rationale = _build_rationale(overlap=overlap, cosine=cosine, missing_count=len(missing))
    return ExplainabilityReport(
        top_overlapping_keywords=overlapping[:top_k],
        missing_keywords=missing,
        rationale=rationale,
    )


def score_resume(
    jd_text: str,
    pdf_path: str | Path,
    normalization: NormalizationMode = "none",
    expand_synonyms: bool = True,
) -> MatchResult:
    """Score a single resume PDF against a JD string."""
    path = Path(pdf_path)
    resume_text, warnings = extract_text_from_pdf(path)

    jd_kw = extract_keywords(
        jd_text,
        normalization=normalization,
        expand_synonyms=expand_synonyms,
    )
    resume_kw = extract_keywords(
        resume_text,
        normalization=normalization,
        expand_synonyms=expand_synonyms,
    )
    overlap, cosine, final = compute_scores(jd_kw, resume_kw)
    matched = sorted(jd_kw & resume_kw)
    explainability = _build_explainability(jd_keywords=jd_kw, resume_keywords=resume_kw, overlap=overlap, cosine=cosine)

    return MatchResult(
        filename=path.name,
        overlap_score=overlap,
        cosine_score=cosine,
        final_score=final,
        jd_keywords=sorted(jd_kw),
        resume_keywords=sorted(resume_kw),
        matched_keywords=matched,
        warnings=warnings,
        explainability=explainability,
    )


def rank_resumes_in_folder(
    jd_text: str,
    folder_path: str | Path,
    top_n: int | None = None,
    normalization: NormalizationMode = "none",
    expand_synonyms: bool = True,
) -> list[MatchResult]:
    """Batch process all PDFs in a folder and return ranked results."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder}")

    pdf_files = sorted(folder.glob("*.pdf"))
    results = [
        score_resume(
            jd_text=jd_text,
            pdf_path=pdf,
            normalization=normalization,
            expand_synonyms=expand_synonyms,
        )
        for pdf in pdf_files
    ]

    ranked = sorted(results, key=lambda item: (-item.final_score, item.filename.lower()))
    if top_n is not None and top_n > 0:
        return ranked[:top_n]
    return ranked
