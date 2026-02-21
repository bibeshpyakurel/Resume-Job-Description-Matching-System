from pathlib import Path

from reportlab.pdfgen import canvas

from resume_matcher.pipeline import rank_resumes_in_folder


def _create_pdf(path: Path, text: str) -> None:
    c = canvas.Canvas(str(path))
    c.drawString(72, 720, text)
    c.save()


def test_batch_ranking_integration(tmp_path, monkeypatch):
    monkeypatch.setattr("resume_matcher.preprocessing._get_stopwords", lambda: set())

    resumes_dir = tmp_path / "resumes"
    resumes_dir.mkdir()

    _create_pdf(resumes_dir / "candidate_a.pdf", "python sql machine learning ml")
    _create_pdf(resumes_dir / "candidate_b.pdf", "excel communication")
    _create_pdf(resumes_dir / "candidate_c.pdf", "python sql")

    jd_text = "python sql ml"
    ranked = rank_resumes_in_folder(jd_text=jd_text, folder_path=resumes_dir)

    assert len(ranked) == 3
    assert ranked[0].filename == "candidate_a.pdf"
    assert ranked[0].final_score >= ranked[1].final_score >= ranked[2].final_score
    assert ranked[0].overlap_score == 100.0
    assert ranked[0].explainability.top_overlapping_keywords
    assert "ml" in ranked[0].explainability.top_overlapping_keywords
    assert "machine" in ranked[0].explainability.top_overlapping_keywords
    assert ranked[-1].explainability.missing_keywords
    assert ranked[0].explainability.rationale
