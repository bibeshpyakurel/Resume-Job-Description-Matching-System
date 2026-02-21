from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ExplainabilityReport:
    """Explainability metadata for one candidate score."""

    top_overlapping_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)
    rationale: str = ""


@dataclass(slots=True)
class MatchResult:
    """Result object for a single resume against one JD."""

    filename: str
    overlap_score: float
    cosine_score: float
    final_score: float
    jd_keywords: list[str] = field(default_factory=list)
    resume_keywords: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    explainability: ExplainabilityReport = field(default_factory=ExplainabilityReport)
