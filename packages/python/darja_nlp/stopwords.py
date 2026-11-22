"""Stopword handling and tokenization for Algerian Darja."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


_DATA_DIR = Path(__file__).parent / 'data'
_stopwords_set: Optional[Set[str]] = None

_CIRCUMFIX_ARABIC = re.compile(r'^ما(.+?)ش$')
_CIRCUMFIX_ARABIZI = re.compile(r'^ma(.+?)ch$', re.IGNORECASE)
_TOKEN_SPLIT = re.compile(r'[\s,.!?;:()\[\]{}"\'`\u060C\u061B\u061F\u0640]+')

_ARABIC_PREFIXES = ['\u0628\u0627\u0644', '\u0648\u0627\u0644', '\u0641\u0627\u0644', '\u0643\u0627\u0644', '\u0627\u0644', '\u0648', '\u0628', '\u0644', '\u0641', '\u0643']


def _strip_arabic_prefix(token: str) -> Optional[str]:
    for prefix in _ARABIC_PREFIXES:
        if token.startswith(prefix) and len(token) > len(prefix) + 1:
            return token[len(prefix):]
    return None


@dataclass
class NegationInfo:
    original: str
    root: str
    negated: bool


@dataclass
class TokenizeResult:
    tokens: List[str] = field(default_factory=list)
    negations: List[NegationInfo] = field(default_factory=list)


def _load_stopwords() -> Set[str]:
    global _stopwords_set
    if _stopwords_set is not None:
        return _stopwords_set

    data_path = _DATA_DIR / 'stopwords.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        data: Dict[str, List[str]] = json.load(f)

    _stopwords_set = set()
    for category_words in data.values():
        for word in category_words:
            _stopwords_set.add(word)
            _stopwords_set.add(word.lower())
    return _stopwords_set


def _detect_circumfix_negation(token: str) -> Optional[NegationInfo]:
    match = _CIRCUMFIX_ARABIC.match(token)
    if match and len(match.group(1)) >= 2:
        return NegationInfo(original=token, root=match.group(1), negated=True)

    match = _CIRCUMFIX_ARABIZI.match(token)
    if match and len(match.group(1)) >= 2:
        return NegationInfo(original=token, root=match.group(1), negated=True)

    return None


def tokenize(text: str) -> TokenizeResult:
    """Tokenize mixed Arabic/Latin text and detect circumfix negations."""
    if not text:
        return TokenizeResult()

    raw_tokens = [t for t in _TOKEN_SPLIT.split(text) if t]
    tokens: List[str] = []
    negations: List[NegationInfo] = []

    for token in raw_tokens:
        negation = _detect_circumfix_negation(token)
        if negation is not None:
            negations.append(negation)
        tokens.append(token)

    return TokenizeResult(tokens=tokens, negations=negations)


def remove_stopwords(text: str) -> str:
    """Remove Algerian Darja stopwords from text."""
    stopwords = _load_stopwords()
    result = tokenize(text)

    def _is_stop(token: str) -> bool:
        if token in stopwords or token.lower() in stopwords:
            return True
        stripped = _strip_arabic_prefix(token)
        if stripped and (stripped in stopwords or stripped.lower() in stopwords):
            return True
        return False

    filtered = [token for token in result.tokens if not _is_stop(token)]
    return ' '.join(filtered)


def is_stopword(word: str) -> bool:
    """Check if a word is a stopword."""
    stopwords = _load_stopwords()
    if word in stopwords or word.lower() in stopwords:
        return True
    stripped = _strip_arabic_prefix(word)
    if stripped and (stripped in stopwords or stripped.lower() in stopwords):
        return True
    return False


def get_stopwords() -> List[str]:
    """Return all loaded stopwords as a sorted list."""
    stopwords = _load_stopwords()
    return sorted(stopwords)
