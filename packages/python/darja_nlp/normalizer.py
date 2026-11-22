"""Text normalizer for Algerian Darja."""
from __future__ import annotations

import re
from typing import Optional


_ALEF_VARIANTS = re.compile(r'[\u0622\u0623\u0625]')
_TA_MARBUTA = re.compile(r'\u0629')
_ALEF_MAQSURA = re.compile(r'\u0649')
_TASHKEEL = re.compile(
    r'[\u0610-\u061A\u064B-\u065F\u0670'
    r'\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]'
)
_TATWEEL = re.compile(r'\u0640')
_ARABIC_ELONGATION = re.compile(r'(.)\1{2,}')
_LATIN_ELONGATION = re.compile(r'([a-zA-Z])\1{2,}')
_MULTI_SPACE = re.compile(r'\s+')
_MULTI_PUNCT = re.compile(r'([!?.]){2,}')

_VALID_DOUBLES = frozenset({
    'll', 'ss', 'mm', 'nn', 'dd', 'tt', 'rr', 'ff', 'cc', 'pp', 'bb', 'gg', 'zz',
    'ee', 'oo', 'aa',
})


def _reduce_arabic_elongation(text: str) -> str:
    return _ARABIC_ELONGATION.sub(r'\1', text)


def _reduce_latin_elongation(text: str) -> str:
    def _replacer(match: re.Match[str]) -> str:
        char = match.group(1)
        doubled = char.lower() * 2
        if doubled in _VALID_DOUBLES:
            return char * 2
        return char
    return _LATIN_ELONGATION.sub(_replacer, text)


class NormalizeOptions:
    __slots__ = ('preserve_tashkeel', 'preserve_length')

    def __init__(
        self,
        preserve_tashkeel: bool = False,
        preserve_length: bool = False,
    ) -> None:
        self.preserve_tashkeel = preserve_tashkeel
        self.preserve_length = preserve_length


def normalize(text: str, options: Optional[NormalizeOptions] = None) -> str:
    """Normalize Algerian Darja text.

    Unifies Arabic letter variants, strips diacritics and tatweel,
    reduces character elongation, and normalizes whitespace.
    """
    if not text:
        return ''

    opts = options or NormalizeOptions()
    result = text

    result = _ALEF_VARIANTS.sub('\u0627', result)
    result = _TA_MARBUTA.sub('\u0647', result)
    result = _ALEF_MAQSURA.sub('\u064A', result)

    if not opts.preserve_tashkeel:
        result = _TASHKEEL.sub('', result)

    result = _TATWEEL.sub('', result)

    if not opts.preserve_length:
        result = _reduce_arabic_elongation(result)
        result = _reduce_latin_elongation(result)

    result = _MULTI_SPACE.sub(' ', result)
    result = _MULTI_PUNCT.sub(r'\1', result)
    result = result.strip()

    return result
