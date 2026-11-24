import { SentimentResult, SentimentLabel, SentimentMode, SentimentOptions, LexiconData } from './types';
import { tokenize } from './stopwords';
import * as path from 'path';
import * as fs from 'fs';

interface SentimentModelData {
  priors: number[];
  weights: Record<string, number[]>;
}

let _lexicon: LexiconData | null = null;
let _sentimentModel: SentimentModelData | null | undefined = undefined;

function loadLexicon(): LexiconData {
  if (_lexicon) {
    return _lexicon;
  }
  const dataPath = path.join(__dirname, '..', 'data', 'lexicon.json');
  const raw = fs.readFileSync(dataPath, 'utf-8');
  _lexicon = JSON.parse(raw) as LexiconData;
  return _lexicon;
}

function loadSentimentModel(): SentimentModelData | null {
  if (_sentimentModel !== undefined) {
    return _sentimentModel;
  }
  const modelPath = path.join(__dirname, '..', 'data', 'sentiment_model.json');
  if (fs.existsSync(modelPath)) {
    try {
      const raw = fs.readFileSync(modelPath, 'utf-8');
      _sentimentModel = JSON.parse(raw) as SentimentModelData;
      return _sentimentModel;
    } catch {
      _sentimentModel = null;
      return null;
    }
  }
  _sentimentModel = null;
  return null;
}

const NEGATION_FLIP_FACTOR = -0.8;
const CIRCUMFIX_NEGATION_FACTOR = -0.8;

const ARABIC_PREFIXES = ['\u0628\u0627\u0644', '\u0648\u0627\u0644', '\u0641\u0627\u0644', '\u0643\u0627\u0644', '\u0627\u0644', '\u0648', '\u0628', '\u0644', '\u0641', '\u0643'];
const ARABIC_SUFFIXES = ['\u064A\u0646', '\u0627\u062A', '\u0629', '\u0647'];

const RE_URL = /https?:\/\/\S+|@\w+/g;
const RE_TASH = /[\u064B-\u065F\u0670\u0640]/g;
const RE_ALEF = /[\u0623\u0625\u0622]/g;
const RE_ELONG = /(.)\1{2,}/g;
const RE_ML_TOK = /[a-zA-Z0-9\u0621-\u064A\u0671-\u06D3]+|[\u{1F300}-\u{1FAFF}\u2600-\u27BF]+/gu;
const RE_ALPHA = /^[a-zA-Z\u0621-\u064A\u0671-\u06D3]+$/;

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

function checkLexiconDirect(
  word: string,
  lexicon: LexiconData,
  customPositive?: Record<string, number>,
  customNegative?: Record<string, number>
): number | null {
  const lower = word.toLowerCase();
  if (customPositive) {
    if (customPositive[word] !== undefined) return customPositive[word];
    if (customPositive[lower] !== undefined) return customPositive[lower];
  }
  if (customNegative) {
    if (customNegative[word] !== undefined) return customNegative[word];
    if (customNegative[lower] !== undefined) return customNegative[lower];
  }

  if (lexicon.positive[word] !== undefined) return lexicon.positive[word];
  if (lexicon.positive[lower] !== undefined) return lexicon.positive[lower];
  if (lexicon.negative[word] !== undefined) return lexicon.negative[word];
  if (lexicon.negative[lower] !== undefined) return lexicon.negative[lower];
  return null;
}

function lookupScore(
  token: string,
  lexicon: LexiconData,
  customPositive?: Record<string, number>,
  customNegative?: Record<string, number>
): number | null {
  const direct = checkLexiconDirect(token, lexicon, customPositive, customNegative);
  if (direct !== null) return direct;

  const strippedPrefix = stripArabicPrefix(token);
  if (strippedPrefix) {
    const score = checkLexiconDirect(strippedPrefix, lexicon, customPositive, customNegative);
    if (score !== null) return score;
  }

  const strippedSuffix = stripArabicSuffix(token);
  if (strippedSuffix) {
    const score = checkLexiconDirect(strippedSuffix, lexicon, customPositive, customNegative);
    if (score !== null) return score;
  }

  if (strippedPrefix) {
    const strippedBoth = stripArabicSuffix(strippedPrefix);
    if (strippedBoth) {
      const score = checkLexiconDirect(strippedBoth, lexicon, customPositive, customNegative);
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

function extractMlFeatures(text: string): string[] {
  let t = text.toLowerCase().replace(RE_URL, ' ');
  t = t.replace(RE_TASH, '');
  t = t.replace(RE_ALEF, '\u0627').replace(/\u0629/g, '\u0647').replace(/\u0649/g, '\u064A');
  t = t.replace(RE_ELONG, '$1$1');
  const toks = t.match(RE_ML_TOK) || [];
  const feats = [...toks];
  for (let i = 0; i < toks.length - 1; i++) {
    feats.push(`${toks[i]}_${toks[i + 1]}`);
  }
  for (const w of toks) {
    if (w.length >= 5 && RE_ALPHA.test(w)) {
      feats.push(`p3:${w.slice(0, 3)}`);
      feats.push(`s3:${w.slice(-3)}`);
    }
  }
  return feats;
}

function predictMlSentiment(text: string): {
  label: SentimentLabel;
  score: number;
  probabilities: Record<string, number>;
  pos: string[];
  neg: string[];
} | null {
  const model = loadSentimentModel();
  if (!model || !model.priors || !model.weights) {
    return null;
  }

  const feats = extractMlFeatures(text);
  if (feats.length === 0) return null;

  const scores = [model.priors[0], model.priors[1], model.priors[2]];
  const matchedPos: string[] = [];
  const matchedNeg: string[] = [];
  let hits = 0;

  for (const f of feats) {
    const w = model.weights[f];
    if (w !== undefined) {
      hits++;
      scores[0] += w[0];
      scores[1] += w[1];
      scores[2] += w[2];
      if (!f.includes('_') && !f.startsWith('p3:') && !f.startsWith('s3:')) {
        if (w[2] - w[0] > 0.4 && !matchedPos.includes(f)) matchedPos.push(f);
        else if (w[0] - w[2] > 0.4 && !matchedNeg.includes(f)) matchedNeg.push(f);
      }
    }
  }

  if (hits === 0) return null;

  const maxS = Math.max(...scores);
  const exps = scores.map((s) => Math.exp(Math.max(-50, s - maxS)));
  const totalE = exps.reduce((a, b) => a + b, 0) || 1;
  const probs = exps.map((e) => e / totalE);
  const probDict: Record<string, number> = {
    NEGATIVE: Math.round(probs[0] * 10000) / 10000,
    NEUTRAL: Math.round(probs[1] * 10000) / 10000,
    POSITIVE: Math.round(probs[2] * 10000) / 10000,
  };

  let predLabel: SentimentLabel = 'NEUTRAL';
  if (probs[2] >= probs[0] && probs[2] >= probs[1]) {
    predLabel = 'POSITIVE';
  } else if (probs[0] >= probs[2] && probs[0] >= probs[1]) {
    predLabel = 'NEGATIVE';
  }

  const polarity = Math.round(Math.max(-1, Math.min(1, probs[2] - probs[0])) * 100) / 100;
  return {
    label: predLabel,
    score: polarity,
    probabilities: probDict,
    pos: matchedPos.slice(0, 6),
    neg: matchedNeg.slice(0, 6),
  };
}

function scanPhraseMatches(
  tokens: string[],
  lexicon: LexiconData,
  customPositive?: Record<string, number>,
  customNegative?: Record<string, number>
): { matches: Array<{ start: number; end: number; phrase: string; score: number }>; covered: Set<number> } {
  const phraseMap: Record<string, number> = {};
  for (const src of [lexicon.positive, lexicon.negative]) {
    for (const [k, v] of Object.entries(src)) {
      if (k.includes(' ')) phraseMap[k.toLowerCase()] = v;
    }
  }
  if (customPositive) {
    for (const [k, v] of Object.entries(customPositive)) {
      if (k.includes(' ')) phraseMap[k.toLowerCase()] = v;
    }
  }
  if (customNegative) {
    for (const [k, v] of Object.entries(customNegative)) {
      if (k.includes(' ')) phraseMap[k.toLowerCase()] = v;
    }
  }

  const matches: Array<{ start: number; end: number; phrase: string; score: number }> = [];
  const covered = new Set<number>();
  if (Object.keys(phraseMap).length === 0 || tokens.length < 2) {
    return { matches, covered };
  }

  const lowerTokens = tokens.map((t) => t.toLowerCase());
  for (const win of [4, 3, 2]) {
    for (let i = 0; i <= lowerTokens.length - win; i++) {
      let overlap = false;
      for (let idx = i; idx < i + win; idx++) {
        if (covered.has(idx)) {
          overlap = true;
          break;
        }
      }
      if (overlap) continue;
      const cand = lowerTokens.slice(i, i + win).join(' ');
      if (phraseMap[cand] !== undefined) {
        matches.push({ start: i, end: i + win, phrase: tokens.slice(i, i + win).join(' '), score: phraseMap[cand] });
        for (let idx = i; idx < i + win; idx++) covered.add(idx);
      }
    }
  }

  return { matches, covered };
}

export function analyzeSentiment(text: string, options?: SentimentOptions): SentimentResult {
  const mode: SentimentMode = options?.mode || 'hybrid';

  if (!text) {
    return {
      score: 0,
      label: 'NEUTRAL',
      positiveTokens: [],
      negativeTokens: [],
      negated: false,
      method: mode,
    };
  }

  if (mode === 'ml') {
    const mlRes = predictMlSentiment(text);
    if (mlRes) {
      return {
        score: mlRes.score,
        label: mlRes.label,
        positiveTokens: mlRes.pos,
        negativeTokens: mlRes.neg,
        negated: false,
        method: 'ml',
        probabilities: mlRes.probabilities,
      };
    }
    return {
      score: 0,
      label: 'NEUTRAL',
      positiveTokens: [],
      negativeTokens: [],
      negated: false,
      method: 'ml',
    };
  }

  const lexicon = loadLexicon();
  const { tokens, negations } = tokenize(text);

  const positiveTokens: string[] = [];
  const negativeTokens: string[] = [];
  let totalScore = 0;
  let scoredCount = 0;
  let hasNegation = false;

  // 1. Multi-word phrase matching
  const { matches: phraseMatches, covered } = scanPhraseMatches(
    tokens,
    lexicon,
    options?.customPositive,
    options?.customNegative
  );
  for (const pm of phraseMatches) {
    let pScore = pm.score;
    const prevToken = pm.start > 0 ? tokens[pm.start - 1] : null;
    if (prevToken && isNegator(prevToken, lexicon)) {
      pScore *= NEGATION_FLIP_FACTOR;
      hasNegation = true;
    }
    const nextToken = pm.end < tokens.length ? tokens[pm.end] : null;
    if (nextToken) {
      const mult = getIntensifierMultiplier(nextToken, lexicon);
      if (mult !== null) pScore *= mult;
    }
    totalScore += pScore;
    scoredCount++;
    if (pScore > 0) positiveTokens.push(pm.phrase);
    else if (pScore < 0) negativeTokens.push(pm.phrase);
  }

  // 2. Unigram + circumfix + intensifiers
  const circumfixNegatedOriginals = new Set(
    negations.filter((n) => n.negated).map((n) => n.original)
  );

  for (let i = 0; i < tokens.length; i++) {
    if (covered.has(i)) continue;
    const token = tokens[i];

    if (circumfixNegatedOriginals.has(token)) {
      hasNegation = true;
      const negInfo = negations.find((n) => n.original === token);
      if (negInfo) {
        const rootScore = lookupScore(negInfo.root, lexicon, options?.customPositive, options?.customNegative);
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

    let score = lookupScore(token, lexicon, options?.customPositive, options?.customNegative);
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

  const mlRes = mode === 'hybrid' ? predictMlSentiment(text) : null;
  if (scoredCount === 0 && mode === 'hybrid' && mlRes) {
    if (mlRes.label !== 'NEUTRAL' && Math.abs(mlRes.score) >= 0.15) {
      return {
        score: mlRes.score,
        label: mlRes.label,
        positiveTokens: mlRes.pos,
        negativeTokens: mlRes.neg,
        negated: hasNegation,
        method: 'ml',
        probabilities: mlRes.probabilities,
      };
    }
    return {
      score: 0,
      label: 'NEUTRAL',
      positiveTokens: [],
      negativeTokens: [],
      negated: hasNegation,
      method: 'hybrid',
      probabilities: mlRes.probabilities,
    };
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
    negated: hasNegation,
    method: mode === 'lexicon' ? 'lexicon' : 'hybrid',
    probabilities: mlRes?.probabilities,
  };
}

export { loadLexicon };
