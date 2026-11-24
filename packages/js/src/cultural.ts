import * as path from 'path';
import * as fs from 'fs';
import { CulturalAnalysisResult, CulturalMatch } from './types';

let _cultureCache: any = null;
let _slangCache: any = null;
let _memesCache: any = null;
let _francoCache: any = null;

const GENERIC_STOP = new Set(['سلعة', 'سوق', 'حي', 'شارع', 'باب', 'واد', 'ساحة', 'جبل', 'جبال', 'طاجين', 'طبق', 'أكلة']);

function extractKeywords(text: string): string[] {
  const clean = text.split(' (')[0].trim();
  const parts = text.split(/[/(),]|\s+و/);
  const res = new Set<string>([text, clean]);
  for (const part of parts) {
    const p = part.trim();
    if (p.length > 2 && !GENERIC_STOP.has(p)) {
      res.add(p);
      if (p.startsWith('ال') && p.length > 3) {
        res.add(p.slice(2));
      } else if (!p.startsWith('ال')) {
        res.add('ال' + p);
      }
      const words = p.split(/\s+/);
      if (words.length === 2) {
        for (const w of words) {
          if (w.length > 3 && !GENERIC_STOP.has(w)) {
            res.add(w);
            if (w.startsWith('ال') && w.length > 4) {
              res.add(w.slice(2));
            } else if (!w.startsWith('ال')) {
              res.add('ال' + w);
            }
          }
        }
      }
    }
  }
  return Array.from(res).filter((x) => x.length > 2 && !GENERIC_STOP.has(x));
}

export function getCulturalData(): any {
  if (_cultureCache) {
    return _cultureCache;
  }
  try {
    const dataPath = path.join(__dirname, '..', 'data', 'culture.json');
    if (fs.existsSync(dataPath)) {
      _cultureCache = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
      return _cultureCache;
    }
  } catch {
    // fallback
  }
  _cultureCache = { proverbs: [], memes_and_trends: [], landmarks: [], gastronomy: [] };
  return _cultureCache;
}

export function getSlangData(): any {
  if (_slangCache) {
    return _slangCache;
  }
  try {
    const dataPath = path.join(__dirname, '..', 'data', 'slang.json');
    if (fs.existsSync(dataPath)) {
      _slangCache = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
      return _slangCache;
    }
  } catch {
    // fallback
  }
  _slangCache = { expressions: [] };
  return _slangCache;
}

export function getMemesData(): any {
  if (_memesCache) {
    return _memesCache;
  }
  try {
    const dataPath = path.join(__dirname, '..', 'data', 'memes.json');
    if (fs.existsSync(dataPath)) {
      _memesCache = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
      return _memesCache;
    }
  } catch {
    // fallback
  }
  _memesCache = { memes: [] };
  return _memesCache;
}

export function getFrancoDarjaData(): any {
  if (_francoCache) {
    return _francoCache;
  }
  try {
    const dataPath = path.join(__dirname, '..', 'data', 'franco_darja.json');
    if (fs.existsSync(dataPath)) {
      _francoCache = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
      return _francoCache;
    }
  } catch {
    // fallback
  }
  _francoCache = { words: [] };
  return _francoCache;
}

export function detectCulturalReferences(text: string): CulturalAnalysisResult {
  if (!text || !text.trim()) {
    return {
      hasCulturalReference: false,
      proverbs: [],
      memesAndTrends: [],
      landmarks: [],
      gastronomy: [],
      slangExpressions: [],
      allMatches: [],
      culturalSummary: 'لا توجد إشارات ثقافية أو شعبية خاصة.',
    };
  }

  const lowerText = text.toLowerCase();
  const cultureDb = getCulturalData();
  const slangDb = getSlangData();

  const matchedProverbs: CulturalMatch[] = [];
  const matchedMemes: CulturalMatch[] = [];
  const matchedLandmarks: CulturalMatch[] = [];
  const matchedGastronomy: CulturalMatch[] = [];
  const matchedSlang: CulturalMatch[] = [];

  // 1. Proverbs
  for (const p of cultureDb.proverbs || []) {
    const pText = p.text || '';
    const pArabizi = p.arabizi || '';
    if ((pText && text.includes(pText)) || (pArabizi && lowerText.includes(pArabizi.toLowerCase()))) {
      matchedProverbs.push({
        matchedText: text.includes(pText) ? pText : pArabizi,
        category: 'proverb',
        canonicalName: pText,
        meaning: p.meaning || '',
        metadata: { category: p.category, region: p.region },
      });
    }
  }

  // 2. Memes & Trends (from culture.json and memes.json)
  for (const m of cultureDb.memes_and_trends || []) {
    const mPhrase = m.phrase || '';
    const mArabizi = m.arabizi || '';
    if ((mPhrase && text.includes(mPhrase)) || (mArabizi && lowerText.includes(mArabizi.toLowerCase()))) {
      matchedMemes.push({
        matchedText: text.includes(mPhrase) ? mPhrase : mArabizi,
        category: 'meme_trend',
        canonicalName: mPhrase,
        meaning: m.meaning || '',
        metadata: { tone: m.tone, context: m.context },
      });
    }
  }

  const memesDb = getMemesData();
  for (const m of memesDb.memes || []) {
    const mPhrase = m.phrase || '';
    const mArabizi = m.arabizi || '';
    if ((mPhrase && text.includes(mPhrase)) || (mArabizi && lowerText.includes(mArabizi.toLowerCase()))) {
      if (!matchedMemes.some((x) => x.canonicalName === mPhrase)) {
        matchedMemes.push({
          matchedText: text.includes(mPhrase) ? mPhrase : mArabizi,
          category: 'meme_trend',
          canonicalName: mPhrase,
          meaning: m.meaning || '',
          metadata: { origin: m.origin, category: m.category, tags: m.tags },
        });
      }
    }
  }

  // 3. Landmarks
  for (const lmk of cultureDb.landmarks || []) {
    const lName = lmk.name || '';
    const keywords = extractKeywords(lName);
    for (const kw of keywords) {
      if (kw && text.includes(kw)) {
        matchedLandmarks.push({
          matchedText: kw,
          category: 'landmark',
          canonicalName: lName,
          meaning: lmk.description || '',
          metadata: { city: lmk.city, wilaya_code: lmk.wilaya_code },
        });
        break;
      }
    }
  }

  // 4. Gastronomy
  for (const f of cultureDb.gastronomy || []) {
    const fName = f.name || '';
    const fArabizi = f.arabizi || '';
    const keywords = extractKeywords(fName);
    let matched = false;
    for (const kw of keywords) {
      if (kw && text.includes(kw)) {
        matchedGastronomy.push({
          matchedText: kw,
          category: 'gastronomy',
          canonicalName: fName,
          meaning: f.description || '',
          metadata: { origin: f.origin, category: f.category },
        });
        matched = true;
        break;
      }
    }
    if (!matched && fArabizi) {
      const parts = fArabizi.split('/');
      for (const part of parts) {
        if (part.trim() && lowerText.includes(part.trim().toLowerCase())) {
          matchedGastronomy.push({
            matchedText: part.trim(),
            category: 'gastronomy',
            canonicalName: fName,
            meaning: f.description || '',
            metadata: { origin: f.origin, category: f.category },
          });
          break;
        }
      }
    }
  }

  // 5. Slang Expressions
  for (const s of slangDb.expressions || []) {
    const sTerm = s.term || '';
    const sArabizi = s.arabizi || '';
    const keywords = extractKeywords(sTerm);
    let matched = false;
    for (const kw of keywords) {
      if (kw && text.includes(kw)) {
        matchedSlang.push({
          matchedText: kw,
          category: 'slang',
          canonicalName: sTerm,
          meaning: s.meaning || '',
          metadata: { type: s.type, polarity: s.polarity },
        });
        matched = true;
        break;
      }
    }
    if (!matched && sArabizi && lowerText.includes(sArabizi.toLowerCase())) {
      matchedSlang.push({
        matchedText: sArabizi,
        category: 'slang',
        canonicalName: sTerm,
        meaning: s.meaning || '',
        metadata: { type: s.type, polarity: s.polarity },
      });
    }
  }

  const allMatches = [
    ...matchedProverbs,
    ...matchedMemes,
    ...matchedLandmarks,
    ...matchedGastronomy,
    ...matchedSlang,
  ];

  const hasRef = allMatches.length > 0;
  const summaryParts: string[] = [];
  if (matchedProverbs.length > 0) {
    summaryParts.push(`أمثال شعبية: ${matchedProverbs.map((p) => `"${p.canonicalName}"`).join('، ')}`);
  }
  if (matchedMemes.length > 0) {
    summaryParts.push(`ترندات وميمز: ${matchedMemes.map((m) => `"${m.canonicalName}"`).join('، ')}`);
  }
  if (matchedLandmarks.length > 0) {
    summaryParts.push(`معالم وأسواق: ${matchedLandmarks.map((l) => `"${l.canonicalName}"`).join('، ')}`);
  }
  if (matchedGastronomy.length > 0) {
    summaryParts.push(`مأكولات جزائرية: ${matchedGastronomy.map((f) => `"${f.canonicalName}"`).join('، ')}`);
  }
  if (matchedSlang.length > 0) {
    summaryParts.push(`مصطلحات شارع: ${matchedSlang.map((s) => `"${s.canonicalName}"`).join('، ')}`);
  }

  const culturalSummary = summaryParts.length > 0 ? summaryParts.join(' | ') : 'لا توجد إشارات ثقافية خاصة.';

  return {
    hasCulturalReference: hasRef,
    proverbs: matchedProverbs,
    memesAndTrends: matchedMemes,
    landmarks: matchedLandmarks,
    gastronomy: matchedGastronomy,
    slangExpressions: matchedSlang,
    allMatches,
    culturalSummary,
  };
}

export function detectMemes(text: string): CulturalMatch[] {
  const res = detectCulturalReferences(text);
  return res.memesAndTrends;
}

export interface FrancoDarjaMatch {
  matchedText: string;
  darjaAr: string;
  arabizi: string;
  frOrigin: string;
  category: string;
  meaningAr: string;
  example: string;
}

export function detectFrancoDarja(text: string): FrancoDarjaMatch[] {
  if (!text || !text.trim()) return [];

  const lowerText = text.toLowerCase();
  const francoDb = getFrancoDarjaData();
  const matches: FrancoDarjaMatch[] = [];

  for (const item of francoDb.words || []) {
    const arTerm = item.darja_ar || '';
    const arabiziTerm = item.arabizi || '';
    const frOrigin = item.fr_origin || '';

    let matchedKey: string | null = null;
    if (arTerm && text.includes(arTerm)) {
      matchedKey = arTerm;
    } else if (arabiziTerm && lowerText.includes(arabiziTerm.toLowerCase())) {
      matchedKey = arabiziTerm;
    } else if (frOrigin && lowerText.includes(frOrigin.toLowerCase())) {
      matchedKey = frOrigin;
    }

    if (matchedKey) {
      matches.push({
        matchedText: matchedKey,
        darjaAr: arTerm,
        arabizi: arabiziTerm,
        frOrigin,
        category: item.category,
        meaningAr: item.meaning_ar,
        example: item.example,
      });
    }
  }

  return matches;
}
