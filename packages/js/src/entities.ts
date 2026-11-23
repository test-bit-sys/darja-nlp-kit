import {
  WilayaRaw,
  WilayaEntity,
  PaymentEntity,
  PriceEntity,
  DeliveryEntity,
  DeliveryModeEntity,
  PhoneEntity,
  EntitiesResult,
} from './types';
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

const PHONE_PATTERN = /(?:^|\s|[^\w\u0600-\u06FF])((?:\+213|00213|0)\s*(?:[5-7]|2[0-9]|3[0-9]|4[0-9])(?:[\s.-]?\d){8})(?=$|\s|[^\w\u0600-\u06FF])/g;

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
        results.push({
          code: w.code,
          codeStr: w.code_str,
          nameAr: w.name_ar,
          nameFr: w.name_fr,
          matchedText: cand,
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

  // Match standard numbers with currency
  let numMatch: RegExpExecArray | null;
  const numRegex = new RegExp(PRICE_NUMERIC_PATTERN.source, 'gi');
  while ((numMatch = numRegex.exec(text)) !== null) {
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
  }

  // Match dynamic colloquial millions (e.g., 2 mlayen, 3 ملاين, 1.5 مليون)
  let dynMatch: RegExpExecArray | null;
  const dynRegex = new RegExp(DYNAMIC_MILLIONS_PATTERN.source, 'gi');
  while ((dynMatch = dynRegex.exec(text)) !== null) {
    const rawVal = dynMatch[1].replace(',', '.');
    const val = parseFloat(rawVal) * 10000;
    results.push({
      raw: dynMatch[0].trim(),
      amount: val,
      currency: 'DZD',
    });
  }

  // Match Darja fixed colloquial amounts
  for (const item of DARJA_AMOUNTS) {
    const match = text.match(item.pattern);
    if (match) {
      results.push({
        raw: match[0].trim(),
        amount: item.value,
        currency: 'DZD',
      });
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
      results.push({
        raw: rawVal,
        normalized: cleaned,
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
  };
}
