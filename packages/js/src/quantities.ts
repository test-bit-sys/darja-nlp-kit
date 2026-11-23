export interface QuantityEntity {
  raw: string;
  value: number;
  unit: string;
}

export interface ProductAttributes {
  colors: string[];
  sizes: string[];
}

const UNIT_NUMBER_WORDS: Record<string, number> = {
  'زوج': 2,
  'تلات': 3,
  'تلاتة': 3,
  'ربع': 4,
  'ربعة': 4,
  'خمس': 5,
  'خمسة': 5,
  'ست': 6,
  'ستة': 6,
  'سبع': 7,
  'سبعة': 7,
  'تمن': 8,
  'تمنية': 8,
  'تسع': 9,
  'تسعة': 9,
  'عشر': 10,
  'عشرة': 10,
  'zouj': 2,
  'zoudj': 2,
  'tlata': 3,
  'tleta': 3,
  'rab3a': 4,
  'khamsa': 5,
  'setta': 6,
  'seb3a': 7,
  'tmenya': 8,
  'tes3a': 9,
  '3achra': 10,
};

const FIXED_QUANTITY_PATTERNS: Array<{ pattern: RegExp; value: number; unit: string }> = [
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(دوزينة|دزينة|douzina|douzaine)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 12, unit: 'دوزينة' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(زوج\s*دوزينات|2\s*douzina)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 24, unit: 'دوزينة' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(حبة\s*وحدة|حبة|حبه|1\s*hba|hba|7ba)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 1, unit: 'حبة' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(شكارة|chkara|1\s*chkara)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 1, unit: 'شكارة' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(باكية|باكيه|bakya|1\s*boite|boite)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 1, unit: 'باكية' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(كرطونة|كردونة|carton|1\s*carton)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 1, unit: 'كرطونة' },
];

const NUM_WORDS_STR = 'زوج|تلات|تلاتة|ربع|ربعة|خمس|خمسة|ست|ستة|سبع|سبعة|تمن|تمنية|تسع|تسعة|عشر|عشرة|zouj|zoudj|tlata|tleta|rab3a|khamsa|setta|seb3a|tmenya|tes3a|3achra';
const UNITS_STR = 'حبات|حبة|حبه|شكاير|شكارة|باكيات|باكية|كراتن|كراطن|كرطونة|كردونة|صاشيات|صاشي|hbat|7bat|chkayer|bakyat|cartons|boites';

const DYNAMIC_QUANTITY_PATTERN = new RegExp(
  `(?:^|\\s|[^\\w\\u0600-\\u06FF])(\\d+(?:\\.\\d+)?|${NUM_WORDS_STR})\\s*(${UNITS_STR})(?=$|\\s|[^\\w\\u0600-\\u06FF])`,
  'gi',
);

const COLORS_MAP: Array<{ pattern: RegExp; label: string }> = [
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(كحل|كحلة|كحلين|noir|noire|noires|k7al|ke7la)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'كحل / noir' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بيض|بيضا|بيضاء|بيوضة|blanc|blanche|byad|bida)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بيض / blanc' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بيج|beige)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بيج / beige' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(غوج|أحمر|احمر|حمرا|حمراء|rouge|7mar|7amra)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'غوج / rouge' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(مارون|قهوي|قهوية|marron|maron|9ahwi)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'مارون / marron' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(خضر|خضرا|خضراء|vert|verte|khdar|khadra)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'خضر / vert' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(غري|رمادي|رمادية|gris|grise)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'غري / gris' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(كحلي|بلو نوي|bleu\s*nuit|bleu\s*marine)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'كحلي / bleu nuit' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بلو|أزرق|ازرق|زرقة|زرقاء|bleu|bleue|zra9)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بلو / bleu' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(دوري|ذهبي|ذهبية|dore|doré|dorée)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'دوري / doré' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(أرجونتي|ارجونتي|فضي|فضية|argente|argenté)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'ارجونتي / argenté' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(روز|وردي|وردية|rose)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'روز / rose' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(موف|بنفسجي|violet|mauve)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'موف / mauve' },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF]|و)(سيل|بلو سيل|bleu\s*ciel)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'سيل / bleu ciel' },
];

const CLOTHING_SIZES = [
  /\b(xxxl|3xl)\b/i,
  /\b(xxl|2xl)\b/i,
  /\b(xl)\b/i,
  /\b(l)\b/i,
  /\b(m)\b/i,
  /\b(s)\b/i,
  /\b(xs)\b/i,
];

const SHOE_SIZE_PATTERN = /(?:pointure|taille|مقاس|نمرة|la\s*taille|pntr)?\s*([3-4][0-9])\b/gi;

export function extractQuantities(text: string): QuantityEntity[] {
  if (!text) return [];

  const results: QuantityEntity[] = [];
  let masked = text;

  // 1. Dynamic matching
  const dynRegex = new RegExp(DYNAMIC_QUANTITY_PATTERN.source, 'gi');
  let match: RegExpExecArray | null;
  while ((match = dynRegex.exec(text)) !== null) {
    const rawNum = match[1].toLowerCase();
    const rawUnit = match[2].toLowerCase();
    const rawFull = match[0].trim();

    let val = 1;
    if (UNIT_NUMBER_WORDS[rawNum] !== undefined) {
      val = UNIT_NUMBER_WORDS[rawNum];
    } else {
      const parsed = parseFloat(rawNum.replace(',', '.'));
      val = isNaN(parsed) ? 1 : parsed;
    }

    let unitNorm = rawUnit;
    if (['حبات', 'hbat', '7bat'].includes(rawUnit)) {
      unitNorm = 'حبة';
    } else if (['شكاير', 'chkayer'].includes(rawUnit)) {
      unitNorm = 'شكارة';
    } else if (['باكيات', 'bakyat', 'boites'].includes(rawUnit)) {
      unitNorm = 'باكية';
    } else if (['كراتن', 'كراطن', 'cartons'].includes(rawUnit)) {
      unitNorm = 'كرطونة';
    } else if (['صاشيات'].includes(rawUnit)) {
      unitNorm = 'صاشي';
    }

    results.push({
      raw: rawFull,
      value: val,
      unit: unitNorm,
    });

    const start = match.index;
    const len = match[0].length;
    masked = masked.slice(0, start) + ' '.repeat(len) + masked.slice(start + len);
  }

  // 2. Fixed units
  for (const item of FIXED_QUANTITY_PATTERNS) {
    const m = masked.match(item.pattern);
    if (m) {
      results.push({
        raw: m[0].trim(),
        value: item.value,
        unit: item.unit,
      });
      const start = m.index || 0;
      const len = m[0].length;
      masked = masked.slice(0, start) + ' '.repeat(len) + masked.slice(start + len);
    }
  }

  return results;
}

export function extractProductAttributes(text: string): ProductAttributes {
  if (!text) return { colors: [], sizes: [] };

  const colors: string[] = [];
  const addedColors = new Set<string>();

  for (const item of COLORS_MAP) {
    if (item.pattern.test(text) && !addedColors.has(item.label)) {
      addedColors.add(item.label);
      colors.push(item.label);
    }
  }

  const sizes: string[] = [];
  const addedSizes = new Set<string>();

  // Shoe sizes (36 to 46)
  const shoeRegex = new RegExp(SHOE_SIZE_PATTERN.source, 'gi');
  let sMatch: RegExpExecArray | null;
  while ((sMatch = shoeRegex.exec(text)) !== null) {
    const valStr = sMatch[1];
    const num = parseInt(valStr, 10);
    if (num >= 35 && num <= 48 && !addedSizes.has(valStr)) {
      addedSizes.add(valStr);
      sizes.push(valStr);
    }
  }

  // Clothing sizes (XS to 3XL)
  for (const pat of CLOTHING_SIZES) {
    const m = text.match(pat);
    if (m) {
      const sVal = m[1].toUpperCase();
      if (!addedSizes.has(sVal)) {
        addedSizes.add(sVal);
        sizes.push(sVal);
      }
    }
  }

  return { colors, sizes };
}
