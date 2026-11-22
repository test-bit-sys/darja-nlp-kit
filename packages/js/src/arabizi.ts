import { ArabiziOptions, ArabiziRules } from './types';
import * as path from 'path';
import * as fs from 'fs';

let _rules: ArabiziRules | null = null;

function loadRules(): ArabiziRules {
  if (_rules) {
    return _rules;
  }
  const dataPath = path.join(__dirname, '..', 'data', 'arabizi_rules.json');
  const raw = fs.readFileSync(dataPath, 'utf-8');
  _rules = JSON.parse(raw) as ArabiziRules;
  return _rules;
}

function isFrenchWord(word: string, rules: ArabiziRules): boolean {
  const lower = word.toLowerCase();
  if (rules.french_whitelist.includes(lower)) {
    return true;
  }
  for (const suffix of rules.french_suffixes) {
    if (lower.endsWith(suffix) && lower.length > suffix.length + 2) {
      return true;
    }
  }
  return false;
}

function isStandaloneNumber(token: string): boolean {
  return /^\d+$/.test(token);
}

function hasAdjacentLetter(text: string, index: number): boolean {
  const before = index > 0 ? text[index - 1] : '';
  const after = index < text.length - 1 ? text[index + 1] : '';
  const letterPattern = /[a-zA-Z\u0600-\u06FF]/;
  return letterPattern.test(before) || letterPattern.test(after);
}

function transliterateToken(token: string, rules: ArabiziRules): string {
  if (isStandaloneNumber(token)) {
    return token;
  }

  const lowerToken = token.toLowerCase();

  if (rules.overrides[lowerToken]) {
    return rules.overrides[lowerToken];
  }

  let result = '';
  let i = 0;

  while (i < lowerToken.length) {
    let matched = false;

    if (i + 1 < lowerToken.length) {
      const digraph = lowerToken.substring(i, i + 2);
      if (rules.digraphs[digraph]) {
        result += rules.digraphs[digraph];
        i += 2;
        matched = true;
      }
    }

    if (!matched) {
      const char = lowerToken[i];

      if (/[0-9]/.test(char) && rules.numbers[char]) {
        if (hasAdjacentLetter(lowerToken, i)) {
          result += rules.numbers[char];
        } else {
          result += char;
        }
        i++;
      } else if (rules.singles[char]) {
        result += rules.singles[char];
        i++;
      } else {
        result += char;
        i++;
      }
    }
  }

  return result;
}

export function arabiziToArabic(text: string, options?: ArabiziOptions): string {
  if (!text) {
    return '';
  }

  const rules = loadRules();
  const preserveFrench = options?.preserveFrench ?? true;
  const tokens = text.split(/(\s+)/);
  const result: string[] = [];

  for (const token of tokens) {
    if (/^\s+$/.test(token)) {
      result.push(token);
      continue;
    }

    if (!token) {
      continue;
    }

    if (/^[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]/.test(token)) {
      result.push(token);
      continue;
    }

    if (preserveFrench && isFrenchWord(token, rules)) {
      result.push(token);
      continue;
    }

    result.push(transliterateToken(token, rules));
  }

  return result.join('');
}

export { loadRules, isFrenchWord };
