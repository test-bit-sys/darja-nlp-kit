import { normalize } from './normalizer';
import { arabiziToArabic } from './arabizi';
import { analyzeSentiment } from './sentiment';
import { extractEntities } from './entities';
import { detectDialect } from './dialect';
import { DialectRegion, SentimentLabel } from './types';

export interface AgentContext {
  storeName: string;
  rawMessage: string;
  arabicTransliterated: string;
  normalized: string;
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
  };
}

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

  const dialect = detectDialect(rawMessage);
  const sentiment = analyzeSentiment(rawMessage);
  const entities = extractEntities(rawMessage);

  let tone = 'PROFESSIONAL_HELPFUL';
  let toneInstruction = '🤝 الزبون يستفسر. أجب بوضوح وسرعة ومهنية جزائرية عفوية.';

  if (sentiment.label === 'NEGATIVE') {
    tone = 'APOLOGETIC_AND_REASSURING';
    toneInstruction = '⚠️ الزبون غاضب أو يشتكي! ابدأ بتطييب الخاطر والاعتذار (\'حقك علينا خويا، ما تقلقش، المشكل نحلوه درك\'). تجنب الجفاف والردود الآلية.';
  } else if (sentiment.label === 'POSITIVE') {
    tone = 'WARM_AND_CELEBRATING';
    toneInstruction = '😊 الزبون مسرور وراضٍ. رد بابتماس وترحاب حار (\'ربي يحفظك، شهادة نعتزوا بيها، سلعة لوز لزبائننا\').';
  }

  const wilayasSummary = entities.wilayas.map((w) => `${w.nameAr} (${w.codeStr})`);
  const paymentsSummary = entities.payments.map((p) => p.label);
  const pricesSummary = entities.prices
    .filter((p) => p.amount !== null)
    .map((p) => `${p.amount?.toLocaleString()} دج (${p.raw})`);
  const deliveriesSummary = (entities.deliveries || []).map((d) => d.label);
  const deliveryModeSummary = entities.deliveryMode?.label || null;
  const phonesSummary = (entities.phones || []).map((ph) => ph.normalized);

  return {
    storeName,
    rawMessage,
    arabicTransliterated: arabicTrans,
    normalized,
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
    },
  };
}

export function formatAgentSystemPrompt(context: AgentContext): string {
  const store = context.storeName || 'المتجر';
  const dialect = context.dialect;
  const sentiment = context.sentiment;
  const facts = context.groundedFacts;

  return `أنت مساعد خدمة عملاء ذكي وبشري جداً لمتجر إلكتروني جزائري '${store}'.
مهمتك الرد على الزبون الجزائري بدارجة واقعية ومتقنة 100%، كأنك تاجر جزائري محترف ولطيف.

[السياق المستخرج من رسالة الزبون]:
- الرسالة: "${context.rawMessage}"
- الترجمة التفسيرية (إذا كانت عربيزي): "${context.arabicTransliterated}"
- المنطقة الجغرافية للهجة: ${dialect.region} (${dialect.guideline})
- حالة الزبون النفسية: ${sentiment.label} (الدرجة: ${sentiment.score})
- إرشادات النبرة: ${sentiment.toneInstruction}
- الولايات المؤكدة: ${facts.wilayas.length > 0 ? facts.wilayas.join(', ') : 'غير محددة'}
- المبالغ المذكورة بالدينار: ${facts.pricesDzd.length > 0 ? facts.pricesDzd.join(', ') : 'غير محددة'}
- وسائل الدفع المرصودة: ${facts.payments.length > 0 ? facts.payments.join(', ') : 'غير محددة'}
- شركات التوصيل: ${facts.deliveryCompanies.length > 0 ? facts.deliveryCompanies.join(', ') : 'غير محددة'}
- نمط التوصيل: ${facts.deliveryMode || 'غير محدد'}
- أرقام الهاتف: ${facts.phones.length > 0 ? facts.phones.join(', ') : 'غير متوفرة'}

[قواعد صارمة للرد]:
1. تحدث بدارجة جزائرية عفوية ومحترمة (لا تستخدم فصحى معربة أو لهجات مشرقية إطلاقاً).
2. طابق نبرة ولهجة الزبون (${dialect.region}) لتبني الثقة والقرب.
3. التزم بالحقائق المستخرجة أعلاه (خاصة الأسعار بالدينار والولايات) دون أي هلوسة.
4. اجعل الرد مختصراً وبشرياً (1 إلى 3 أسطر).
`;
}
