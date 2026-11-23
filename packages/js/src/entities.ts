import {
  WilayaRaw,
  WilayaEntity,
  PaymentEntity,
  PriceEntity,
  DeliveryEntity,
  DeliveryModeEntity,
  PhoneEntity,
  TelecomOperator,
  EntitiesResult,
} from './types';
import { extractQuantities, extractProductAttributes } from './quantities';
import * as path from 'path';
import * as fs from 'fs';

let _wilayas: WilayaRaw[] | null = null;

export function loadWilayas(): WilayaRaw[] {
  if (_wilayas) {
    return _wilayas;
  }
  const dataPath = path.join(__dirname, '..', 'data', 'wilayas.json');
  const raw = fs.readFileSync(dataPath, 'utf-8');
  _wilayas = JSON.parse(raw) as WilayaRaw[];
  return _wilayas;
}

export function getWilayas(): WilayaRaw[] {
  return loadWilayas();
}

export function getWilayaByCode(code: number | string): WilayaRaw | undefined {
  const wilayas = loadWilayas();
  const num = typeof code === 'string' ? parseInt(code, 10) : code;
  return wilayas.find((w) => w.code === num);
}

const PAYMENT_PATTERNS = [
  {
    type: 'BARIDIMOB' as const,
    label: 'BaridiMob (بريدي موب)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(baridimob|baridi\s*mob|بريدي\s*موب|بريديموب)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    type: 'EDAHABIA' as const,
    label: 'Edahabia Card (البطاقة الذهبية)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(edahabia|dahabia|carte\s*edahabia|الذهبيه|الذهبية|بالذهبية|بالذهبيه|بطاقة\s*الذهبيه|بطاقه\s*الذهبيه|لاكارط\s*الذهبيه)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    type: 'CCP' as const,
    label: 'CCP Postal Account (حساب بريدي)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(ccp|سي\s*سي\s*بي|حساب\s*بريدي|شيك\s*بريدي|virement\s*ccp)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    type: 'COD' as const,
    label: 'Cash on Delivery (الدفع عند الاستلام)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(cod|cash\s*on\s*delivery|main\s*[aà]\s*main|الدفع\s*عند\s*الاستلام|كاش\s*عند\s*الاستلام|خلص\s*كي\s*تلحقك|كاش|يد\s*بيد)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
];

const DELIVERY_COMPANY_PATTERNS = [
  {
    company: 'YALIDINE' as const,
    label: 'Yalidine Express (ياليدين)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(yalidine|yalidin|ياليدين)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    company: 'ZR_EXPRESS' as const,
    label: 'ZR Express (زد ار اكسبرس)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(zr\s*express|zr|زد\s*ار\s*اكسبرس|زد\s*ار)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    company: 'MAYSTRO' as const,
    label: 'Maystro Delivery (مايسترو)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(maystro\s*delivery|maystro|مايسترو)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    company: 'PROCOLIS' as const,
    label: 'Procolis (بروكولي)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(procolis|pro\s*colis|بروكولي|بروكوليس)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    company: 'EMS' as const,
    label: 'EMS Algérie Poste (البريد السريع)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(ems|ems\s*algerie|البريد\s*السريع)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    company: 'KAZITOUR' as const,
    label: 'Kazitour Express (كازيتور)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(kazitour|kazi\s*tour|كازيتور)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    company: 'GUEPEX' as const,
    label: 'Guepex Express (قيباكس)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(guepex|قيباكس)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
];

const DELIVERY_MODE_PATTERNS = [
  {
    mode: 'STOP_DESK' as const,
    label: 'Stop Desk (استلام من المكتب)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(stop\s*desk|stopdesk|سطوب\s*ديسك|ستوب\s*ديسك|المكتب|فالبيرو|في\s*البيرو|agence)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
  {
    mode: 'HOME_DELIVERY' as const,
    label: 'Home Delivery (توصيل للمنزل)',
    pattern: /(?:^|\s|[^\w\u0600-\u06FF])(a\s*domicile|[aà]\s*domicile|للدار|لباب\s*الدار|توصيل\s*للمنزل|توصيل\s*للدار|فالدار)(?=$|\s|[^\w\u0600-\u06FF])/i,
  },
];

const PHONE_PATTERN =
  /(?:^|\s|[^\w\u0600-\u06FF])((?:\+213|00213|0)\s*(?:[5-7](?:[\s.-]?\d){8}|(?:2[0-9]|3[0-9]|4[0-9])(?:[\s.-]?\d){6}))(?=$|\s|[^\w\u0600-\u06FF])/g;

const DARJA_MILLIONS_WORDS: Record<string, number> = {
  زوج: 2, تلات: 3, تلاتة: 3, ربع: 4, ربعة: 4,
  خمس: 5, خمسة: 5, ست: 6, ستة: 6, سبع: 7,
  سبعة: 7, تمن: 8, تمنية: 8, تسع: 9, تسعة: 9,
  عشر: 10, عشرة: 10,
  zouj: 2, zoudj: 2, tlata: 3, tleta: 3, rab3a: 4, reb3a: 4,
  khamsa: 5, setta: 6, seb3a: 7, tmenya: 8, tes3a: 9, '3achra': 10,
};

const DARJA_THOUSANDS_WORDS: Record<string, number> = {
  مية: 100, ميتين: 200, تلمية: 300, تلتمية: 300, تلاتمية: 300,
  ربعمية: 400, خمسمية: 500, ستمية: 600, سبعمية: 700, تمنمية: 800,
  تسعمية: 900, عشرين: 20, تلاتين: 30, ربعين: 40, خمسين: 50,
  ستين: 60, سبعين: 70, تمانين: 80, تسعين: 90,
  mya: 100, myat: 100, mitin: 200, mitayn: 200, teltmya: 300,
  rab3mya: 400, khamsmya: 500, settmya: 600, seb3mya: 700,
  tmenmya: 800, tes3mya: 900, '3echrin': 20, tlatin: 30, rab3in: 40,
  khamsin: 50, settin: 60, seb3in: 70, tmanin: 80, tes3in: 90,
};

const MILLIONS_WORDS_STR = 'زوج|تلات|تلاتة|ربع|ربعة|خمس|خمسة|ست|ستة|سبع|سبعة|تمن|تمنية|تسع|تسعة|عشر|عشرة|zouj|zoudj|tlata|tleta|rab3a|reb3a|khamsa|setta|seb3a|tmenya|tes3a|3achra';
const THOUSANDS_WORDS_STR = 'مية|ميتين|تلمية|تلتمية|تلاتمية|ربعمية|خمسمية|ستمية|سبعمية|تمنمية|تسعمية|عشرين|تلاتين|ربعين|خمسين|ستين|سبعين|تمانين|تسعين|mya|myat|mitin|mitayn|teltmya|rab3mya|khamsmya|settmya|seb3mya|tmenmya|tes3mya|3echrin|tlatin|rab3in|khamsin|settin|seb3in|tmanin|tes3in';

const COMPOUND_PRICE_PATTERN = new RegExp(
  `(?:^|\\s|[^\\w\\u0600-\\u06FF])(\\d+(?:[.,]\\d+)?|${MILLIONS_WORDS_STR})?\\s*(?:ملاين|ملايين|مليون|mlyon|mlayen|mlayin)\\s*(?:و|\\+|et|w)\\s*(\\d+(?:[.,]\\d+)?|${THOUSANDS_WORDS_STR})?\\s*(?:الف|ألف|alf)(?=$|\\s|[^\\w\\u0600-\\u06FF])`,
  'gi',
);

const PRICE_NUMERIC_PATTERN = /(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(da|dzd|دج|دينار|الف|ألف|alf)(?=$|\s|[^\w\u0600-\u06FF])/gi;
const DYNAMIC_MILLIONS_PATTERN = /(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(?:ملاين|ملايين|مليون|mlyon|mlayen|mlayin)(?=$|\s|[^\w\u0600-\u06FF])/gi;
const DARJA_AMOUNTS: Array<{ pattern: RegExp; value: number }> = [
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(مية\s*الف|100\s*الف|mya|myat\s*alf)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 1000 },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(ميتين\s*الف|200\s*الف|mitin\s*alf)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 2000 },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(خمسمية\s*الف|500\s*الف|khams\s*mya|500\s*alf)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 5000 },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(مليون|mlyon|1\s*mlyon)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 10000 },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(زوج\s*ملاين|زوج\s*ملايين|zoudj\s*mlayen|zouj\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 20000 },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(خمس\s*ملاين|khams\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 50000 },
  { pattern: /(?:^|\s|[^\w\u0600-\u06FF])(عشر\s*ملاين|3achr\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])/i, value: 100000 },
];

function extractWilayas(text: string, wilayas: WilayaRaw[]): WilayaEntity[] {
  const results: WilayaEntity[] = [];
  const addedCodes = new Set<number>();
  const lowerText = text.toLowerCase();

  // 1. Direct code patterns like "wilaya 16", "w 31", "l 16", "w16"
  const codeRegex = /\b(?:wilaya|w|ولاية|ولايه|l)\s*([0-6]?[0-9])\b/gi;
  let codeMatch: RegExpExecArray | null;
  while ((codeMatch = codeRegex.exec(text)) !== null) {
    const num = parseInt(codeMatch[1], 10);
    if (num >= 1 && num <= 69 && !addedCodes.has(num)) {
      const w = wilayas.find((item) => item.code === num);
      if (w) {
        addedCodes.add(num);
        results.push({
          code: w.code,
          codeStr: w.code_str,
          nameAr: w.name_ar,
          nameFr: w.name_fr,
          matchedText: codeMatch[0],
        });
      }
    }
  }

  // 2. Name & Aliases matching
  for (const w of wilayas) {
    if (addedCodes.has(w.code)) continue;

    const candidates = [w.name_ar, w.name_fr, ...w.aliases];
    for (const cand of candidates) {
      if (!cand || cand.length < 2) continue;
      const candLower = cand.toLowerCase();

      // Check boundary match
      const escaped = candLower.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
      const reg = new RegExp(`(^|\\s|[.,!?;:()])${escaped}($|\\s|[.,!?;:()])`, 'i');

      if (reg.test(lowerText) || lowerText.includes(candLower)) {
        // Extra validation for very short words
        if (candLower.length <= 3 && !reg.test(lowerText)) {
          continue;
        }
        addedCodes.add(w.code);
        const allCommunes = [...(w.communes_sample || []), ...(w.communes_fr_sample || [])];
        const matchedCommune = allCommunes.find((c) => c.toLowerCase() === candLower) || null;
        results.push({
          code: w.code,
          codeStr: w.code_str,
          nameAr: w.name_ar,
          nameFr: w.name_fr,
          matchedText: cand,
          commune: matchedCommune,
        });
        break;
      }
    }
  }

  // 3. Major Communes matching (550+ Algerian communes)
  for (const w of wilayas) {
    if (addedCodes.has(w.code)) continue;

    const communes = [...(w.communes_sample || []), ...(w.communes_fr_sample || [])];
    for (const com of communes) {
      if (!com || com.length < 3) continue;
      const comLower = com.toLowerCase();
      const escaped = comLower.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
      const reg = new RegExp(`(^|\\s|[.,!?;:()])${escaped}($|\\s|[.,!?;:()])`, 'i');

      if (reg.test(lowerText) || (comLower.length >= 4 && lowerText.includes(comLower))) {
        addedCodes.add(w.code);
        results.push({
          code: w.code,
          codeStr: w.code_str,
          nameAr: w.name_ar,
          nameFr: w.name_fr,
          matchedText: com,
          commune: com,
        });
        break;
      }
    }
  }

  return results;
}

function extractPayments(text: string): PaymentEntity[] {
  const results: PaymentEntity[] = [];
  const addedTypes = new Set<string>();

  for (const item of PAYMENT_PATTERNS) {
    const match = text.match(item.pattern);
    if (match && !addedTypes.has(item.type)) {
      addedTypes.add(item.type);
      results.push({
        type: item.type,
        label: item.label,
        matchedText: match[0],
      });
    }
  }

  return results;
}

function extractPrices(text: string): PriceEntity[] {
  const results: PriceEntity[] = [];
  let maskedText = text;

  // 1. Compound prices (e.g., "زوج ملاين و خمسمية الف", "3 mlayen w 500 alf")
  const compRegex = new RegExp(COMPOUND_PRICE_PATTERN.source, 'gi');
  let compMatch: RegExpExecArray | null;
  while ((compMatch = compRegex.exec(text)) !== null) {
    const rawM = compMatch[1];
    const rawK = compMatch[2];
    const rawFull = compMatch[0].trim();

    let millionsVal = 1;
    if (rawM) {
      const mKey = rawM.toLowerCase();
      if (DARJA_MILLIONS_WORDS[mKey] !== undefined) {
        millionsVal = DARJA_MILLIONS_WORDS[mKey];
      } else {
        const parsed = parseFloat(mKey.replace(',', '.'));
        millionsVal = isNaN(parsed) ? 1 : parsed;
      }
    }

    let thousandsVal = 1;
    if (rawK) {
      const kKey = rawK.toLowerCase();
      if (DARJA_THOUSANDS_WORDS[kKey] !== undefined) {
        thousandsVal = DARJA_THOUSANDS_WORDS[kKey];
      } else {
        const parsed = parseFloat(kKey.replace(',', '.'));
        thousandsVal = isNaN(parsed) ? 0 : parsed;
      }
    }

    const totalDzd = (millionsVal * 10000) + (thousandsVal * 10);
    results.push({
      raw: rawFull,
      amount: totalDzd,
      currency: 'DZD',
    });

    const start = compMatch.index;
    const len = compMatch[0].length;
    maskedText = maskedText.slice(0, start) + ' '.repeat(len) + maskedText.slice(start + len);
  }

  // 2. Standard numbers with currency
  const numRegex = new RegExp(PRICE_NUMERIC_PATTERN.source, 'gi');
  let numMatch: RegExpExecArray | null;
  while ((numMatch = numRegex.exec(maskedText)) !== null) {
    const rawVal = numMatch[1].replace(',', '.');
    const unit = numMatch[2].toLowerCase();
    let val = parseFloat(rawVal);
    if (unit === 'الف' || unit === 'ألف' || unit === 'alf') {
      val = val * 1000;
    }
    results.push({
      raw: numMatch[0].trim(),
      amount: val,
      currency: 'DZD',
    });
    const start = numMatch.index;
    const len = numMatch[0].length;
    maskedText = maskedText.slice(0, start) + ' '.repeat(len) + maskedText.slice(start + len);
  }

  // 3. Dynamic colloquial millions
  const dynRegex = new RegExp(DYNAMIC_MILLIONS_PATTERN.source, 'gi');
  let dynMatch: RegExpExecArray | null;
  while ((dynMatch = dynRegex.exec(maskedText)) !== null) {
    const rawVal = dynMatch[1].replace(',', '.');
    const val = parseFloat(rawVal) * 10000;
    results.push({
      raw: dynMatch[0].trim(),
      amount: val,
      currency: 'DZD',
    });
    const start = dynMatch.index;
    const len = dynMatch[0].length;
    maskedText = maskedText.slice(0, start) + ' '.repeat(len) + maskedText.slice(start + len);
  }

  // 4. Fixed colloquial amounts
  for (const item of DARJA_AMOUNTS) {
    const match = maskedText.match(item.pattern);
    if (match) {
      results.push({
        raw: match[0].trim(),
        amount: item.value,
        currency: 'DZD',
      });
      const start = match.index || 0;
      const len = match[0].length;
      maskedText = maskedText.slice(0, start) + ' '.repeat(len) + maskedText.slice(start + len);
    }
  }

  return results;
}

function extractDeliveries(text: string): DeliveryEntity[] {
  const results: DeliveryEntity[] = [];
  const added = new Set<string>();

  for (const item of DELIVERY_COMPANY_PATTERNS) {
    const match = text.match(item.pattern);
    if (match && !added.has(item.company)) {
      added.add(item.company);
      results.push({
        company: item.company,
        label: item.label,
        matchedText: match[0].trim(),
      });
    }
  }

  return results;
}

function extractDeliveryMode(text: string): DeliveryModeEntity | null {
  for (const item of DELIVERY_MODE_PATTERNS) {
    const match = text.match(item.pattern);
    if (match) {
      return {
        mode: item.mode,
        label: item.label,
        matchedText: match[0].trim(),
      };
    }
  }
  return null;
}

function detectTelecomOperator(phone: string): { operator: TelecomOperator | null; label: string | null } {
  if (!phone || phone.length < 3) return { operator: null, label: null };
  const prefix = phone.slice(0, 2);
  if (prefix === '06') return { operator: 'MOBILIS', label: 'Mobilis (موبيليس)' };
  if (prefix === '07') return { operator: 'DJEZZY', label: 'Djezzy (جيزي)' };
  if (prefix === '05') return { operator: 'OOREDOO', label: 'Ooredoo (أوريدو)' };
  if (['02', '03', '04'].includes(prefix))
    return { operator: 'ALGERIE_TELECOM', label: 'Algérie Télécom (اتصالات الجزائر)' };
  return { operator: null, label: null };
}

function formatAlgerianPhone(phone: string): { formatted: string | null; whatsappUrl: string | null } {
  if (!phone) return { formatted: null, whatsappUrl: null };
  if (phone.length === 10 && ['05', '06', '07'].includes(phone.slice(0, 2))) {
    const formatted = `+213 ${phone.slice(1, 4)} ${phone.slice(4, 6)} ${phone.slice(6, 8)} ${phone.slice(8, 10)}`;
    const whatsappUrl = `https://wa.me/213${phone.slice(1)}`;
    return { formatted, whatsappUrl };
  } else if (phone.length === 9 && ['02', '03', '04'].includes(phone.slice(0, 2))) {
    const formatted = `+213 ${phone.slice(1, 3)} ${phone.slice(3, 5)} ${phone.slice(5, 7)} ${phone.slice(7, 9)}`;
    return { formatted, whatsappUrl: null };
  }
  return { formatted: null, whatsappUrl: null };
}

function extractPhones(text: string): PhoneEntity[] {
  const results: PhoneEntity[] = [];
  const added = new Set<string>();
  const regex = new RegExp(PHONE_PATTERN.source, 'gi');
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    const rawVal = match[1].trim();
    let cleaned = rawVal.replace(/[\s.-]/g, '');
    if (cleaned.startsWith('00213')) {
      cleaned = '0' + cleaned.slice(5);
    } else if (cleaned.startsWith('+213')) {
      cleaned = '0' + cleaned.slice(4);
    }

    if (!added.has(cleaned)) {
      added.add(cleaned);
      const { operator, label } = detectTelecomOperator(cleaned);
      const { formatted, whatsappUrl } = formatAlgerianPhone(cleaned);
      results.push({
        raw: rawVal,
        normalized: cleaned,
        operator,
        operatorLabel: label,
        formatted,
        whatsappUrl,
      });
    }
  }

  return results;
}

export function extractEntities(text: string): EntitiesResult {
  if (!text) {
    return {
      wilayas: [],
      payments: [],
      prices: [],
      deliveries: [],
      deliveryMode: null,
      phones: [],
      quantities: [],
      attributes: { colors: [], sizes: [] },
    };
  }

  const wilayasData = loadWilayas();
  return {
    wilayas: extractWilayas(text, wilayasData),
    payments: extractPayments(text),
    prices: extractPrices(text),
    deliveries: extractDeliveries(text),
    deliveryMode: extractDeliveryMode(text),
    phones: extractPhones(text),
    quantities: extractQuantities(text),
    attributes: extractProductAttributes(text),
  };
}
