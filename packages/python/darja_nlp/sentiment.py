"""Sentiment analysis for Algerian Darja text (Hybrid Linguistic Rules + 55K-trained ML Model)."""
from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

from .stopwords import tokenize


_DATA_DIR = Path(__file__).parent / 'data'
_lexicon: Optional[Dict[str, Any]] = None
_sentiment_model: Optional[Dict[str, Any]] = None

NEGATION_FLIP_FACTOR = -0.8
CIRCUMFIX_NEGATION_FACTOR = -0.8

_ARABIC_PREFIXES = ['\u0628\u0627\u0644', '\u0648\u0627\u0644', '\u0641\u0627\u0644', '\u0643\u0627\u0644', '\u0627\u0644', '\u0648', '\u0628', '\u0644', '\u0641', '\u0643']
_ARABIC_SUFFIXES = ['\u064A\u0646', '\u0627\u062A', '\u0629', '\u0647']

_RE_URL = re.compile(r'https?://\S+|@\w+')
_RE_TASH = re.compile(r'[\u064B-\u065F\u0670\u0640]')
_RE_ALEF = re.compile(r'[\u0623\u0625\u0622]')
_RE_ELONG = re.compile(r'(.)\1{2,}')
_RE_ML_TOK = re.compile(r'[a-zA-Z0-9\u0621-\u064A\u0671-\u06D3]+|[\U0001F300-\U0001FAFF\u2600-\u27BF]+')

SentimentLabel = Literal['POSITIVE', 'NEGATIVE', 'NEUTRAL', 'MIXED']
SentimentMode = Literal['hybrid', 'lexicon', 'ml']


@dataclass
class SentimentResult:
    score: float
    label: SentimentLabel
    positive_tokens: List[str] = field(default_factory=list)
    negative_tokens: List[str] = field(default_factory=list)
    negated: bool = False
    method: str = 'lexicon'
    probabilities: Optional[Dict[str, float]] = None


def _load_lexicon() -> Dict[str, Any]:
    global _lexicon
    if _lexicon is not None:
        return _lexicon
    lexicon_path = _DATA_DIR / 'lexicon.json'
    with open(lexicon_path, 'r', encoding='utf-8') as f:
        _lexicon = json.load(f)
    return _lexicon


def _load_sentiment_model() -> Optional[Dict[str, Any]]:
    global _sentiment_model
    if _sentiment_model is not None:
        return _sentiment_model
    model_path = _DATA_DIR / 'sentiment_model.json'
    if model_path.exists():
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                _sentiment_model = json.load(f)
                return _sentiment_model
        except Exception:
            return None
    return None


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


def _check_lexicon_direct(
    word: str,
    lexicon: Dict[str, Any],
    custom_positive: Optional[Dict[str, float]] = None,
    custom_negative: Optional[Dict[str, float]] = None,
) -> Optional[float]:
    lower = word.lower()
    if custom_positive:
        if word in custom_positive:
            return custom_positive[word]
        if lower in custom_positive:
            return custom_positive[lower]
    if custom_negative:
        if word in custom_negative:
            return custom_negative[word]
        if lower in custom_negative:
            return custom_negative[lower]

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


def _lookup_score(
    token: str,
    lexicon: Dict[str, Any],
    custom_positive: Optional[Dict[str, float]] = None,
    custom_negative: Optional[Dict[str, float]] = None,
) -> Optional[float]:
    direct = _check_lexicon_direct(token, lexicon, custom_positive, custom_negative)
    if direct is not None:
        return direct

    stripped_prefix = _strip_arabic_prefix(token)
    if stripped_prefix:
        score = _check_lexicon_direct(stripped_prefix, lexicon, custom_positive, custom_negative)
        if score is not None:
            return score

    stripped_suffix = _strip_arabic_suffix(token)
    if stripped_suffix:
        score = _check_lexicon_direct(stripped_suffix, lexicon, custom_positive, custom_negative)
        if score is not None:
            return score

    if stripped_prefix:
        stripped_both = _strip_arabic_suffix(stripped_prefix)
        if stripped_both:
            score = _check_lexicon_direct(stripped_both, lexicon, custom_positive, custom_negative)
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


def _extract_ml_features(text: str) -> List[str]:
    t = _RE_URL.sub(' ', text.lower())
    t = _RE_TASH.sub('', t)
    t = _RE_ALEF.sub('\u0627', t).replace('\u0629', '\u0647').replace('\u0649', '\u064A')
    t = _RE_ELONG.sub(r'\1\1', t)
    toks = _RE_ML_TOK.findall(t)
    feats = list(toks)
    for i in range(len(toks) - 1):
        feats.append(f'{toks[i]}_{toks[i + 1]}')
    for w in toks:
        if len(w) >= 5 and w.isalpha():
            feats.append(f'p3:{w[:3]}')
            feats.append(f's3:{w[-3:]}')
    return feats


def _predict_ml_sentiment(text: str) -> Optional[Tuple[SentimentLabel, float, Dict[str, float], List[str], List[str]]]:
    model = _load_sentiment_model()
    if not model:
        return None
    priors = model.get('priors')
    weights = model.get('weights')
    if not priors or not weights:
        return None

    feats = _extract_ml_features(text)
    if not feats:
        return None

    scores = [float(priors[0]), float(priors[1]), float(priors[2])]
    matched_pos: List[str] = []
    matched_neg: List[str] = []
    hits = 0

    for f in feats:
        w = weights.get(f)
        if w is not None:
            hits += 1
            scores[0] += w[0]
            scores[1] += w[1]
            scores[2] += w[2]
            if '_' not in f and not f.startswith(('p3:', 's3:')):
                if w[2] - w[0] > 0.4 and f not in matched_pos:
                    matched_pos.append(f)
                elif w[0] - w[2] > 0.4 and f not in matched_neg:
                    matched_neg.append(f)

    if hits == 0:
        return None

    max_s = max(scores)
    exps = [math.exp(max(-50.0, s - max_s)) for s in scores]
    total_e = sum(exps) or 1.0
    probs = [e / total_e for e in exps]
    prob_dict = {
        'NEGATIVE': round(probs[0], 4),
        'NEUTRAL': round(probs[1], 4),
        'POSITIVE': round(probs[2], 4),
    }

    if probs[2] >= probs[0] and probs[2] >= probs[1]:
        pred_label: SentimentLabel = 'POSITIVE'
    elif probs[0] >= probs[2] and probs[0] >= probs[1]:
        pred_label = 'NEGATIVE'
    else:
        pred_label = 'NEUTRAL'

    polarity = round(max(-1.0, min(1.0, probs[2] - probs[0])), 2)
    return pred_label, polarity, prob_dict, matched_pos[:6], matched_neg[:6]


def _scan_phrase_matches(
    tokens: List[str],
    lexicon: Dict[str, Any],
    custom_positive: Optional[Dict[str, float]] = None,
    custom_negative: Optional[Dict[str, float]] = None,
) -> Tuple[List[Tuple[int, int, str, float]], set[int]]:
    """Match multi-word lexicon phrases across token slices without double counting."""
    phrase_map: Dict[str, float] = {}
    for src in (lexicon['positive'], lexicon['negative']):
        for k, v in src.items():
            if ' ' in k:
                phrase_map[k.lower()] = float(v)
    if custom_positive:
        for k, v in custom_positive.items():
            if ' ' in k:
                phrase_map[k.lower()] = float(v)
    if custom_negative:
        for k, v in custom_negative.items():
            if ' ' in k:
                phrase_map[k.lower()] = float(v)

    if not phrase_map or len(tokens) < 2:
        return [], set()

    lower_tokens = [t.lower() for t in tokens]
    matches: List[Tuple[int, int, str, float]] = []
    covered: set[int] = set()

    n = len(lower_tokens)
    for window in (4, 3, 2):
        for i in range(0, n - window + 1):
            if any(idx in covered for idx in range(i, i + window)):
                continue
            cand = ' '.join(lower_tokens[i:i + window])
            if cand in phrase_map:
                matches.append((i, i + window, ' '.join(tokens[i:i + window]), phrase_map[cand]))
                covered.update(range(i, i + window))

    return matches, covered


def analyze_sentiment(
    text: str,
    mode: SentimentMode = 'hybrid',
    custom_positive: Optional[Dict[str, float]] = None,
    custom_negative: Optional[Dict[str, float]] = None,
) -> SentimentResult:
    """Analyze sentiment of Algerian Darja text.

    Supports three modes:
    - 'hybrid' (default): linguistic lexicon + circumfix negation + 55K-trained ML fallback
    - 'lexicon': pure deterministic rule/lexicon engine
    - 'ml': trained zero-dependency statistical classifier (55K+ real Algerian texts)
    """
    if not text:
        return SentimentResult(score=0.0, label='NEUTRAL', method=mode)

    if mode == 'ml':
        ml_res = _predict_ml_sentiment(text)
        if ml_res:
            ml_label, ml_score, probs, m_pos, m_neg = ml_res
            return SentimentResult(
                score=ml_score,
                label=ml_label,
                positive_tokens=m_pos,
                negative_tokens=m_neg,
                negated=False,
                method='ml',
                probabilities=probs,
            )
        return SentimentResult(score=0.0, label='NEUTRAL', method='ml')

    lexicon = _load_lexicon()
    result = tokenize(text)
    tokens = result.tokens
    negations = result.negations

    positive_tokens: List[str] = []
    negative_tokens: List[str] = []
    total_score = 0.0
    scored_count = 0
    has_negation = False

    # 1. Multi-word lexicon phrase matches first
    phrase_matches, covered_indices = _scan_phrase_matches(tokens, lexicon, custom_positive, custom_negative)
    for start_i, end_i, phrase_str, p_score in phrase_matches:
        prev_token = tokens[start_i - 1] if start_i > 0 else None
        if prev_token is not None and _is_negator(prev_token, lexicon):
            p_score *= NEGATION_FLIP_FACTOR
            has_negation = True
        next_token = tokens[end_i] if end_i < len(tokens) else None
        if next_token is not None:
            mult = _get_intensifier_multiplier(next_token, lexicon)
            if mult is not None:
                p_score *= mult
        total_score += p_score
        scored_count += 1
        if p_score > 0:
            positive_tokens.append(phrase_str)
        elif p_score < 0:
            negative_tokens.append(phrase_str)

    # 2. Unigram + circumfix negation + intensifiers
    circumfix_originals = {n.original for n in negations if n.negated}

    for i, token in enumerate(tokens):
        if i in covered_indices:
            continue

        if token in circumfix_originals:
            has_negation = True
            neg_info = next((n for n in negations if n.original == token), None)
            if neg_info is not None:
                root_score = _lookup_score(neg_info.root, lexicon, custom_positive, custom_negative)
                if root_score is not None:
                    flipped = root_score * CIRCUMFIX_NEGATION_FACTOR
                    total_score += flipped
                    scored_count += 1
                    if flipped > 0:
                        positive_tokens.append(token)
                    else:
                        negative_tokens.append(token)
                    continue

        score = _lookup_score(token, lexicon, custom_positive, custom_negative)
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

    ml_res = _predict_ml_sentiment(text) if mode == 'hybrid' else None
    ml_probs = ml_res[2] if ml_res else None

    if scored_count == 0 and mode == 'hybrid' and ml_res is not None:
        ml_label, ml_score, probs, m_pos, m_neg = ml_res
        if ml_label != 'NEUTRAL' and abs(ml_score) >= 0.15:
            return SentimentResult(
                score=ml_score,
                label=ml_label,
                positive_tokens=m_pos,
                negative_tokens=m_neg,
                negated=has_negation,
                method='ml',
                probabilities=probs,
            )
        return SentimentResult(
            score=0.0,
            label='NEUTRAL',
            negated=has_negation,
            method='hybrid',
            probabilities=probs,
        )

    final_score = max(-1.0, min(1.0, total_score / scored_count)) if scored_count > 0 else 0.0
    final_score = round(final_score * 100) / 100

    label = _determine_label(final_score, len(positive_tokens), len(negative_tokens))

    return SentimentResult(
        score=final_score,
        label=label,
        positive_tokens=positive_tokens,
        negative_tokens=negative_tokens,
        negated=has_negation,
        method='lexicon' if mode == 'lexicon' else 'hybrid',
        probabilities=ml_probs,
    )
