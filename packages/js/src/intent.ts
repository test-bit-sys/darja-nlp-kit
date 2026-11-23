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

const INTENT_RULES: Array<{ intent: IntentType; keywords: string[] }> = [
  {
    intent: 'COMPLAINT',
    keywords: [
      'مكسرة', 'مكسر', 'ما وصلتش', 'ما لحقتش', 'روطار', 'سلعة عيانة', 'سلعة ميتة', 'حشيتوهالي',
      'حشاوها لي', 'بدلوهالي', 'روتور', 'رجعولي دراهمي', 'ما رديتوش', 'حقار', 'سراقين', 'سرقة',
      'فضيحة', 'سلعة مفاتشة', 'ماشي كيما الفوتو', 'ماشي كيما التصويرة', 'ناقصة', 'معطوبة', 'مخدوعة',
      'reclamation', 'retour', 'casse', 'mfetcha', 'retard', 'ma wesletch', '7chawhali',
      'arnaque', 'ser9a', 'khorda', 'naqsa',
    ],
  },
  {
    intent: 'ORDER',
    keywords: [
      'كوموندي', 'نكوموندي', 'كومونديلي', 'كوموندالي', 'باغي نشري', 'راني باغي', 'باغي', 'حاب نشري',
      'حبيت نشري', 'راني حاب', 'حاب', 'حبيت', 'ابعثلي', 'ابعثهالي', 'ابعثوهالي', 'احجزلي', 'حجز', 'احجز',
      'راني شاري', 'نشريها', 'نشري', 'جيبهالي', 'حاب نطلب', 'طلب شراء', 'نحتاج حبة', 'نحتاج زوج', 'نحتاج',
      'commander', 'ncommander', 'baghi nchri', 'rani baghi', 'baghi', 'hab nchri', '7ab nchri',
      'rani hab', 'rani 7ab', 'hab', '7ab', 'habb', 'nchri', 'chrit', 'nchriha', 'nchrihoum',
      'ab3atli', 'ab3athali', 'livrili', 'livrihali', 'livreli', '7jezli', 'reserver', 'je veux acheter',
    ],
  },
  {
    intent: 'DELIVERY_INQUIRY',
    keywords: [
      'شحال التوصيل', 'كاين توصيل', 'توصلو', 'توصيل لـ', 'توصيل', 'ليفريزون', 'شحال ليفريزون',
      'وقتاش تلحق', 'وقتاش يوصل', 'شحال تاخذ وقت', 'توصلوها', 'توصيل مجاني', 'شحال فالدار',
      'livraison', 'chhal livraison', 'toussil', 'twaslou', 'we9tach tel7a9', 'wektach telhaq',
      'chhal w9t', 'livraison gratuite', 'frais de livraison', 'delai',
    ],
  },
  {
    intent: 'PRICE_INQUIRY',
    keywords: [
      'شحال', 'بشحال', 'بقداش', 'قداش', 'سومة', 'شحال السومة', 'شحال يدير', 'شحال دير',
      'شحال راها دير', 'بشحال هاذي', 'شحال تسوى', 'بري', 'بري تاعو', 'سعر', 'شحال السعر',
      'prix', 'bch7al', 'ch7al', 'bchhal', 'chhal', '9dach', 'qadach', 'souma', 'c combien',
      'combien', 'chhal ydir', 'chhal tdir', 'ch7al ydir', 'tarif',
    ],
  },
  {
    intent: 'AVAILABILITY_INQUIRY',
    keywords: [
      'كاينة', 'كاين', 'كاينين', 'متوفرة', 'متوفر', 'مازالت', 'مازال كاين', 'مازال كاينة',
      'ديسبو', 'مازالت عندكم', 'عندكم منها', 'كاش ما بقا', 'كاش جديد', 'كاين ستوك',
      'kayen', 'kayna', 'dispo', 'disponible', 'mazal', 'mazal kayn', 'mazal kayna', '3andkom',
      'fih stock',
    ],
  },
  {
    intent: 'GREETING',
    keywords: [
      'سلام', 'سلام عليكم', 'السلام عليكم', 'صباح الخير', 'مساء الخير', 'يعطيك الصحة', 'صحيت',
      'واش راك', 'كيراك', 'كيراكم', 'شراكم', 'واش خويا', 'عيشك', 'خويا لعزيز', 'ربي يحفظك',
      'salam', 'slm', 'salam alikoum', 'sbah lkhir', 'msa lkhir', 'sahit', 'kirak', 'wach rak',
      'azul', 'bonjour', 'bonsoir',
    ],
  },
];

export function identifyIntent(text: string): IntentResult {
  if (!text) {
    return { intent: 'UNKNOWN', confidence: 0, matchedKeywords: [] };
  }

  const lower = text.toLowerCase();
  const scores: Record<IntentType, string[]> = {
    COMPLAINT: [],
    ORDER: [],
    DELIVERY_INQUIRY: [],
    PRICE_INQUIRY: [],
    AVAILABILITY_INQUIRY: [],
    GREETING: [],
    UNKNOWN: [],
  };

  for (const rule of INTENT_RULES) {
    for (const kw of rule.keywords) {
      if (lower.includes(kw.toLowerCase())) {
        scores[rule.intent].push(kw);
      }
    }
  }

  // Priority order for operational/business intents:
  // COMPLAINT > ORDER > DELIVERY_INQUIRY > PRICE_INQUIRY > AVAILABILITY_INQUIRY
  const businessPriority: IntentType[] = [
    'COMPLAINT',
    'ORDER',
    'DELIVERY_INQUIRY',
    'PRICE_INQUIRY',
    'AVAILABILITY_INQUIRY',
  ];

  let bestIntent: IntentType = 'UNKNOWN';
  let bestKeywords: string[] = [];

  for (const intent of businessPriority) {
    const kws = scores[intent];
    if (kws.length > 0) {
      bestIntent = intent;
      bestKeywords = kws;
      break;
    }
  }

  // Fallback to GREETING only if no operational business intent was expressed
  if (bestIntent === 'UNKNOWN' && scores.GREETING.length > 0) {
    bestIntent = 'GREETING';
    bestKeywords = scores.GREETING;
  }

  if (bestIntent === 'UNKNOWN') {
    return { intent: 'UNKNOWN', confidence: 0, matchedKeywords: [] };
  }

  const confidence = Math.min(0.99, Math.round((0.70 + bestKeywords.length * 0.1) * 100) / 100);
  return {
    intent: bestIntent,
    confidence,
    matchedKeywords: bestKeywords,
  };
}
