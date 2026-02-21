# Resume-Job Description Matching System

[![CI](https://img.shields.io/badge/CI-GitHub_Actions-lightgrey)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#)
[![License](https://img.shields.io/badge/License-MIT-green)](#)

A production-ready student NLP project for ranking resumes against job descriptions.

## Elevator Pitch

A lightweight, explainable candidate-screening engine that converts resumes and job descriptions into normalized keyword signals, scores fit with overlap + cosine metrics, and returns ranked candidates with human-readable reasoning.

## Features

- `src/` package layout with typed modules
- PDF text extraction using `pypdf`
- NLTK-based preprocessing and keyword extraction
- Skill synonym expansion (`ml -> machine learning`, `js -> javascript`, etc.)
- Optional stemming/lemmatization toggle (`--normalize stem|lemma`)
- Dual scoring: overlap and cosine
- Final weighted score (`0.5 * overlap + 0.5 * cosine`)
- Explainability report per candidate (top overlaps, missing keywords, rationale)
- CLI for single and batch use-cases
- Pytest test suite and Ruff linting
- GitHub Actions CI

## Demo

![Demo GIF Placeholder](./docs/demo.gif)

> Replace `docs/demo.gif` with a short terminal recording of `single` and `batch --json` flows.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

## CLI Usage

### Single Resume

```bash
resume-matcher single ./data/sample_resumes/candidate_a.pdf --jd "python sql machine learning"
```

### Batch Ranking

```bash
resume-matcher batch ./data/sample_resumes --jd "python sql machine learning" --top 5
```

### Batch JSON Output

```bash
resume-matcher batch ./data/sample_resumes --jd "python sql machine learning" --top 5 --json
```

### Optional quality switches

```bash
resume-matcher batch ./data/sample_resumes --jd "python sql ml" --normalize lemma
resume-matcher batch ./data/sample_resumes --jd "python sql ml" --no-synonyms
```

## Architecture

- `extraction.py`: Robust PDF text extraction with warning-based error handling.
- `preprocessing.py`: Lowercase, punctuation removal, whitespace normalization, tokenization, NLTK stopword filtering, synonym expansion, optional stem/lemma normalization.
- `scoring.py`: `overlap_score`, `cosine_score` (binary vectors), and `final_score`.
- `models.py`: Dataclass result model (`MatchResult`) carrying filename, scores, keywords, warnings, and explainability.
- `pipeline.py`: Single-file scoring and folder-based batch ranking.
- `cli.py`: User-facing `resume-matcher` command.

```text
                    +----------------------+
                    |   Job Description    |
                    +----------+-----------+
                               |
+-----------+       +----------v-----------+       +----------------+
| Resume PDF | ----> |  Extraction Layer   | ----> | Preprocessing  |
+-----------+       |   (pypdf parsing)    |       | + Synonyms/NLP |
                    +----------+-----------+       +--------+-------+
                               |                            |
                               +------------+---------------+
                                            v
                                  +---------+---------+
                                  |   Scoring Engine  |
                                  | overlap / cosine  |
                                  | final weighted    |
                                  +---------+---------+
                                            |
                                            v
                                  +---------+---------+
                                  | Explainability +  |
                                  | Ranked Outputs    |
                                  +-------------------+
```

## Design decisions

- Binary keyword vectors for cosine similarity:
  - Keeps scoring deterministic, fast, and easy to explain.
  - Works well for a baseline student project without heavy model dependencies.
- Weighted final score (`50% overlap + 50% cosine`):
  - Overlap captures strict requirement coverage.
  - Cosine captures broader similarity across keyword sets.
  - Equal weighting keeps behavior intuitive and transparent.

## Privacy & security

Resumes often contain sensitive personal data. Treat input files as confidential:

- Do not commit real resumes or personal data to Git.
- Prefer local/offline processing for candidate documents.
- Redact PII before sharing samples or debug logs.
- Use anonymized fixture PDFs for tests and demos.

## Development

```bash
ruff check .
pytest
```

## Project Structure

```text
.
├── .github/workflows/ci.yml
├── data/
│   ├── sample_job_descriptions/
│   └── sample_resumes/
├── src/resume_matcher/
├── tests/
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```
