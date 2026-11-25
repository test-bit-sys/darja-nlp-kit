import { normalize } from './normalizer';
import { arabiziToArabic } from './arabizi';
import { analyzeSentiment } from './sentiment';
import { extractEntities, getWilayaByCode } from './entities';
import { detectDialect } from './dialect';
import { identifyIntent } from './intent';
import { detectEscalation } from './escalation';
import { detectCulturalReferences } from './cultural';
import { respondToDarja, DialoguePersona } from './dialogue';
import { detectProfanity, censorProfanity } from './profanity';
import { DarjaChat, ChatSlots } from './chat';
import { CulturalAnalysisResult, DialectRegion, EscalationResult, IntentType, SentimentLabel } from './types';
import * as path from 'path';
import * as fs from 'fs';

export interface DialogueExample {
  id: string;
  region: DialectRegion;
  intent: string;
  customerMessage: string;
  merchantResponse: string;
}

export interface AgentContext {
  storeName: string;
  rawMessage: string;
  arabicTransliterated: string;
  normalized: string;
  intent: {
    intent: IntentType;
    confidence: number;
    matchedKeywords: string[];
    guideline: string;
  };
  escalation: EscalationResult;
  dialect: {
    region: DialectRegion;
    confidence: number;
    detectedMarkers: string[];
    guideline: string;
  };
  sentiment: {
    label: SentimentLabel;
    score: number;
    tone: string;
    toneInstruction: string;
  };
  groundedFacts: {
    wilayas: string[];
    payments: string[];
    pricesDzd: string[];
    deliveryCompanies: string[];
    deliveryMode: string | null;
    phones: string[];
    quantities: string[];
    productAttributes: { colors: string[]; sizes: string[] };
  };
  fewShotExamples?: DialogueExample[];
  cultural?: CulturalAnalysisResult;
}

let _dialoguesCache: any[] | null = null;

function loadDialogues(): any[] {
  if (_dialoguesCache) {
    return _dialoguesCache;
  }
  try {
    const dataPath = path.join(__dirname, '..', 'data', 'dialogues.json');
    if (fs.existsSync(dataPath)) {
      const raw = fs.readFileSync(dataPath, 'utf-8');
      _dialoguesCache = JSON.parse(raw);
      return _dialoguesCache || [];
    }
  } catch {
    // fallback
  }
  _dialoguesCache = [];
  return _dialoguesCache;
}

export function getFewShotDialogues(
  region: DialectRegion = 'GENERAL_DARJA',
  intent?: string,
  limit = 2
): DialogueExample[] {
  const allDialogues = loadDialogues();
  if (!allDialogues || allDialogues.length === 0) {
    return [];
  }

  const regionUpper = (region || 'GENERAL_DARJA').toUpperCase();
  let regional = allDialogues.filter((d: any) => (d.region || '').toUpperCase() === regionUpper);
  if (regional.length === 0) {
    regional = allDialogues.filter((d: any) => (d.region || '').toUpperCase() === 'GENERAL_DARJA');
  }

  const selected: any[] = [];
  if (intent && intent.toUpperCase() !== 'UNKNOWN') {
    const intentUpper = intent.toUpperCase();
    const matchingIntent = regional.filter((d: any) => (d.intent || '').toUpperCase() === intentUpper);
    selected.push(...matchingIntent.slice(0, limit));
  }

  for (const d of regional) {
    if (selected.length >= limit) break;
    if (!selected.includes(d)) {
      selected.push(d);
    }
  }

  if (selected.length < limit) {
    for (const d of allDialogues) {
      if (selected.length >= limit) break;
      if (!selected.includes(d)) {
        selected.push(d);
      }
    }
  }

  return selected.slice(0, limit).map((d: any) => ({
    id: d.id,
    region: d.region,
    intent: d.intent,
    customerMessage: d.customer_message || d.customerMessage,
    merchantResponse: d.merchant_response || d.merchantResponse,
  }));
}

const INTENT_GUIDELINES: Record<IntentType, string> = {
  ORDER: '🛒 نية الزبون: طلب شراء/حجز. اطلب منه تأكيد الاسم، الولاية/البلدية، ورقم الهاتف لتسجيل طلبيته فورا.',
  PRICE_INQUIRY: '💰 نية الزبون: استفسار عن السعر. أعطه السعر بالدينار الجزائري مع توضيح مصاريف التوصيل.',
  AVAILABILITY_INQUIRY: '📦 نية الزبون: توفر السلعة. أكد التوفر وحفزه على الطلب فورا.',
  DELIVERY_INQUIRY: '🚚 نية الزبون: التوصيل والشحن. وضح سعر ومدة التوصيل لولايته (خدمة سريعة للدار أو المكتب).',
  COMPLAINT: '⚠️ نية الزبون: شكوى أو استرجاع. استوعب غضب الزبون بلطف واعتذر وقم بحل الإشكال باحترافية.',
  GREETING: '👋 نية الزبون: تحية وتواصل. رد بترحيب جزائري عفوي ومستعد للخدمة.',
  UNKNOWN: 'استفسار عام. قدم المساعدة بطريقة واضحة ومباشرة.',
};

const DIALECT_GUIDELINES: Record<DialectRegion, string> = {
  WEST: 'لهجة الغرب الجزائري (وهران وتلمسان): استعمل كلمات خفيفة مثل (درك، غايا، مرحبا بيك خويا، ما تقلقش روحك).',
  EAST: 'لهجة الشرق الجزائري (قسنطينة وسطيف وعنابة): استعمل كلمات دافئة مثل (عيشك، ضرك، وشبيك، على عيني، ما كاش مشكل).',
  CENTER: 'لهجة الوسط والعاصمة (الجزائر والبليدة): استعمل أسلوب العاصمة السلس (واش خويا، مرحبا بيك، رانا هنا، كاش ما تسحق).',
  SOUTH: 'لهجة الجنوب الجزائري الكريمة: استعمل كلمات الترحيب والأصالة (مرحبا بيك، ربي يحفظك، على راسنا وعينينا).',
  GENERAL_DARJA: 'دارجة جزائرية عامة ومفهومة ومحترمة تجمع بين العفوية واللباقة المهنية.',
};

export function buildAgentContext(message: string, storeName = 'Bazar El Djazair'): AgentContext {
  const rawMessage = message || '';
  const arabicTrans = arabiziToArabic(rawMessage);
  const normalized = normalize(rawMessage);

  const intent = identifyIntent(rawMessage);
  const escalation = detectEscalation(rawMessage);
  const dialect = detectDialect(rawMessage);
  const sentiment = analyzeSentiment(rawMessage);
  const entities = extractEntities(rawMessage);
  const cultural = detectCulturalReferences(rawMessage);

  let tone = 'PROFESSIONAL_HELPFUL';
  let toneInstruction = '🤝 الزبون يستفسر. أجب بوضوح وسرعة ومهنية جزائرية عفوية.';

  if (escalation.needsEscalation) {
    tone = 'CRITICAL_ESCALATION';
    toneInstruction = `🚨 تصعيد فوري: ${escalation.guideline}`;
  } else if (sentiment.label === 'NEGATIVE') {
    tone = 'APOLOGETIC_AND_REASSURING';
    toneInstruction = '⚠️ الزبون غاضب أو يشتكي! ابدأ بتطييب الخاطر والاعتذار (\'حقك علينا خويا، ما تقلقش، المشكل نحلوه درك\'). تجنب الجفاف والردود الآلية.';
  } else if (sentiment.label === 'POSITIVE') {
    tone = 'WARM_AND_CELEBRATING';
    toneInstruction = '😊 الزبون مسرور وراضٍ. رد بابتماس وترحاب حار (\'ربي يحفظك، شهادة نعتزوا بيها، سلعة لوز لزبائننا\').';
  }

  const wilayasSummary = entities.wilayas.map((w) => {
    const communeInfo = w.commune ? ` - بلدية ${w.commune}` : '';
    return `${w.nameAr} (${w.codeStr})${communeInfo}`;
  });
  const paymentsSummary = entities.payments.map((p) => p.label);
  const pricesSummary = entities.prices
    .filter((p) => p.amount !== null)
    .map((p) => `${p.amount?.toLocaleString()} دج (${p.raw})`);
  const deliveriesSummary = (entities.deliveries || []).map((d) => d.label);
  const deliveryModeSummary = entities.deliveryMode?.label || null;
  const phonesSummary = (entities.phones || []).map((ph) => {
    const op = ph.operatorLabel ? ` (${ph.operatorLabel})` : '';
    return `${ph.normalized}${op}`;
  });
  const quantitiesSummary = (entities.quantities || []).map((q) => `${q.value} ${q.unit} (${q.raw})`);
  const productAttributesSummary = {
    colors: entities.attributes?.colors || [],
    sizes: entities.attributes?.sizes || [],
  };

  return {
    storeName,
    rawMessage,
    arabicTransliterated: arabicTrans,
    normalized,
    intent: {
      intent: intent.intent,
      confidence: intent.confidence,
      matchedKeywords: intent.matchedKeywords,
      guideline: INTENT_GUIDELINES[intent.intent] || INTENT_GUIDELINES.UNKNOWN,
    },
    escalation,
    dialect: {
      region: dialect.region,
      confidence: dialect.confidence,
      detectedMarkers: dialect.detectedMarkers,
      guideline: DIALECT_GUIDELINES[dialect.region] || DIALECT_GUIDELINES.GENERAL_DARJA,
    },
    sentiment: {
      label: sentiment.label,
      score: sentiment.score,
      tone,
      toneInstruction,
    },
    groundedFacts: {
      wilayas: wilayasSummary,
      payments: paymentsSummary,
      pricesDzd: pricesSummary,
      deliveryCompanies: deliveriesSummary,
      deliveryMode: deliveryModeSummary,
      phones: phonesSummary,
      quantities: quantitiesSummary,
      productAttributes: productAttributesSummary,
    },
    fewShotExamples: getFewShotDialogues(dialect.region, intent.intent, 2),
    cultural,
  };
}

export function formatAgentSystemPrompt(context: AgentContext): string {
  const store = context.storeName || 'المتجر';
  const intent = context.intent;
  const escalation = context.escalation;
  const dialect = context.dialect;
  const sentiment = context.sentiment;
  const facts = context.groundedFacts;

  const escalationNotice = escalation.needsEscalation
    ? `\n🚨 [تنبيه تصعيد عاجل - Escalation Triggered]:\n- السبب: ${escalation.reason} (درجة الإلحاح: ${escalation.urgency})\n- الإجراء: ${escalation.guideline}\n`
    : '';

  const quantitiesStr = facts.quantities.length > 0 ? facts.quantities.join(', ') : 'غير محددة';
  const colorsStr = facts.productAttributes.colors.length > 0 ? facts.productAttributes.colors.join(', ') : 'غير محدد';
  const sizesStr = facts.productAttributes.sizes.length > 0 ? facts.productAttributes.sizes.join(', ') : 'غير محدد';

  const fewShots = context.fewShotExamples || [];
  let fewShotsSection = '';
  if (fewShots.length > 0) {
    fewShotsSection = '\n[أمثلة واقعية لنبرة الرد بالدارجة الجزائرية المستهدفة]:\n';
    fewShots.forEach((ex, idx) => {
      fewShotsSection += `${idx + 1}. رسالة الزبون: "${ex.customerMessage}"\n   رد التاجر الطبيعي: "${ex.merchantResponse}"\n`;
    });
  }

  let culturalSection = '';
  if (context.cultural?.hasCulturalReference) {
    culturalSection = `\n[إشارات ثقافية وشعبية مرصودة في رسالة الزبون]:\n- الدلالات الشعبية: ${context.cultural.culturalSummary}\n👉 إرشاد الرد: أظهر فهماً ذكياً وتفاعلاً طيباً مع المثل الشعبي أو الأكلة أو المعلم المذكور بروح جزائرية أصيلة.\n`;
  }

  return `أنت مساعد خدمة عملاء ذكي وبشري جداً لمتجر إلكتروني جزائري '${store}'.
مهمتك الرد على الزبون الجزائري بدارجة واقعية ومتقنة 100%، كأنك تاجر جزائري محترف ولطيف.${escalationNotice}
[السياق المستخرج من رسالة الزبون]:
- الرسالة: "${context.rawMessage}"
- الترجمة التفسيرية (إذا كانت عربيزي): "${context.arabicTransliterated}"
- النية الأساسية (Intent): ${intent.intent} (${intent.guideline})
- المنطقة الجغرافية للهجة: ${dialect.region} (${dialect.guideline})
- حالة الزبون النفسية: ${sentiment.label} (الدرجة: ${sentiment.score})
- إرشادات النبرة: ${sentiment.toneInstruction}
- الولايات والبلديات: ${facts.wilayas.length > 0 ? facts.wilayas.join(', ') : 'غير محددة'}
- الكمية المطلوبة: ${quantitiesStr}
- مواصفات المنتج (ألوان/مقاسات): ألوان: ${colorsStr} | مقاسات: ${sizesStr}
- المبالغ المذكورة بالدينار: ${facts.pricesDzd.length > 0 ? facts.pricesDzd.join(', ') : 'غير محددة'}
- وسائل الدفع المرصودة: ${facts.payments.length > 0 ? facts.payments.join(', ') : 'غير محددة'}
- شركات التوصيل: ${facts.deliveryCompanies.length > 0 ? facts.deliveryCompanies.join(', ') : 'غير محددة'}
- نمط التوصيل: ${facts.deliveryMode || 'غير محدد'}
- أرقام الهاتف: ${facts.phones.length > 0 ? facts.phones.join(', ') : 'غير متوفرة'}
${culturalSection}
${fewShotsSection}
[قواعد صارمة للرد]:
1. تحدث بدارجة جزائرية عفوية ومحترمة (لا تستخدم فصحى معربة أو لهجات مشرقية إطلاقاً).
2. طابق نبرة ولهجة الزبون (${dialect.region}) لتبني الثقة والقرب.
3. التزم بالحقائق المستخرجة أعلاه (خاصة الأسعار بالدينار والولايات) دون أي هلوسة.
4. اجعل الرد مختصراً وبشرياً (1 إلى 3 أسطر).
`;
}

export function getOpenAiToolDefinitions(): Array<Record<string, unknown>> {
  return [
    {
      type: 'function',
      function: {
        name: 'parse_algerian_message',
        description: 'Parse and extract Algerian entities (Wilayas, colloquial prices in DZD, payments, carriers, phones with telecom operator, quantities, product attributes) and dialect from customer text.',
        parameters: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: "The customer's message in Arabic, Arabizi, or French code-switching.",
            },
          },
          required: ['text'],
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'get_wilaya_details',
        description: 'Get official Algerian Wilaya information (Arabic/French name, postal code 01-69, region).',
        parameters: {
          type: 'object',
          properties: {
            code: {
              type: 'integer',
              description: 'The wilaya numeric code (1 to 69).',
            },
          },
          required: ['code'],
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'check_human_escalation',
        description: 'Detect if customer is furious, making legal threats, or explicitly asking for a human agent.',
        parameters: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: "The customer's message text.",
            },
          },
          required: ['text'],
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'detect_cultural_references',
        description: 'Detect Algerian cultural references, proverbs, viral memes, landmarks, gastronomy, and slang in customer text.',
        parameters: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: "The customer's message text in Arabic or Arabizi.",
            },
          },
          required: ['text'],
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'respond_to_darja',
        description: "Generate an authentic Algerian colloquial response (supporting 'wach ya khoy' -> 'we cv', greetings, and order inquiries).",
        parameters: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'The customer message to reply to.',
            },
            persona: {
              type: 'string',
              enum: ['casual', 'merchant', 'assistant'],
              description: 'Persona tone of the reply.',
            },
          },
          required: ['text'],
        },
      },
    },
    {
      type: 'function',
      function: {
        name: 'moderate_darja_text',
        description: 'Check text for Algerian profanity, vulgar expressions, slurs, and toxic language in Arabic script and Arabizi.',
        parameters: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'The message to check and sanitize.',
            },
          },
          required: ['text'],
        },
      },
    },
  ];
}

export const LLM_PROVIDERS: Record<string, { baseUrl: string; defaultModel: string }> = {
  openai: { baseUrl: 'https://api.openai.com/v1', defaultModel: 'gpt-4o-mini' },
  gemini: { baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai', defaultModel: 'gemini-2.5-flash' },
  groq: { baseUrl: 'https://api.groq.com/openai/v1', defaultModel: 'llama-3.3-70b-versatile' },
  deepseek: { baseUrl: 'https://api.deepseek.com/v1', defaultModel: 'deepseek-chat' },
  openrouter: { baseUrl: 'https://openrouter.ai/api/v1', defaultModel: 'meta-llama/llama-3.3-70b-instruct' },
  ollama: { baseUrl: 'http://127.0.0.1:11434/v1', defaultModel: 'qwen2.5:7b' },
};

export function executeAgentTool(name: string, args: Record<string, any> = {}): Record<string, any> {
  if (name === 'parse_algerian_message') {
    const text = String(args.text || '');
    const ent = extractEntities(text);
    const dia = detectDialect(text);
    return {
      dialect: { region: dia.region, confidence: dia.confidence, markers: dia.detectedMarkers },
      wilayas: ent.wilayas.map((w) => ({
        code: w.code,
        name_ar: w.nameAr,
        name_fr: w.nameFr,
        commune: w.commune ?? null,
      })),
      prices_dzd: ent.prices.filter((p) => p.amount !== null).map((p) => ({ amount: p.amount, raw: p.raw })),
      payments: ent.payments.map((p) => p.type),
      deliveries: (ent.deliveries || []).map((d) => d.company),
      delivery_mode: ent.deliveryMode ? ent.deliveryMode.mode : null,
      phones: (ent.phones || []).map((ph) => ({
        normalized: ph.normalized,
        operator: ph.operator ?? null,
        whatsapp_url: ph.whatsappUrl ?? null,
      })),
      quantities: (ent.quantities || []).map((q) => ({ value: q.value, unit: q.unit, raw: q.raw })),
      attributes: ent.attributes || { colors: [], sizes: [] },
    };
  }

  if (name === 'get_wilaya_details') {
    const code = parseInt(String(args.code ?? '0'), 10) || 0;
    const w = getWilayaByCode(code);
    return w ? (w as unknown as Record<string, any>) : { error: `Wilaya code ${code} not found (valid range: 1..69)` };
  }

  if (name === 'check_human_escalation') {
    const text = String(args.text || '');
    const esc = detectEscalation(text);
    return {
      needs_escalation: esc.needsEscalation,
      reason: esc.reason,
      urgency: esc.urgency,
      matched_triggers: esc.matchedTriggers,
      guideline: esc.guideline,
    };
  }

  if (name === 'detect_cultural_references') {
    const text = String(args.text || '');
    const cult = detectCulturalReferences(text);
    return {
      has_cultural_reference: cult.hasCulturalReference,
      cultural_summary: cult.culturalSummary,
      proverbs: cult.proverbs.map((p) => p.canonicalName),
      memes_and_trends: cult.memesAndTrends.map((m) => m.canonicalName),
      landmarks: cult.landmarks.map((lm) => lm.canonicalName),
      gastronomy: cult.gastronomy.map((g) => g.canonicalName),
      slang_expressions: cult.slangExpressions.map((s) => s.canonicalName),
    };
  }

  if (name === 'respond_to_darja') {
    const text = String(args.text || '');
    const persona = (args.persona || 'casual') as DialoguePersona;
    return respondToDarja(text, { persona }) as unknown as Record<string, any>;
  }

  if (name === 'moderate_darja_text') {
    const text = String(args.text || '');
    const prof = detectProfanity(text);
    return {
      is_profane: prof.isProfane,
      severity: prof.severity,
      matches: prof.matches.map((m) => ({ term: m.term, category: m.category, severity: m.severity })),
      censored_text: censorProfanity(text),
    };
  }

  if (name === 'analyze_darja_message') {
    const { analyze } = require('./pipeline');
    const text = String(args.text || '');
    return analyze(text, {
      persona: (args.persona || 'merchant') as DialoguePersona,
      sentimentMode: args.sentiment_mode || 'hybrid',
    });
  }

  if (name === 'build_agent_prompt') {
    const text = String(args.text || '');
    const store = String(args.store_name || 'Bazar El Djazair');
    const ctx = buildAgentContext(text, store);
    return { context: ctx, system_prompt: formatAgentSystemPrompt(ctx) };
  }

  return { error: `Unknown darja-nlp tool: ${name}` };
}

export function getMcpToolDefinitions(): Array<Record<string, any>> {
  const mcpTools = getOpenAiToolDefinitions().map((item: any) => ({
    name: item.function.name,
    description: item.function.description,
    inputSchema: item.function.parameters,
  }));
  mcpTools.push(
    {
      name: 'analyze_darja_message',
      description: 'Run complete unified Algerian Darja analysis (sentiment, intent, dialect, entities, moderation, cultural references, and grounded reply).',
      inputSchema: {
        type: 'object',
        properties: {
          text: { type: 'string', description: 'Algerian Darja, Arabic, or Arabizi text.' },
          persona: { type: 'string', enum: ['casual', 'merchant', 'assistant'], description: 'Response persona.' },
          sentiment_mode: { type: 'string', enum: ['hybrid', 'ml', 'lexicon'], description: 'Sentiment engine mode.' },
        },
        required: ['text'],
      },
    },
    {
      name: 'build_agent_prompt',
      description: 'Extract structured grounded facts and generate an anti-hallucination Algerian Darja system prompt for an LLM.',
      inputSchema: {
        type: 'object',
        properties: {
          text: { type: 'string', description: 'Customer message.' },
          store_name: { type: 'string', description: 'Optional store name.' },
        },
        required: ['text'],
      },
    }
  );
  return mcpTools;
}

export interface AgentOptions {
  storeName?: string;
  persona?: DialoguePersona;
  provider?: string;
  apiKey?: string;
  model?: string;
  baseUrl?: string;
  timeoutMs?: number;
}

export interface AgentReply {
  reply: string;
  provider: string;
  model: string;
  intent: string;
  dialect: DialectRegion;
  needsEscalation: boolean;
  slots: ChatSlots;
  readyToConfirm: boolean;
  missingSlots: string[];
  context: AgentContext;
  toolCallsExecuted: string[];
}

export class DarjaAIAgent {
  public storeName: string;
  public persona: DialoguePersona;
  public provider: string;
  public apiKey?: string;
  public baseUrl: string;
  public model: string;
  public timeoutMs: number;
  public chatSession: DarjaChat;
  public conversationHistory: Array<Record<string, any>> = [];

  constructor(options?: AgentOptions) {
    this.storeName = options?.storeName ?? 'Bazar El Djazair';
    this.persona = options?.persona ?? 'merchant';
    this.apiKey = options?.apiKey || process.env.DARJA_API_KEY || process.env.OPENAI_API_KEY;
    if (options?.provider) {
      this.provider = options.provider.toLowerCase();
    } else if (this.apiKey || options?.baseUrl) {
      this.provider = 'openai';
    } else {
      this.provider = 'offline';
    }

    const cfg = LLM_PROVIDERS[this.provider] || {};
    this.baseUrl = (options?.baseUrl || cfg.baseUrl || '').replace(/\/+$/, '');
    this.model = options?.model || cfg.defaultModel || 'local-darja-rules';
    this.timeoutMs = options?.timeoutMs ?? 30000;
    this.chatSession = new DarjaChat({ storeName: this.storeName, persona: this.persona });
  }

  get slots(): ChatSlots {
    return this.chatSession.slots;
  }

  reset(): void {
    this.chatSession.reset();
    this.conversationHistory = [];
  }

  askOffline(message: string): AgentReply {
    const turn = this.chatSession.send(message);
    const ctx = buildAgentContext(message, this.storeName);
    this.conversationHistory.push({ role: 'user', content: message });
    this.conversationHistory.push({ role: 'assistant', content: turn.reply });
    return {
      reply: turn.reply,
      provider: 'offline',
      model: 'offline-darja-kb',
      intent: turn.intent,
      dialect: turn.dialect,
      needsEscalation: turn.escalation.needsEscalation,
      slots: turn.extractedSlots,
      readyToConfirm: turn.readyToConfirm,
      missingSlots: turn.missingSlots,
      context: ctx,
      toolCallsExecuted: [],
    };
  }

  async ask(message: string): Promise<AgentReply> {
    if (this.provider === 'offline') {
      return this.askOffline(message);
    }
    const turn = this.chatSession.send(message);
    const ctx = buildAgentContext(message, this.storeName);
    if (turn.escalation.needsEscalation) {
      return {
        reply: turn.reply,
        provider: 'offline',
        model: 'offline-darja-kb',
        intent: turn.intent,
        dialect: turn.dialect,
        needsEscalation: true,
        slots: turn.extractedSlots,
        readyToConfirm: turn.readyToConfirm,
        missingSlots: turn.missingSlots,
        context: ctx,
        toolCallsExecuted: [],
      };
    }
    if (this.provider !== 'ollama' && !this.apiKey) {
      throw new Error(`API key is required for provider '${this.provider}'. Set apiKey or DARJA_API_KEY, or use provider='offline'.`);
    }

    const systemPrompt = formatAgentSystemPrompt(ctx);
    const messages: Array<Record<string, any>> = [
      { role: 'system', content: systemPrompt },
      ...this.conversationHistory.slice(-8),
      { role: 'user', content: message },
    ];
    const tools = getOpenAiToolDefinitions();
    const executed: string[] = [];

    for (let hop = 0; hop < 3; hop++) {
      const resp = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.apiKey || 'ollama'}`,
        },
        body: JSON.stringify({ model: this.model, messages, tools, tool_choice: 'auto', temperature: 0.4 }),
        signal: AbortSignal.timeout(this.timeoutMs),
      });
      if (!resp.ok) {
        throw new Error(`LLM HTTP ${resp.status}: ${await resp.text()}`);
      }
      const data: any = await resp.json();
      const msg = data.choices?.[0]?.message || {};
      const toolCalls = msg.tool_calls || [];
      if (!toolCalls.length) {
        const replyText = String(msg.content || '').trim();
        this.conversationHistory.push({ role: 'user', content: message });
        this.conversationHistory.push({ role: 'assistant', content: replyText });
        return {
          reply: replyText,
          provider: this.provider,
          model: this.model,
          intent: turn.intent,
          dialect: turn.dialect,
          needsEscalation: false,
          slots: turn.extractedSlots,
          readyToConfirm: turn.readyToConfirm,
          missingSlots: turn.missingSlots,
          context: ctx,
          toolCallsExecuted: executed,
        };
      }

      messages.push(msg);
      for (const tc of toolCalls) {
        const tName = tc.function?.name || '';
        let tArgs: Record<string, any> = {};
        try {
          tArgs = JSON.parse(tc.function?.arguments || '{}');
        } catch {
          tArgs = {};
        }
        const tRes = executeAgentTool(tName, tArgs);
        executed.push(tName);
        messages.push({ role: 'tool', tool_call_id: tc.id || tName, content: JSON.stringify(tRes) });
      }
    }

    return this.askOffline(message);
  }

  static getMcpConfig(runtime: 'python' | 'node' = 'python'): Record<string, any> {
    if (runtime === 'node') {
      return { mcpServers: { 'darja-nlp': { command: 'npx', args: ['-y', '@dz-open-suite/darja-nlp-kit', 'mcp'] } } };
    }
    return { mcpServers: { 'darja-nlp': { command: 'python', args: ['-m', 'darja_nlp.cli', 'mcp'] } } };
  }
}
