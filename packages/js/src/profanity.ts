/**
 * Algerian Darja profanity, vulgarity, and toxic language detection and censorship.
 */
import * as path from 'path';
import * as fs from 'fs';

export type ProfanitySeverity = 'none' | 'low' | 'medium' | 'high';

export interface ProfanityMatch {
  term: string;
  category: string;
  severity: ProfanitySeverity;
  matchedText: string;
  start: number;
  end: number;
}

export interface ProfanityResult {
  isProfane: boolean;
  severity: ProfanitySeverity;
  matches: ProfanityMatch[];
  censoredText: string;
}

interface ProfanityTermItem {
  term: string;
  ar: string;
  arabizi: string[];
  category: string;
  severity: ProfanitySeverity;
}

interface ProfanityDataset {
  terms: ProfanityTermItem[];
}

let profanityData: ProfanityDataset | null = null;

function loadProfanityData(): ProfanityDataset {
  if (profanityData) return profanityData;

  const dataPath = path.resolve(__dirname, '../data/profanity.json');
  const raw = fs.readFileSync(dataPath, 'utf-8');
  profanityData = JSON.parse(raw) as ProfanityDataset;
  return profanityData;
}

function normalizeForMatching(text: string): string {
  let t = text.toLowerCase();
  // Strip tashkeel and tatweel
  t = t.replace(/[\u064B-\u065F\u0670\u0640]/g, '');
  // Collapse repetitive chars (3+ down to 2)
  t = t.replace(/(.)\1{2,}/g, '$1$1');
  return t;
}

export interface ProfanityOptions {
  customTerms?: string[];
}

export function detectProfanity(text: string, options?: ProfanityOptions): ProfanityResult {
  if (!text || !text.trim()) {
    return {
      isProfane: false,
      severity: 'none',
      matches: [],
      censoredText: text
    };
  }

  const data = loadProfanityData();
  const termsList = [...(data.terms || [])];
  if (options?.customTerms) {
    for (const ct of options.customTerms) {
      if (ct && ct.trim()) {
        termsList.push({
          term: ct.trim(),
          ar: ct.trim(),
          arabizi: [ct.trim()],
          category: 'custom',
          severity: 'medium',
        });
      }
    }
  }
  const matches: ProfanityMatch[] = [];
  const normText = normalizeForMatching(text);
  const censoredChars = text.split('');

  const severityOrder: Record<ProfanitySeverity, number> = {
    none: 0,
    low: 1,
    medium: 2,
    high: 3
  };

  let highestSeverity: ProfanitySeverity = 'none';

  for (const item of termsList) {
    const variants: string[] = [];
    if (item.ar) variants.push(item.ar);
    if (item.arabizi) variants.push(...item.arabizi);

    for (const v of variants) {
      if (!v) continue;
      const escaped = v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const pattern = new RegExp(`(?<![\\w\u0600-\u06FF])${escaped}(?![\\w\u0600-\u06FF])`, 'gi');

      let m: RegExpExecArray | null;
      while ((m = pattern.exec(normText)) !== null) {
        const start = m.index;
        const end = start + m[0].length;
        const matchedText = text.slice(start, end);

        matches.push({
          term: item.term || v,
          category: item.category || 'insult_street',
          severity: item.severity || 'medium',
          matchedText,
          start,
          end
        });

        if (severityOrder[item.severity] > severityOrder[highestSeverity]) {
          highestSeverity = item.severity;
        }

        for (let i = start; i < Math.min(end, censoredChars.length); i++) {
          censoredChars[i] = '*';
        }
      }
    }
  }

  const isProfane = matches.length > 0;
  return {
    isProfane,
    severity: isProfane ? highestSeverity : 'none',
    matches,
    censoredText: censoredChars.join('')
  };
}

export function isProfane(text: string, options?: ProfanityOptions): boolean {
  return detectProfanity(text, options).isProfane;
}

export function censorProfanity(text: string, mask: string = '***', options?: ProfanityOptions): string {
  const result = detectProfanity(text, options);
  if (!result.isProfane) return text;
  return result.censoredText.replace(/\*+/g, mask);
}
