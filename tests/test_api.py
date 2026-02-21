from pathlib import Path

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from api.main import app


def _create_pdf(path: Path, text: str) -> None:
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 720, text)
    pdf.save()


def test_match_endpoint_returns_ranked_results(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("resume_matcher.preprocessing._get_stopwords", lambda: set())

    pdf_a = tmp_path / "candidate_a.pdf"
    pdf_b = tmp_path / "candidate_b.pdf"
    _create_pdf(pdf_a, "python sql machine learning")
    _create_pdf(pdf_b, "excel communication")

    client = TestClient(app)

    with pdf_a.open("rb") as a_file, pdf_b.open("rb") as b_file:
        response = client.post(
            "/match",
            data={"jd": "python sql machine learning"},
            files=[
                ("files", ("candidate_a.pdf", a_file, "application/pdf")),
                ("files", ("candidate_b.pdf", b_file, "application/pdf")),
            ],
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 2
    assert payload["results"][0]["filename"] == "candidate_a.pdf"
    assert "explainability" in payload["results"][0]
    assert "missing_keywords" in payload["results"][0]["explainability"]


def test_match_endpoint_rejects_non_pdf_files() -> None:
    client = TestClient(app)

    response = client.post(
        "/match",
        data={"jd": "python"},
        files=[("files", ("notes.txt", b"hello", "text/plain"))],
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No valid PDF files were provided"
