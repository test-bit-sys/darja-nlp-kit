import { normalize } from './normalizer';
import { arabiziToArabic } from './arabizi';
import { analyzeSentiment } from './sentiment';
import { extractEntities } from './entities';
import { detectDialect } from './dialect';
import { identifyIntent } from './intent';
import { detectEscalation } from './escalation';
import { detectCulturalReferences } from './cultural';
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
