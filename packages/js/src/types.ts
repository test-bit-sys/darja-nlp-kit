export interface NormalizeOptions {
  preserveTashkeel?: boolean;
  preserveLength?: boolean;
}

export interface ArabiziOptions {
  preserveFrench?: boolean;
}

export interface TokenizeResult {
  tokens: string[];
  negations: NegationInfo[];
}

export interface NegationInfo {
  original: string;
  root: string;
  negated: boolean;
}

export type SentimentLabel = 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL' | 'MIXED';

export interface SentimentResult {
  score: number;
  label: SentimentLabel;
  positiveTokens: string[];
  negativeTokens: string[];
  negated: boolean;
}

export interface StopwordsData {
  [category: string]: string[];
}

export interface LexiconData {
  positive: Record<string, number>;
  negative: Record<string, number>;
  negators: string[];
  intensifiers: Record<string, number>;
}

export interface ArabiziRules {
  numbers: Record<string, string>;
  digraphs: Record<string, string>;
  singles: Record<string, string>;
  french_whitelist: string[];
  french_suffixes: string[];
  overrides: Record<string, string>;
}
