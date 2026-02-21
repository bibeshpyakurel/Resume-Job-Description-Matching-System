from __future__ import annotations

import math


def overlap_score(jd_keywords: set[str], resume_keywords: set[str]) -> float:
    """Percent of JD keywords found in resume keywords."""
    if not jd_keywords:
        return 0.0
    overlap_count = len(jd_keywords & resume_keywords)
    return round((overlap_count / len(jd_keywords)) * 100.0, 2)


def cosine_score(jd_keywords: set[str], resume_keywords: set[str]) -> float:
    """Cosine similarity between binary vectors over keyword union."""
    if not jd_keywords or not resume_keywords:
        return 0.0

    intersection = len(jd_keywords & resume_keywords)
    denominator = math.sqrt(len(jd_keywords) * len(resume_keywords))
    if denominator == 0:
        return 0.0

    return round((intersection / denominator) * 100.0, 2)


def final_score(overlap: float, cosine: float) -> float:
    """Weighted final score."""
    return round((0.5 * overlap) + (0.5 * cosine), 2)


def compute_scores(jd_keywords: set[str], resume_keywords: set[str]) -> tuple[float, float, float]:
    """Compute overlap, cosine, and final scores (0-100)."""
    overlap = overlap_score(jd_keywords, resume_keywords)
    cosine = cosine_score(jd_keywords, resume_keywords)
    final = final_score(overlap, cosine)
    return overlap, cosine, final
