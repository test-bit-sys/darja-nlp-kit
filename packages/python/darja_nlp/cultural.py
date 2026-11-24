"""
Algerian Cultural Knowledge, Proverbs, Memes, Landmarks, and Slang detection module.
Part of darja-nlp-kit. Zero external dependencies.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA_DIR = Path(__file__).parent / 'data'
_culture_cache: Optional[Dict[str, Any]] = None
_slang_cache: Optional[Dict[str, Any]] = None
_memes_cache: Optional[Dict[str, Any]] = None
_franco_cache: Optional[Dict[str, Any]] = None

_GENERIC_STOP = {'سلعة', 'سوق', 'حي', 'شارع', 'باب', 'واد', 'ساحة', 'جبل', 'جبال', 'طاجين', 'طبق', 'أكلة'}


def _extract_keywords(text: str) -> List[str]:
    clean = text.split(" (")[0].strip()
    parts = re.split(r'[/(),]|\s+و', text)
    res = set([text, clean])
    for p in parts:
        p = p.strip()
        if len(p) > 2 and p not in _GENERIC_STOP:
            res.add(p)
            if p.startswith('ال') and len(p) > 3:
                res.add(p[2:])
            elif not p.startswith('ال'):
                res.add('ال' + p)
            words = p.split()
            if len(words) == 2:
                for w in words:
                    if len(w) > 3 and w not in _GENERIC_STOP:
                        res.add(w)
                        if w.startswith('ال') and len(w) > 4:
                            res.add(w[2:])
                        elif not w.startswith('ال'):
                            res.add('ال' + w)
    return [x for x in res if len(x) > 2 and x not in _GENERIC_STOP]


def get_cultural_data() -> Dict[str, Any]:
    """Load culture.json containing proverbs, memes, landmarks, and gastronomy."""
    global _culture_cache
    if _culture_cache is not None:
        return _culture_cache
    path = _DATA_DIR / 'culture.json'
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                _culture_cache = json.load(f)
                return _culture_cache
        except Exception:
            pass
    _culture_cache = {'proverbs': [], 'memes_and_trends': [], 'landmarks': [], 'gastronomy': []}
    return _culture_cache


def get_slang_data() -> Dict[str, Any]:
    """Load slang.json containing Algerian youth, street, and marketplace slang."""
    global _slang_cache
    if _slang_cache is not None:
        return _slang_cache
    path = _DATA_DIR / 'slang.json'
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                _slang_cache = json.load(f)
                return _slang_cache
        except Exception:
            pass
    _slang_cache = {'expressions': []}
    return _slang_cache


def get_memes_data() -> Dict[str, Any]:
    """Load memes.json containing iconic Algerian memes, viral TV quotes, and pop-culture phrases."""
    global _memes_cache
    if _memes_cache is not None:
        return _memes_cache
    path = _DATA_DIR / 'memes.json'
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                _memes_cache = json.load(f)
                return _memes_cache
        except Exception:
            pass
    _memes_cache = {'memes': []}
    return _memes_cache


def get_franco_darja_data() -> Dict[str, Any]:
    """Load franco_darja.json containing French-Darja loanwords and hybrid verbs."""
    global _franco_cache
    if _franco_cache is not None:
        return _franco_cache
    path = _DATA_DIR / 'franco_darja.json'
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                _franco_cache = json.load(f)
                return _franco_cache
        except Exception:
            pass
    _franco_cache = {'words': []}
    return _franco_cache


@dataclass
class CulturalMatch:
    matched_text: str
    category: str  # 'proverb', 'meme_trend', 'landmark', 'gastronomy', 'slang'
    canonical_name: str
    meaning: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CulturalAnalysisResult:
    has_cultural_reference: bool
    proverbs: List[CulturalMatch] = field(default_factory=list)
    memes_and_trends: List[CulturalMatch] = field(default_factory=list)
    landmarks: List[CulturalMatch] = field(default_factory=list)
    gastronomy: List[CulturalMatch] = field(default_factory=list)
    slang_expressions: List[CulturalMatch] = field(default_factory=list)
    all_matches: List[CulturalMatch] = field(default_factory=list)
    cultural_summary: str = ""


def detect_cultural_references(text: str) -> CulturalAnalysisResult:
    """
    Detect Algerian proverbs, internet memes, historical landmarks,
    traditional gastronomy, and street slang in customer text.
    """
    if not text or not text.strip():
        return CulturalAnalysisResult(
            has_cultural_reference=False,
            proverbs=[],
            memes_and_trends=[],
            landmarks=[],
            gastronomy=[],
            slang_expressions=[],
            all_matches=[],
            cultural_summary="لا توجد إشارات ثقافية أو شعبية خاصة.",
        )

    lower_text = text.lower()
    culture_db = get_cultural_data()
    slang_db = get_slang_data()

    matched_proverbs: List[CulturalMatch] = []
    matched_memes: List[CulturalMatch] = []
    matched_landmarks: List[CulturalMatch] = []
    matched_gastronomy: List[CulturalMatch] = []
    matched_slang: List[CulturalMatch] = []

    # 1. Match Proverbs
    for p in culture_db.get("proverbs", []):
        p_text = p.get("text", "")
        p_arabizi = p.get("arabizi", "")
        if (p_text and p_text in text) or (p_arabizi and p_arabizi.lower() in lower_text):
            matched_proverbs.append(CulturalMatch(
                matched_text=p_text if p_text in text else p_arabizi,
                category="proverb",
                canonical_name=p_text,
                meaning=p.get("meaning", ""),
                metadata={"category": p.get("category"), "region": p.get("region")}
            ))

    # 2. Match Memes & Trends (from culture.json and memes.json)
    for m in culture_db.get("memes_and_trends", []):
        m_phrase = m.get("phrase", "")
        m_arabizi = m.get("arabizi", "")
        if (m_phrase and m_phrase in text) or (m_arabizi and m_arabizi.lower() in lower_text):
            matched_memes.append(CulturalMatch(
                matched_text=m_phrase if m_phrase in text else m_arabizi,
                category="meme_trend",
                canonical_name=m_phrase,
                meaning=m.get("meaning", ""),
                metadata={"tone": m.get("tone"), "context": m.get("context")}
            ))

    memes_db = get_memes_data()
    for m in memes_db.get("memes", []):
        m_phrase = m.get("phrase", "")
        m_arabizi = m.get("arabizi", "")
        if (m_phrase and m_phrase in text) or (m_arabizi and m_arabizi.lower() in lower_text):
            if not any(x.canonical_name == m_phrase for x in matched_memes):
                matched_memes.append(CulturalMatch(
                    matched_text=m_phrase if m_phrase in text else m_arabizi,
                    category="meme_trend",
                    canonical_name=m_phrase,
                    meaning=m.get("meaning", ""),
                    metadata={"origin": m.get("origin"), "category": m.get("category"), "tags": m.get("tags")}
                ))

    # 3. Match Landmarks
    for lmk in culture_db.get("landmarks", []):
        l_name = lmk.get("name", "")
        keywords = _extract_keywords(l_name)
        for kw in keywords:
            if kw and kw in text:
                matched_landmarks.append(CulturalMatch(
                    matched_text=kw,
                    category="landmark",
                    canonical_name=l_name,
                    meaning=lmk.get("description", ""),
                    metadata={"city": lmk.get("city"), "wilaya_code": lmk.get("wilaya_code")}
                ))
                break

    # 4. Match Gastronomy
    for f in culture_db.get("gastronomy", []):
        f_name = f.get("name", "")
        f_arabizi = f.get("arabizi", "")
        keywords = _extract_keywords(f_name)
        matched = False
        for kw in keywords:
            if kw and kw in text:
                matched_gastronomy.append(CulturalMatch(
                    matched_text=kw,
                    category="gastronomy",
                    canonical_name=f_name,
                    meaning=f.get("description", ""),
                    metadata={"origin": f.get("origin"), "category": f.get("category")}
                ))
                matched = True
                break
        if not matched and f_arabizi:
            for part in f_arabizi.split("/"):
                if part.strip() and part.strip().lower() in lower_text:
                    matched_gastronomy.append(CulturalMatch(
                        matched_text=part.strip(),
                        category="gastronomy",
                        canonical_name=f_name,
                        meaning=f.get("description", ""),
                        metadata={"origin": f.get("origin"), "category": f.get("category")}
                    ))
                    break

    # 5. Match Slang Expressions
    for s in slang_db.get("expressions", []):
        s_term = s.get("term", "")
        s_arabizi = s.get("arabizi", "")
        keywords = _extract_keywords(s_term)
        matched = False
        for kw in keywords:
            if kw and kw in text:
                matched_slang.append(CulturalMatch(
                    matched_text=kw,
                    category="slang",
                    canonical_name=s_term,
                    meaning=s.get("meaning", ""),
                    metadata={"type": s.get("type"), "polarity": s.get("polarity")}
                ))
                matched = True
                break
        if not matched and s_arabizi and s_arabizi.lower() in lower_text:
            matched_slang.append(CulturalMatch(
                matched_text=s_arabizi,
                category="slang",
                canonical_name=s_term,
                meaning=s.get("meaning", ""),
                metadata={"type": s.get("type"), "polarity": s.get("polarity")}
            ))

    all_matches = (
        matched_proverbs +
        matched_memes +
        matched_landmarks +
        matched_gastronomy +
        matched_slang
    )

    has_ref = len(all_matches) > 0

    # Build human-readable cultural summary
    summary_parts = []
    if matched_proverbs:
        prv_names = "، ".join([f'"{p.canonical_name}"' for p in matched_proverbs])
        summary_parts.append(f"أمثال شعبية: {prv_names}")
    if matched_memes:
        meme_names = "، ".join([f'"{m.canonical_name}"' for m in matched_memes])
        summary_parts.append(f"ترندات وميمز: {meme_names}")
    if matched_landmarks:
        lmk_names = "، ".join([f'"{l.canonical_name}"' for l in matched_landmarks])
        summary_parts.append(f"معالم وأسواق: {lmk_names}")
    if matched_gastronomy:
        food_names = "، ".join([f'"{f.canonical_name}"' for f in matched_gastronomy])
        summary_parts.append(f"مأكولات جزائرية: {food_names}")
    if matched_slang:
        slang_names = "، ".join([f'"{s.canonical_name}"' for s in matched_slang])
        summary_parts.append(f"مصطلحات شارع: {slang_names}")

    cultural_summary = " | ".join(summary_parts) if summary_parts else "لا توجد إشارات ثقافية خاصة."

    return CulturalAnalysisResult(
        has_cultural_reference=has_ref,
        proverbs=matched_proverbs,
        memes_and_trends=matched_memes,
        landmarks=matched_landmarks,
        gastronomy=matched_gastronomy,
        slang_expressions=matched_slang,
        all_matches=all_matches,
        cultural_summary=cultural_summary,
    )


def detect_memes(text: str) -> List[CulturalMatch]:
    """Extract specifically Algerian memes and viral pop-culture quotes from text."""
    res = detect_cultural_references(text)
    return res.memes_and_trends


def detect_franco_darja(text: str) -> List[Dict[str, Any]]:
    """Detect French-Darja loanwords and hybrid verbs in text."""
    if not text or not text.strip():
        return []

    lower_text = text.lower()
    franco_db = get_franco_darja_data()
    matches = []

    for item in franco_db.get("words", []):
        ar_term = item.get("darja_ar", "")
        arabizi_term = item.get("arabizi", "")
        fr_origin = item.get("fr_origin", "")

        matched_key = None
        if ar_term and ar_term in text:
            matched_key = ar_term
        elif arabizi_term and arabizi_term.lower() in lower_text:
            matched_key = arabizi_term
        elif fr_origin and fr_origin.lower() in lower_text:
            matched_key = fr_origin

        if matched_key:
            matches.append({
                "matched_text": matched_key,
                "darja_ar": ar_term,
                "arabizi": arabizi_term,
                "fr_origin": fr_origin,
                "category": item.get("category"),
                "meaning_ar": item.get("meaning_ar"),
                "example": item.get("example")
            })

    return matches

