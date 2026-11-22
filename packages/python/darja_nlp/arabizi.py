"""Arabizi-to-Arabic transliterator with French code-switching awareness."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


_DATA_DIR = Path(__file__).parent / 'data'
_rules: Optional[Dict[str, Any]] = None


class ArabiziOptions:
    __slots__ = ('preserve_french',)

    def __init__(self, preserve_french: bool = True) -> None:
        self.preserve_french = preserve_french


def _load_rules() -> Dict[str, Any]:
    global _rules
    if _rules is not None:
        return _rules
    rules_path = _DATA_DIR / 'arabizi_rules.json'
    with open(rules_path, 'r', encoding='utf-8') as f:
        _rules = json.load(f)
    return _rules


def _is_french_word(word: str, rules: Dict[str, Any]) -> bool:
    lower = word.lower()
    whitelist: List[str] = rules['french_whitelist']
    if lower in whitelist:
        return True
    suffixes: List[str] = rules['french_suffixes']
    for suffix in suffixes:
        if lower.endswith(suffix) and len(lower) > len(suffix) + 2:
            return True
    return False


def _is_standalone_number(token: str) -> bool:
    return bool(re.match(r'^\d+$', token))


def _has_adjacent_letter(text: str, index: int) -> bool:
    letter_pattern = re.compile(r'[a-zA-Z\u0600-\u06FF]')
    before = text[index - 1] if index > 0 else ''
    after = text[index + 1] if index < len(text) - 1 else ''
    return bool(letter_pattern.match(before) or letter_pattern.match(after))


def _transliterate_token(token: str, rules: Dict[str, Any]) -> str:
    if _is_standalone_number(token):
        return token

    lower_token = token.lower()
    overrides: Dict[str, str] = rules['overrides']
    if lower_token in overrides:
        return overrides[lower_token]

    digraphs: Dict[str, str] = rules['digraphs']
    singles: Dict[str, str] = rules['singles']
    numbers: Dict[str, str] = rules['numbers']

    result: list[str] = []
    i = 0

    while i < len(lower_token):
        matched = False

        if i + 1 < len(lower_token):
            digraph = lower_token[i:i + 2]
            if digraph in digraphs:
                result.append(digraphs[digraph])
                i += 2
                matched = True

        if not matched:
            char = lower_token[i]

            if char.isdigit() and char in numbers:
                if _has_adjacent_letter(lower_token, i):
                    result.append(numbers[char])
                else:
                    result.append(char)
                i += 1
            elif char in singles:
                result.append(singles[char])
                i += 1
            else:
                result.append(char)
                i += 1

    return ''.join(result)


_SPLIT_PATTERN = re.compile(r'(\s+)')
_ARABIC_START = re.compile(r'^[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]')


def arabizi_to_arabic(text: str, options: Optional[ArabiziOptions] = None) -> str:
    """Convert Arabizi text to Arabic script.

    Handles French loanword detection, irregular overrides,
    digraph mappings, and context-sensitive number conversion.
    """
    if not text:
        return ''

    rules = _load_rules()
    opts = options or ArabiziOptions()
    tokens = _SPLIT_PATTERN.split(text)
    result: list[str] = []

    for token in tokens:
        if re.match(r'^\s+$', token):
            result.append(token)
            continue

        if not token:
            continue

        if _ARABIC_START.match(token):
            result.append(token)
            continue

        if opts.preserve_french and _is_french_word(token, rules):
            result.append(token)
            continue

        result.append(_transliterate_token(token, rules))

    return ''.join(result)
