import { SentimentResult, SentimentLabel, LexiconData } from './types';
import { tokenize } from './stopwords';
import * as path from 'path';
import * as fs from 'fs';

let _lexicon: LexiconData | null = null;

function loadLexicon(): LexiconData {
  if (_lexicon) {
    return _lexicon;
  }
  const dataPath = path.join(__dirname, '..', 'data', 'lexicon.json');
  const raw = fs.readFileSync(dataPath, 'utf-8');
  _lexicon = JSON.parse(raw) as LexiconData;
  return _lexicon;
}

const NEGATION_FLIP_FACTOR = -0.8;
const CIRCUMFIX_NEGATION_FACTOR = -0.8;

const ARABIC_PREFIXES = ['\u0628\u0627\u0644', '\u0648\u0627\u0644', '\u0641\u0627\u0644', '\u0643\u0627\u0644', '\u0627\u0644', '\u0648', '\u0628', '\u0644', '\u0641', '\u0643'];
const ARABIC_SUFFIXES = ['\u064A\u0646', '\u0627\u062A', '\u0629', '\u0647'];

function stripArabicPrefix(token: string): string | null {
  for (const prefix of ARABIC_PREFIXES) {
    if (token.startsWith(prefix) && token.length > prefix.length + 1) {
      return token.slice(prefix.length);
    }
  }
  return null;
}

function stripArabicSuffix(token: string): string | null {
  for (const suffix of ARABIC_SUFFIXES) {
    if (token.endsWith(suffix) && token.length > suffix.length + 1) {
      return token.slice(0, -suffix.length);
    }
  }
  return null;
}

function checkLexiconDirect(word: string, lexicon: LexiconData): number | null {
  const lower = word.toLowerCase();
  if (lexicon.positive[word] !== undefined) return lexicon.positive[word];
  if (lexicon.positive[lower] !== undefined) return lexicon.positive[lower];
  if (lexicon.negative[word] !== undefined) return lexicon.negative[word];
  if (lexicon.negative[lower] !== undefined) return lexicon.negative[lower];
  return null;
}

function lookupScore(token: string, lexicon: LexiconData): number | null {
  const direct = checkLexiconDirect(token, lexicon);
  if (direct !== null) return direct;

  const strippedPrefix = stripArabicPrefix(token);
  if (strippedPrefix) {
    const score = checkLexiconDirect(strippedPrefix, lexicon);
    if (score !== null) return score;
  }

  const strippedSuffix = stripArabicSuffix(token);
  if (strippedSuffix) {
    const score = checkLexiconDirect(strippedSuffix, lexicon);
    if (score !== null) return score;
  }

  if (strippedPrefix) {
    const strippedBoth = stripArabicSuffix(strippedPrefix);
    if (strippedBoth) {
      const score = checkLexiconDirect(strippedBoth, lexicon);
      if (score !== null) return score;
    }
  }

  return null;
}

function getIntensifierMultiplier(token: string, lexicon: LexiconData): number | null {
  const lower = token.toLowerCase();
  if (lexicon.intensifiers[token] !== undefined) {
    return lexicon.intensifiers[token];
  }
  if (lexicon.intensifiers[lower] !== undefined) {
    return lexicon.intensifiers[lower];
  }
  return null;
}

function isNegator(token: string, lexicon: LexiconData): boolean {
  const lower = token.toLowerCase();
  return lexicon.negators.includes(token) || lexicon.negators.includes(lower);
}

function determineLabel(score: number, positiveCount: number, negativeCount: number): SentimentLabel {
  if (positiveCount > 0 && negativeCount > 0) {
    return 'MIXED';
  }
  if (score > 0.05) {
    return 'POSITIVE';
  }
  if (score < -0.05) {
    return 'NEGATIVE';
  }
  return 'NEUTRAL';
}

export function analyzeSentiment(text: string): SentimentResult {
  if (!text) {
    return {
      score: 0,
      label: 'NEUTRAL',
      positiveTokens: [],
      negativeTokens: [],
      negated: false
    };
  }

  const lexicon = loadLexicon();
  const { tokens, negations } = tokenize(text);

  const positiveTokens: string[] = [];
  const negativeTokens: string[] = [];
  let totalScore = 0;
  let scoredCount = 0;
  let hasNegation = false;

  const circumfixNegatedOriginals = new Set(
    negations.filter((n) => n.negated).map((n) => n.original)
  );

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];

    if (circumfixNegatedOriginals.has(token)) {
      hasNegation = true;
      const negInfo = negations.find((n) => n.original === token);
      if (negInfo) {
        const rootScore = lookupScore(negInfo.root, lexicon);
        if (rootScore !== null) {
          const flipped = rootScore * CIRCUMFIX_NEGATION_FACTOR;
          totalScore += flipped;
          scoredCount++;
          if (flipped > 0) {
            positiveTokens.push(token);
          } else {
            negativeTokens.push(token);
          }
          continue;
        }
      }
    }

    let score = lookupScore(token, lexicon);
    if (score === null) {
      continue;
    }

    const prevToken = i > 0 ? tokens[i - 1] : null;
    if (prevToken && isNegator(prevToken, lexicon)) {
      score = score * NEGATION_FLIP_FACTOR;
      hasNegation = true;
    }

    const nextToken = i + 1 < tokens.length ? tokens[i + 1] : null;
    if (nextToken) {
      const intensifier = getIntensifierMultiplier(nextToken, lexicon);
      if (intensifier !== null) {
        score = score * intensifier;
      }
    }
    if (prevToken) {
      const intensifier = getIntensifierMultiplier(prevToken, lexicon);
      if (intensifier !== null && !isNegator(prevToken, lexicon)) {
        score = score * intensifier;
      }
    }

    totalScore += score;
    scoredCount++;

    if (score > 0) {
      positiveTokens.push(token);
    } else if (score < 0) {
      negativeTokens.push(token);
    }
  }

  const finalScore = scoredCount > 0
    ? Math.max(-1, Math.min(1, totalScore / scoredCount))
    : 0;

  const label = determineLabel(finalScore, positiveTokens.length, negativeTokens.length);

  return {
    score: Math.round(finalScore * 100) / 100,
    label,
    positiveTokens,
    negativeTokens,
    negated: hasNegation
  };
}

export { loadLexicon };
