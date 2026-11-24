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
export type SentimentMode = 'hybrid' | 'lexicon' | 'ml';

export interface SentimentOptions {
  mode?: SentimentMode;
  customPositive?: Record<string, number>;
  customNegative?: Record<string, number>;
}

export interface SentimentResult {
  score: number;
  label: SentimentLabel;
  positiveTokens: string[];
  negativeTokens: string[];
  negated: boolean;
  method?: string;
  probabilities?: Record<string, number>;
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

export type TelecomOperator = 'MOBILIS' | 'DJEZZY' | 'OOREDOO' | 'ALGERIE_TELECOM';

export interface PhoneEntity {
  raw: string;
  normalized: string;
  operator?: TelecomOperator | null;
  operatorLabel?: string | null;
  formatted?: string | null;
  whatsappUrl?: string | null;
}

export interface QuantityEntity {
  raw: string;
  value: number;
  unit: string;
}

export interface ProductAttributes {
  colors: string[];
  sizes: string[];
}

export interface EntitiesResult {
  wilayas: WilayaEntity[];
  payments: PaymentEntity[];
  prices: PriceEntity[];
  deliveries?: DeliveryEntity[];
  deliveryMode?: DeliveryModeEntity | null;
  phones?: PhoneEntity[];
  quantities?: QuantityEntity[];
  attributes?: ProductAttributes | null;
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

export type EscalationUrgency = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
export type EscalationReason = 'ANGRY_CUSTOMER' | 'HUMAN_REQUESTED' | 'DISPUTE' | 'LEGAL_THREAT';

export interface EscalationResult {
  needsEscalation: boolean;
  urgency: EscalationUrgency;
  reason?: EscalationReason | null;
  matchedTriggers: string[];
  guideline: string;
}

export type CulturalCategory = 'proverb' | 'meme_trend' | 'landmark' | 'gastronomy' | 'slang';

export interface CulturalMatch {
  matchedText: string;
  category: CulturalCategory;
  canonicalName: string;
  meaning: string;
  metadata?: Record<string, any>;
}

export interface CulturalAnalysisResult {
  hasCulturalReference: boolean;
  proverbs: CulturalMatch[];
  memesAndTrends: CulturalMatch[];
  landmarks: CulturalMatch[];
  gastronomy: CulturalMatch[];
  slangExpressions: CulturalMatch[];
  allMatches: CulturalMatch[];
  culturalSummary: string;
}
