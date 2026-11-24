/**
 * Unified configurable NLP pipeline and convenience facade for Algerian Darja.
 */
import { normalize } from './normalizer';
import { arabiziToArabic } from './arabizi';
import { removeStopwords } from './stopwords';
import { analyzeSentiment } from './sentiment';
import { identifyIntent } from './intent';
import { detectDialect } from './dialect';
import { extractEntities } from './entities';
import { detectEscalation } from './escalation';
import { detectProfanity, censorProfanity, ProfanityResult } from './profanity';
import { detectCulturalReferences, detectFrancoDarja, FrancoDarjaMatch } from './cultural';
import { respondToDarja, DialoguePersona, DialogueResponse, DialogueRule, DialogueScript, DialogueStrategy } from './dialogue';
import { buildAgentContext, formatAgentSystemPrompt } from './agent';
import {
  CulturalAnalysisResult,
  DialectResult,
  EntitiesResult,
  EscalationResult,
  IntentResult,
  SentimentMode,
  SentimentResult,
} from './types';

export type AnalysisTask =
  | 'normalize'
  | 'arabizi'
  | 'clean'
  | 'sentiment'
  | 'intent'
  | 'dialect'
  | 'entities'
  | 'escalation'
  | 'profanity'
  | 'cultural'
  | 'franco'
  | 'reply';

export interface PipelineOptions {
  storeName?: string;
  persona?: DialoguePersona;
  script?: DialogueScript;
  sentimentMode?: SentimentMode;
  dialogueStrategy?: DialogueStrategy;
  preserveFrench?: boolean;
  customPositive?: Record<string, number>;
  customNegative?: Record<string, number>;
  customStopwords?: string[];
  customProfanity?: string[];
  customRules?: DialogueRule[];
}

export interface AnalyzeOptions {
  tasks?: AnalysisTask[];
  includeReply?: boolean;
  persona?: DialoguePersona;
  sentimentMode?: SentimentMode;
}

export interface AnalysisReport {
  rawText: string;
  normalized: string | null;
  arabic: string | null;
  cleaned: string | null;
  sentiment: SentimentResult | null;
  intent: IntentResult | null;
  dialect: DialectResult | null;
  entities: EntitiesResult | null;
  escalation: EscalationResult | null;
  profanity: ProfanityResult | null;
  cultural: CulturalAnalysisResult | null;
  francoDarja: FrancoDarjaMatch[] | null;
  reply: DialogueResponse | null;
}

const ALL_TASKS: AnalysisTask[] = [
  'normalize',
  'arabizi',
  'clean',
  'sentiment',
  'intent',
  'dialect',
  'entities',
  'escalation',
  'profanity',
  'cultural',
  'franco',
  'reply',
];

export class DarjaPipeline {
  public storeName: string;
  public persona: DialoguePersona;
  public script: DialogueScript;
  public sentimentMode: SentimentMode;
  public dialogueStrategy: DialogueStrategy;
  public preserveFrench: boolean;
  public customPositive: Record<string, number>;
  public customNegative: Record<string, number>;
  public customStopwords: Set<string>;
  public customProfanity: string[];
  public customRules: DialogueRule[];

  constructor(options?: PipelineOptions) {
    this.storeName = options?.storeName ?? 'Bazar El Djazair';
    this.persona = options?.persona ?? 'casual';
    this.script = options?.script ?? 'auto';
    this.sentimentMode = options?.sentimentMode ?? 'hybrid';
    this.dialogueStrategy = options?.dialogueStrategy ?? 'auto';
    this.preserveFrench = options?.preserveFrench ?? true;
    this.customPositive = { ...(options?.customPositive || {}) };
    this.customNegative = { ...(options?.customNegative || {}) };
    this.customStopwords = new Set(
      (options?.customStopwords || []).filter(Boolean).map((w) => w.toLowerCase())
    );
    this.customProfanity = [...(options?.customProfanity || [])];
    this.customRules = [...(options?.customRules || [])];
  }

  extendLexicon(positive?: Record<string, number>, negative?: Record<string, number>): this {
    if (positive) Object.assign(this.customPositive, positive);
    if (negative) Object.assign(this.customNegative, negative);
    return this;
  }

  addStopwords(words: string[]): this {
    for (const w of words) {
      if (w && w.trim()) this.customStopwords.add(w.trim().toLowerCase());
    }
    return this;
  }

  addProfanity(terms: string[]): this {
    for (const t of terms) {
      if (t && t.trim() && !this.customProfanity.includes(t.trim())) {
        this.customProfanity.push(t.trim());
      }
    }
    return this;
  }

  addDialogueRule(rule: DialogueRule): this {
    this.customRules.push(rule);
    return this;
  }

  clean(text: string): string {
    if (!text) return '';
    const baseCleaned = removeStopwords(normalize(text));
    if (this.customStopwords.size === 0) return baseCleaned;
    return baseCleaned
      .split(/\s+/)
      .filter((tok) => tok && !this.customStopwords.has(tok.toLowerCase()))
      .join(' ');
  }

  moderate(text: string, mask = '***'): ProfanityResult {
    const res = detectProfanity(
      text,
      this.customProfanity.length ? { customTerms: this.customProfanity } : undefined
    );
    if (res.isProfane && mask !== '***') {
      res.censoredText = censorProfanity(
        text,
        mask,
        this.customProfanity.length ? { customTerms: this.customProfanity } : undefined
      );
    }
    return res;
  }

  reply(
    text: string,
    options?: {
      vary?: boolean;
      strategy?: DialogueStrategy;
      persona?: DialoguePersona;
      script?: DialogueScript;
    }
  ): DialogueResponse {
    return respondToDarja(text, {
      persona: options?.persona || this.persona,
      script: options?.script || this.script,
      strategy: options?.strategy || this.dialogueStrategy,
      vary: options?.vary ?? false,
      customRules: this.customRules.length ? this.customRules : undefined,
    });
  }

  buildPrompt(text: string): string {
    const ctx = buildAgentContext(text, this.storeName);
    return formatAgentSystemPrompt(ctx);
  }

  analyze(
    text: string,
    options?: { tasks?: AnalysisTask[]; includeReply?: boolean }
  ): AnalysisReport {
    const active = new Set<AnalysisTask>(options?.tasks || ALL_TASKS);
    if (options?.includeReply === false && !options?.tasks) {
      active.delete('reply');
    }

    const hasPos = Object.keys(this.customPositive).length > 0;
    const hasNeg = Object.keys(this.customNegative).length > 0;

    return {
      rawText: text,
      normalized: active.has('normalize') ? normalize(text) : null,
      arabic: active.has('arabizi')
        ? arabiziToArabic(text, { preserveFrench: this.preserveFrench })
        : null,
      cleaned: active.has('clean') ? this.clean(text) : null,
      sentiment: active.has('sentiment')
        ? analyzeSentiment(text, {
            mode: this.sentimentMode,
            customPositive: hasPos ? this.customPositive : undefined,
            customNegative: hasNeg ? this.customNegative : undefined,
          })
        : null,
      intent: active.has('intent') ? identifyIntent(text) : null,
      dialect: active.has('dialect') ? detectDialect(text) : null,
      entities: active.has('entities') ? extractEntities(text) : null,
      escalation: active.has('escalation') ? detectEscalation(text) : null,
      profanity: active.has('profanity')
        ? detectProfanity(
            text,
            this.customProfanity.length ? { customTerms: this.customProfanity } : undefined
          )
        : null,
      cultural: active.has('cultural') ? detectCulturalReferences(text) : null,
      francoDarja: active.has('franco') ? detectFrancoDarja(text) : null,
      reply: active.has('reply') ? this.reply(text) : null,
    };
  }

  analyzeBatch(
    texts: string[],
    options?: { tasks?: AnalysisTask[]; includeReply?: boolean }
  ): AnalysisReport[] {
    return texts.map((t) => this.analyze(t, options));
  }
}

let defaultPipeline: DarjaPipeline | null = null;

export function analyze(text: string, options?: AnalyzeOptions): AnalysisReport {
  const persona = options?.persona || 'casual';
  const sentimentMode = options?.sentimentMode || 'hybrid';
  if (persona === 'casual' && sentimentMode === 'hybrid') {
    if (!defaultPipeline) {
      defaultPipeline = new DarjaPipeline();
    }
    return defaultPipeline.analyze(text, {
      tasks: options?.tasks,
      includeReply: options?.includeReply,
    });
  }
  return new DarjaPipeline({ persona, sentimentMode }).analyze(text, {
    tasks: options?.tasks,
    includeReply: options?.includeReply,
  });
}
