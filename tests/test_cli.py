from resume_matcher.cli import main
from resume_matcher.models import ExplainabilityReport, MatchResult


def _sample_result(filename: str = "candidate.pdf") -> MatchResult:
    return MatchResult(
        filename=filename,
        overlap_score=80.0,
        cosine_score=70.0,
        final_score=75.0,
        jd_keywords=["python", "sql"],
        resume_keywords=["python", "sql", "aws"],
        matched_keywords=["python", "sql"],
        warnings=[],
        explainability=ExplainabilityReport(
            top_overlapping_keywords=["python", "sql"],
            missing_keywords=[],
            rationale="Strong alignment.",
        ),
    )


def test_cli_single_output(monkeypatch, capsys):
    monkeypatch.setattr("resume_matcher.cli.score_resume", lambda **kwargs: _sample_result())
    monkeypatch.setattr(
        "sys.argv",
        ["resume-matcher", "single", "resume.pdf", "--jd", "python sql"],
    )

    code = main()
    out = capsys.readouterr().out

    assert code == 0
    assert "Filename" in out
    assert "Matched keywords" in out
    assert "Rationale" in out


def test_cli_batch_json_output(monkeypatch, capsys):
    monkeypatch.setattr(
        "resume_matcher.cli.rank_resumes_in_folder",
        lambda **kwargs: [_sample_result("a.pdf"), _sample_result("b.pdf")],
    )
    monkeypatch.setattr(
        "sys.argv",
        ["resume-matcher", "batch", "./resumes", "--jd", "python sql", "--json"],
    )

    code = main()
    out = capsys.readouterr().out

    assert code == 0
    assert '"filename": "a.pdf"' in out
    assert '"explainability"' in out
