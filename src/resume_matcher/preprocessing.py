from __future__ import annotations

import re
from functools import lru_cache
from typing import Literal

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import wordpunct_tokenize

NormalizationMode = Literal["none", "stem", "lemma"]

_NON_WORD_PATTERN = re.compile(r"[^a-zA-Z0-9\s]")
_MULTISPACE_PATTERN = re.compile(r"\s+")

SKILL_SYNONYMS: dict[str, list[str]] = {
    "ml": ["machine", "learning"],
    "ai": ["artificial", "intelligence"],
    "js": ["javascript"],
    "ts": ["typescript"],
    "py": ["python"],
    "db": ["database"],
    "nlp": ["natural", "language", "processing"],
}


@lru_cache(maxsize=1)
def _get_stopwords() -> set[str]:
    """Load NLTK English stopwords, downloading if unavailable."""
    try:
        return set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        return set(stopwords.words("english"))


@lru_cache(maxsize=1)
def _get_stemmer() -> PorterStemmer:
    return PorterStemmer()


@lru_cache(maxsize=1)
def _get_lemmatizer() -> WordNetLemmatizer:
    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        nltk.download("wordnet", quiet=True)
    return WordNetLemmatizer()


def normalize_text(text: str) -> str:
    """Lowercase text, remove punctuation, and normalize whitespace."""
    lowered = text.lower()
    without_punctuation = _NON_WORD_PATTERN.sub(" ", lowered)
    normalized = _MULTISPACE_PATTERN.sub(" ", without_punctuation).strip()
    return normalized


def _expand_skill_synonyms(tokens: list[str]) -> list[str]:
    expanded: list[str] = []
    for token in tokens:
        expanded.append(token)
        expanded.extend(SKILL_SYNONYMS.get(token, []))
    return expanded


def _apply_normalization(tokens: list[str], mode: NormalizationMode) -> list[str]:
    if mode == "none":
        return tokens

    if mode == "stem":
        stemmer = _get_stemmer()
        return [stemmer.stem(token) for token in tokens]

    lemmatizer = _get_lemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]


def preprocess_text(
    text: str,
    normalization: NormalizationMode = "none",
    expand_synonyms: bool = True,
) -> list[str]:
    """Tokenize normalized text and remove stopwords."""
    normalized = normalize_text(text)
    if not normalized:
        return []

    stop_words = _get_stopwords()
    tokens = wordpunct_tokenize(normalized)
    filtered = [token for token in tokens if token and token not in stop_words]

    if expand_synonyms:
        filtered = _expand_skill_synonyms(filtered)

    return _apply_normalization(filtered, normalization)


def extract_keywords(
    text: str,
    normalization: NormalizationMode = "none",
    expand_synonyms: bool = True,
) -> set[str]:
    """Extract keyword set from arbitrary text."""
    return set(
        preprocess_text(
            text=text,
            normalization=normalization,
            expand_synonyms=expand_synonyms,
        )
    )
