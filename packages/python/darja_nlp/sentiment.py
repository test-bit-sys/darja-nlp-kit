"""Sentiment analysis for Algerian Darja text."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from .stopwords import tokenize


_DATA_DIR = Path(__file__).parent / 'data'
_lexicon: Optional[Dict[str, Any]] = None

NEGATION_FLIP_FACTOR = -0.8
CIRCUMFIX_NEGATION_FACTOR = -0.8

_ARABIC_PREFIXES = ['\u0628\u0627\u0644', '\u0648\u0627\u0644', '\u0641\u0627\u0644', '\u0643\u0627\u0644', '\u0627\u0644', '\u0648', '\u0628', '\u0644', '\u0641', '\u0643']
_ARABIC_SUFFIXES = ['\u064A\u0646', '\u0627\u062A', '\u0629', '\u0647']


def _strip_arabic_prefix(token: str) -> Optional[str]:
    for prefix in _ARABIC_PREFIXES:
        if token.startswith(prefix) and len(token) > len(prefix) + 1:
            return token[len(prefix):]
    return None


def _strip_arabic_suffix(token: str) -> Optional[str]:
    for suffix in _ARABIC_SUFFIXES:
        if token.endswith(suffix) and len(token) > len(suffix) + 1:
            return token[:-len(suffix)]
    return None


def _check_lexicon_direct(word: str, lexicon: Dict[str, Any]) -> Optional[float]:
    lower = word.lower()
    positive: Dict[str, float] = lexicon['positive']
    negative: Dict[str, float] = lexicon['negative']

    if word in positive:
        return positive[word]
    if lower in positive:
        return positive[lower]
    if word in negative:
        return negative[word]
    if lower in negative:
        return negative[lower]
    return None


SentimentLabel = Literal['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED']


@dataclass
class SentimentResult:
    score: float
    label: SentimentLabel
    positive_tokens: List[str] = field(default_factory=list)
    negative_tokens: List[str] = field(default_factory=list)
    negated: bool = False


def _load_lexicon() -> Dict[str, Any]:
    global _lexicon
    if _lexicon is not None:
        return _lexicon
    lexicon_path = _DATA_DIR / 'lexicon.json'
    with open(lexicon_path, 'r', encoding='utf-8') as f:
        _lexicon = json.load(f)
    return _lexicon


def _lookup_score(token: str, lexicon: Dict[str, Any]) -> Optional[float]:
    direct = _check_lexicon_direct(token, lexicon)
    if direct is not None:
        return direct

    stripped_prefix = _strip_arabic_prefix(token)
    if stripped_prefix:
        score = _check_lexicon_direct(stripped_prefix, lexicon)
        if score is not None:
            return score

    stripped_suffix = _strip_arabic_suffix(token)
    if stripped_suffix:
        score = _check_lexicon_direct(stripped_suffix, lexicon)
        if score is not None:
            return score

    if stripped_prefix:
        stripped_both = _strip_arabic_suffix(stripped_prefix)
        if stripped_both:
            score = _check_lexicon_direct(stripped_both, lexicon)
            if score is not None:
                return score

    return None


def _get_intensifier_multiplier(token: str, lexicon: Dict[str, Any]) -> Optional[float]:
    lower = token.lower()
    intensifiers: Dict[str, float] = lexicon['intensifiers']
    if token in intensifiers:
        return intensifiers[token]
    if lower in intensifiers:
        return intensifiers[lower]
    return None


def _is_negator(token: str, lexicon: Dict[str, Any]) -> bool:
    lower = token.lower()
    negators: List[str] = lexicon['negators']
    return token in negators or lower in negators


def _determine_label(
    score: float,
    positive_count: int,
    negative_count: int,
) -> SentimentLabel:
    if positive_count > 0 and negative_count > 0:
        return 'MIXED'
    if score > 0.05:
        return 'POSITIVE'
    if score < -0.05:
        return 'NEGATIVE'
    return 'NEUTRAL'


def analyze_sentiment(text: str) -> SentimentResult:
    """Analyze sentiment of Algerian Darja text.

    Handles negation inversion, circumfix negation, and intensifier scaling.
    Returns a SentimentResult with score, label, and token breakdown.
    """
    if not text:
        return SentimentResult(score=0.0, label='NEUTRAL')

    lexicon = _load_lexicon()
    result = tokenize(text)
    tokens = result.tokens
    negations = result.negations

    positive_tokens: List[str] = []
    negative_tokens: List[str] = []
    total_score = 0.0
    scored_count = 0
    has_negation = False

    circumfix_originals = {n.original for n in negations if n.negated}

    for i, token in enumerate(tokens):
        if token in circumfix_originals:
            has_negation = True
            neg_info = next((n for n in negations if n.original == token), None)
            if neg_info is not None:
                root_score = _lookup_score(neg_info.root, lexicon)
                if root_score is not None:
                    flipped = root_score * CIRCUMFIX_NEGATION_FACTOR
                    total_score += flipped
                    scored_count += 1
                    if flipped > 0:
                        positive_tokens.append(token)
                    else:
                        negative_tokens.append(token)
                    continue

        score = _lookup_score(token, lexicon)
        if score is None:
            continue

        prev_token = tokens[i - 1] if i > 0 else None
        if prev_token is not None and _is_negator(prev_token, lexicon):
            score = score * NEGATION_FLIP_FACTOR
            has_negation = True

        next_token = tokens[i + 1] if i + 1 < len(tokens) else None
        if next_token is not None:
            intensifier = _get_intensifier_multiplier(next_token, lexicon)
            if intensifier is not None:
                score = score * intensifier

        if prev_token is not None:
            intensifier = _get_intensifier_multiplier(prev_token, lexicon)
            if intensifier is not None and not _is_negator(prev_token, lexicon):
                score = score * intensifier

        total_score += score
        scored_count += 1

        if score > 0:
            positive_tokens.append(token)
        elif score < 0:
            negative_tokens.append(token)

    final_score = max(-1.0, min(1.0, total_score / scored_count)) if scored_count > 0 else 0.0
    final_score = round(final_score * 100) / 100

    label = _determine_label(final_score, len(positive_tokens), len(negative_tokens))

    return SentimentResult(
        score=final_score,
        label=label,
        positive_tokens=positive_tokens,
        negative_tokens=negative_tokens,
        negated=has_negation,
    )
