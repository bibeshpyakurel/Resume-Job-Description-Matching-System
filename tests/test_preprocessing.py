from resume_matcher.preprocessing import extract_keywords, normalize_text, preprocess_text


def test_normalize_text_removes_punctuation_and_normalizes_space(monkeypatch):
    monkeypatch.setattr("resume_matcher.preprocessing._get_stopwords", lambda: {"and", "the"})
    text = "Python, SQL!!!   and   ML"
    assert normalize_text(text) == "python sql and ml"


def test_preprocess_text_removes_stopwords(monkeypatch):
    monkeypatch.setattr("resume_matcher.preprocessing._get_stopwords", lambda: {"and", "with"})
    tokens = preprocess_text("Python and SQL with analytics")
    assert tokens == ["python", "sql", "analytics"]


def test_extract_keywords_expands_skill_synonyms(monkeypatch):
    monkeypatch.setattr("resume_matcher.preprocessing._get_stopwords", lambda: set())
    keywords = extract_keywords("ml engineer with js")
    assert "ml" in keywords
    assert "machine" in keywords
    assert "learning" in keywords
    assert "javascript" in keywords


def test_stemming_toggle(monkeypatch):
    monkeypatch.setattr("resume_matcher.preprocessing._get_stopwords", lambda: set())
    keywords = extract_keywords("plays played playing", normalization="stem", expand_synonyms=False)
    assert keywords == {"play"}


def test_lemmatization_toggle(monkeypatch):
    class DummyLemmatizer:
        def lemmatize(self, token: str) -> str:
            if token == "geese":
                return "goose"
            return token

    monkeypatch.setattr("resume_matcher.preprocessing._get_stopwords", lambda: set())
    monkeypatch.setattr("resume_matcher.preprocessing._get_lemmatizer", lambda: DummyLemmatizer())
    keywords = extract_keywords("geese", normalization="lemma", expand_synonyms=False)
    assert keywords == {"goose"}
