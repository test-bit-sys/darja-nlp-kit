import { TokenizeResult, NegationInfo, StopwordsData } from './types';
import * as path from 'path';
import * as fs from 'fs';

let _stopwordsSet: Set<string> | null = null;
let _stopwordsData: StopwordsData | null = null;

function loadStopwords(): Set<string> {
  if (_stopwordsSet) {
    return _stopwordsSet;
  }
  const dataPath = path.join(__dirname, '..', 'data', 'stopwords.json');
  const raw = fs.readFileSync(dataPath, 'utf-8');
  _stopwordsData = JSON.parse(raw) as StopwordsData;

  _stopwordsSet = new Set<string>();
  for (const category of Object.values(_stopwordsData)) {
    for (const word of category) {
      _stopwordsSet.add(word);
      _stopwordsSet.add(word.toLowerCase());
    }
  }
  return _stopwordsSet;
}

const CIRCUMFIX_ARABIC = /^ما(.+?)ش$/;
const CIRCUMFIX_ARABIZI = /^ma(.+?)ch$/i;

const ARABIC_PREFIXES = ['\u0628\u0627\u0644', '\u0648\u0627\u0644', '\u0641\u0627\u0644', '\u0643\u0627\u0644', '\u0627\u0644', '\u0648', '\u0628', '\u0644', '\u0641', '\u0643'];

function stripArabicPrefix(token: string): string | null {
  for (const prefix of ARABIC_PREFIXES) {
    if (token.startsWith(prefix) && token.length > prefix.length + 1) {
      return token.slice(prefix.length);
    }
  }
  return null;
}

function detectCircumfixNegation(token: string): NegationInfo | null {
  let match = token.match(CIRCUMFIX_ARABIC);
  if (match && match[1].length >= 2) {
    return {
      original: token,
      root: match[1],
      negated: true
    };
  }

  match = token.match(CIRCUMFIX_ARABIZI);
  if (match && match[1].length >= 2) {
    return {
      original: token,
      root: match[1],
      negated: true
    };
  }

  return null;
}

export function tokenize(text: string): TokenizeResult {
  if (!text) {
    return { tokens: [], negations: [] };
  }

  const rawTokens = text.split(/[\s,.!?;:()[\]{}"'`\u060C\u061B\u061F\u0640]+/)
    .filter((t: string) => t.length > 0);

  const tokens: string[] = [];
  const negations: NegationInfo[] = [];

  for (const token of rawTokens) {
    const negation = detectCircumfixNegation(token);
    if (negation) {
      negations.push(negation);
    }
    tokens.push(token);
  }

  return { tokens, negations };
}

export function removeStopwords(text: string): string {
  const stopwords = loadStopwords();
  const { tokens } = tokenize(text);

  const filtered = tokens.filter((token: string) => {
    const lower = token.toLowerCase();
    if (stopwords.has(token) || stopwords.has(lower)) {
      return false;
    }
    const stripped = stripArabicPrefix(token);
    if (stripped && (stopwords.has(stripped) || stopwords.has(stripped.toLowerCase()))) {
      return false;
    }
    return true;
  });

  return filtered.join(' ');
}

export function isStopword(word: string): boolean {
  const stopwords = loadStopwords();
  if (stopwords.has(word) || stopwords.has(word.toLowerCase())) {
    return true;
  }
  const stripped = stripArabicPrefix(word);
  if (stripped && (stopwords.has(stripped) || stopwords.has(stripped.toLowerCase()))) {
    return true;
  }
  return false;
}

export function getStopwords(): string[] {
  const stopwords = loadStopwords();
  return Array.from(stopwords);
}

export { detectCircumfixNegation, loadStopwords };
