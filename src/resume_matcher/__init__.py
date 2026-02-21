"""Resume matcher package."""

from .models import ExplainabilityReport, MatchResult
from .pipeline import rank_resumes_in_folder, score_resume

__all__ = ["ExplainabilityReport", "MatchResult", "score_resume", "rank_resumes_in_folder"]
__version__ = "1.0.0"
