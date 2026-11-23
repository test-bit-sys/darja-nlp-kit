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

export interface WilayaRaw {
  code: number;
  code_str: string;
  name_ar: string;
  name_fr: string;
  aliases: string[];
  communes_sample?: string[];
  communes_fr_sample?: string[];
}

export interface WilayaEntity {
  code: number;
  codeStr: string;
  nameAr: string;
  nameFr: string;
  matchedText: string;
  commune?: string | null;
}

export type PaymentMethodType = 'BARIDIMOB' | 'EDAHABIA' | 'CCP' | 'COD';

export interface PaymentEntity {
  type: PaymentMethodType;
  label: string;
  matchedText: string;
}

export interface PriceEntity {
  raw: string;
  amount: number | null;
  currency: 'DZD';
}

export type DeliveryCompanyType = 'YALIDINE' | 'ZR_EXPRESS' | 'MAYSTRO' | 'PROCOLIS' | 'EMS' | 'KAZITOUR' | 'GUEPEX';
export type DeliveryModeType = 'STOP_DESK' | 'HOME_DELIVERY';

export interface DeliveryEntity {
  company: DeliveryCompanyType;
  label: string;
  matchedText: string;
}

export interface DeliveryModeEntity {
  mode: DeliveryModeType;
  label: string;
  matchedText: string;
}

export interface PhoneEntity {
  raw: string;
  normalized: string;
}

export interface EntitiesResult {
  wilayas: WilayaEntity[];
  payments: PaymentEntity[];
  prices: PriceEntity[];
  deliveries?: DeliveryEntity[];
  deliveryMode?: DeliveryModeEntity | null;
  phones?: PhoneEntity[];
}

export type DialectRegion = 'WEST' | 'EAST' | 'CENTER' | 'SOUTH' | 'GENERAL_DARJA';

export interface DialectResult {
  region: DialectRegion;
  confidence: number;
  detectedMarkers: string[];
}

export type IntentType =
  | 'ORDER'
  | 'PRICE_INQUIRY'
  | 'AVAILABILITY_INQUIRY'
  | 'DELIVERY_INQUIRY'
  | 'COMPLAINT'
  | 'GREETING'
  | 'UNKNOWN';

export interface IntentResult {
  intent: IntentType;
  confidence: number;
  matchedKeywords: string[];
}
