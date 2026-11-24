/**
 * Algerian Darja conversational dialogue response engine (Rules + Real KB Retrieval).
 */
import * as path from 'path';
import * as fs from 'fs';
import { identifyIntent } from './intent';

export type DialoguePersona = 'casual' | 'merchant' | 'assistant';
export type DialogueScript = 'auto' | 'arabizi' | 'arabic';
export type DialogueStrategy = 'auto' | 'rules' | 'retrieval';

export interface DialogueRule {
  intent: string;
  patterns_arabizi: string[];
  patterns_arabic: string[];
  responses_arabizi: string[];
  responses_arabic: string[];
}

export interface DialogueOptions {
  persona?: DialoguePersona;
  script?: DialogueScript;
  strategy?: DialogueStrategy;
  vary?: boolean;
  customRules?: DialogueRule[];
}

export interface DialogueResponse {
  reply: string;
  intent: string;
  script: 'arabizi' | 'arabic';
  confidence: number;
  matchedPattern?: string;
  source?: string;
}

interface DialogueRulesDataset {
  rules: DialogueRule[];
}

interface KBEntry {
  id: string;
  source: string;
  script: 'arabizi' | 'arabic';
  prompt: string;
  reply: string;
  intent: string;
}

const KB_STOP = new Set([
  'el', 'al', 'la', 'le', 'les', 'de', 'du', 'un', 'une', 'et', 'ou', 'en',
  'wa', 'w', 'f', 'fi', 'fel', 'l', 'li', 'ta3', 'taa', 'men', 'mn', 'min',
  'b', 'bi', 'ala', '3la', 'ya', 'في', 'من', 'على', 'الى', 'إلى', 'عن', 'مع',
  'و', 'أو', 'او', 'ال', 'لي', 'تاع', 'نتاع', 'ديال', 'وش', 'واش', 'يا', 'راها', 'راهو',
]);

let dialogueRulesData: DialogueRulesDataset | null = null;
let kbEntriesCache: KBEntry[] | null = null;
let kbIndexCache: {
  inv: Map<string, number[]>;
  docVecs: Array<Map<string, number>>;
  idf: Map<string, number>;
} | null = null;

function loadDialogueRules(): DialogueRulesDataset {
  if (dialogueRulesData) return dialogueRulesData;

  const dataPath = path.resolve(__dirname, '../data/dialogue_rules.json');
  const raw = fs.readFileSync(dataPath, 'utf-8');
  dialogueRulesData = JSON.parse(raw) as DialogueRulesDataset;
  return dialogueRulesData;
}

function detectScript(text: string): 'arabizi' | 'arabic' {
  const latinCount = (text.match(/[a-zA-Z]/g) || []).length;
  const arabicCount = (text.match(/[\u0600-\u06FF]/g) || []).length;
  return arabicCount > latinCount ? 'arabic' : 'arabizi';
}

function normalizeChatInput(text: string): string {
  let t = text.toLowerCase().trim();
  t = t.replace(/[!?.,;:\-_/\\]+/g, ' ');
  t = t.replace(/[\u064B-\u065F\u0670\u0640]/g, '');
  t = t.replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي');
  t = t.replace(/(.)\1{2,}/g, '$1');
  t = t.replace(/\s+/g, ' ').trim();
  return t;
}

function kbTokenize(text: string): string[] {
  const norm = normalizeChatInput(text);
  const toks = norm.match(/[a-z0-9\u0600-\u06FF']+/g) || [];
  return toks.filter((tok) => tok.length >= 2 && !KB_STOP.has(tok));
}

function loadDialogueKB(): KBEntry[] {
  if (!kbEntriesCache) {
    const kbPath = path.resolve(__dirname, '../data/dialogue_kb.json');
    if (fs.existsSync(kbPath)) {
      try {
        const parsed = JSON.parse(fs.readFileSync(kbPath, 'utf-8'));
        kbEntriesCache = (parsed.entries || []) as KBEntry[];
      } catch {
        kbEntriesCache = [];
      }
    } else {
      kbEntriesCache = [];
    }
  }

  if (!kbIndexCache && kbEntriesCache.length > 0) {
    const inv = new Map<string, number[]>();
    const df = new Map<string, number>();
    const docToks: string[][] = [];

    kbEntriesCache.forEach((entry, idx) => {
      const uniqueToks = Array.from(new Set(kbTokenize(entry.prompt || '')));
      docToks.push(uniqueToks);
      for (const tok of uniqueToks) {
        df.set(tok, (df.get(tok) || 0) + 1);
        const list = inv.get(tok) || [];
        list.push(idx);
        inv.set(tok, list);
      }
    });

    const nDocs = kbEntriesCache.length;
    const idf = new Map<string, number>();
    for (const [tok, freq] of df.entries()) {
      idf.set(tok, Math.log((nDocs + 1) / (freq + 1)) + 1);
    }

    const docVecs: Array<Map<string, number>> = docToks.map((toks) => {
      const vec = new Map<string, number>();
      let sqSum = 0;
      for (const tok of toks) {
        const w = idf.get(tok) || 1;
        sqSum += w * w;
        vec.set(tok, w);
      }
      const norm = Math.sqrt(sqSum) || 1;
      for (const [k, v] of vec.entries()) {
        vec.set(k, v / norm);
      }
      return vec;
    });

    kbIndexCache = { inv, docVecs, idf };
  }

  return kbEntriesCache;
}

function searchKB(text: string, preferredScript: 'arabizi' | 'arabic'): { entry: KBEntry; score: number } | null {
  const entries = loadDialogueKB();
  if (!entries.length || !kbIndexCache) return null;

  const qToks = Array.from(new Set(kbTokenize(text)));
  if (qToks.length < 2) return null;

  const { inv, docVecs, idf } = kbIndexCache;
  const qVec = new Map<string, number>();
  let sqSum = 0;
  for (const tok of qToks) {
    const w = idf.get(tok) || 1;
    sqSum += w * w;
    qVec.set(tok, w);
  }
  const qNorm = Math.sqrt(sqSum) || 1;
  for (const [k, v] of qVec.entries()) {
    qVec.set(k, v / qNorm);
  }

  const candidates = new Set<number>();
  for (const tok of qVec.keys()) {
    const posting = inv.get(tok);
    if (posting) {
      for (const idx of posting) candidates.add(idx);
    }
  }
  if (candidates.size === 0) return null;

  let bestEntry: KBEntry | null = null;
  let bestScore = 0;

  for (const idx of candidates) {
    const dVec = docVecs[idx];
    let sim = 0;
    for (const [tok, w] of qVec.entries()) {
      sim += w * (dVec.get(tok) || 0);
    }
    const entry = entries[idx];
    if (entry.script === preferredScript) sim += 0.06;
    if (sim > bestScore) {
      bestScore = sim;
      bestEntry = entry;
    }
  }

  if (bestEntry && bestScore >= 0.34) {
    return { entry: bestEntry, score: bestScore };
  }
  return null;
}

function pickResponse(responses: string[], normInput: string, vary: boolean): string {
  if (!responses || responses.length === 0) return '';
  if (!vary || responses.length === 1) return responses[0];
  let hashSum = 0;
  for (let i = 0; i < normInput.length; i++) hashSum += normInput.charCodeAt(i);
  return responses[hashSum % responses.length];
}

export function respondToDarja(
  text: string,
  options?: DialogueOptions
): DialogueResponse {
  const persona = options?.persona || 'casual';
  const reqScript = options?.script || 'auto';
  const strategy: DialogueStrategy = options?.strategy || 'auto';
  const vary = options?.vary ?? false;

  if (!text || !text.trim()) {
    const defaultScript = reqScript === 'arabizi' ? 'arabizi' : 'arabic';
    return {
      reply: defaultScript === 'arabizi' ? 'We cv kho, kash ma khasek?' : 'مرحباً بيك خويا، كاش ما نسحقو نخدموك؟',
      intent: 'EMPTY',
      script: defaultScript,
      confidence: 1.0,
      source: 'default',
    };
  }

  const resolvedScript = reqScript === 'auto' ? detectScript(text) : reqScript;
  const normInput = normalizeChatInput(text);

  if (strategy !== 'retrieval') {
    const baseRules = loadDialogueRules().rules || [];
    const allRules: Array<{ isCustom: boolean; rule: DialogueRule }> = [
      ...(options?.customRules || []).map((rule) => ({ isCustom: true, rule })),
      ...baseRules.map((rule) => ({ isCustom: false, rule })),
    ];

    let bestMatch: { score: number; matchedPattern: string; isCustom: boolean; rule: DialogueRule; confidence: number } | null = null;

    for (const { isCustom, rule } of allRules) {
      const patterns = resolvedScript === 'arabizi' ? rule.patterns_arabizi : rule.patterns_arabic;
      const altPatterns = resolvedScript === 'arabizi' ? rule.patterns_arabic : rule.patterns_arabizi;

      for (const p of patterns || []) {
        const normP = normalizeChatInput(p);
        if (!normP) continue;
        let score = 0;
        if (normInput === normP) {
          score = normP.length + 200;
        } else if (normInput.includes(normP)) {
          score = normP.length + 25;
        } else if (normInput.length >= 4 && normP.includes(normInput)) {
          score = normInput.length + 5;
        }
        if (score > 0) {
          if (isCustom) score += 50;
          if (!bestMatch || score > bestMatch.score) {
            bestMatch = { score, matchedPattern: p, isCustom, rule, confidence: 0.95 };
          }
        }
      }

      for (const p of altPatterns || []) {
        const normP = normalizeChatInput(p);
        if (!normP) continue;
        if (normInput.includes(normP)) {
          const score = normP.length + (isCustom ? 40 : 10);
          if (!bestMatch || score > bestMatch.score) {
            bestMatch = { score, matchedPattern: p, isCustom, rule, confidence: 0.90 };
          }
        }
      }
    }

    if (bestMatch) {
      const { matchedPattern, isCustom, rule, confidence } = bestMatch;
      const responses = resolvedScript === 'arabizi' ? rule.responses_arabizi : rule.responses_arabic;
      let chosenReply = pickResponse(responses || [], normInput, vary);

      if (!isCustom && rule.intent === 'WELLBEING_INQUIRY') {
        if (persona === 'merchant') {
          chosenReply = resolvedScript === 'arabizi'
            ? 'We cv hamdoulah kho! Marhba bik f la boutique ta3na, kash ma khasek sel3a?'
            : 'لاباس الحمد لله ربي يحفظك خويا! مرحباً بيك في متجرنا، كاش ما راك تحوس سلعة؟';
        } else if (persona === 'assistant') {
          chosenReply = resolvedScript === 'arabizi'
            ? 'Hamdoullah kolchi bkhir! Kifech n9der n3awnek lyoum kho?'
            : 'الحمد لله على خير خويا! كيفاش نقدر نعاونك اليوم في استفسارك؟';
        }
      }

      return {
        reply: chosenReply,
        intent: rule.intent,
        script: resolvedScript,
        confidence,
        matchedPattern,
        source: isCustom ? 'custom_rule' : 'rule',
      };
    }
  }

  if (strategy === 'auto' || strategy === 'retrieval') {
    const kbHit = searchKB(text, resolvedScript);
    if (kbHit) {
      const { entry, score } = kbHit;
      const entryScript = reqScript !== 'auto' ? resolvedScript : entry.script;
      return {
        reply: entry.reply,
        intent: entry.intent || 'CONVERSATION',
        script: entryScript,
        confidence: Math.round(Math.min(0.92, 0.55 + score * 0.5) * 100) / 100,
        matchedPattern: entry.prompt,
        source: 'kb_retrieval',
      };
    }
  }

  const intentResult = identifyIntent(text);
  const primary = intentResult.intent;

  if (primary === 'GREETING') {
    const reply = resolvedScript === 'arabizi'
      ? 'We cv hamdoulah w nta kho? Marhba bik!'
      : 'مرحباً بيك خويا العزيز! واش راك وكاش ما نسحقو نخدموك؟';
    return { reply, intent: 'GREETING', script: resolvedScript, confidence: 0.85, source: 'intent_fallback' };
  }

  if (primary === 'PRICE_INQUIRY') {
    const reply = resolvedScript === 'arabizi'
      ? 'Marhba bik kho! Souma mrigla w kayna livraison rapide l ga3 69 wilaya.'
      : 'مرحباً بيك خويا! السومة مريڤلة بزاف والتوصيل متوفر لجميع 69 ولاية.';
    return { reply, intent: 'PRICE_INQUIRY', script: resolvedScript, confidence: 0.85, source: 'intent_fallback' };
  }

  if (primary === 'ORDER') {
    const reply = resolvedScript === 'arabizi'
      ? "Marhba bik kho! Ab3atli lwilaya, l'adresse w numéro de téléphone w nconfirmiwlek la commande."
      : 'مرحباً بيك خويا! ابعثلي الولاية، العنوان ورقم الهاتف باش نسجلو طلبيتك فوراً.';
    return { reply, intent: 'ORDER', script: resolvedScript, confidence: 0.85, source: 'intent_fallback' };
  }

  if (primary === 'DELIVERY_INQUIRY') {
    const reply = resolvedScript === 'arabizi'
      ? 'Kayna livraison rapide l ga3 69 wilaya (24-48h) l bab dar wla stop desk!'
      : 'التوصيل متوفر لجميع 69 ولاية في ظرف 24 إلى 48 ساعة لباب الدار أو المكتب!';
    return { reply, intent: 'DELIVERY_INQUIRY', script: resolvedScript, confidence: 0.85, source: 'intent_fallback' };
  }

  if (primary === 'AVAILABILITY_INQUIRY') {
    const reply = resolvedScript === 'arabizi'
      ? 'Ih kho mazalha dispo f stock! Marhba bik idha rak hab tcommandi.'
      : 'إيه خويا مازالها متوفرة في الستوك! مرحباً بيك إذا راك حاب تطلبها.';
    return { reply, intent: 'AVAILABILITY_INQUIRY', script: resolvedScript, confidence: 0.85, source: 'intent_fallback' };
  }

  if (primary === 'COMPLAINT') {
    const reply = resolvedScript === 'arabizi'
      ? "Hassinek kho w smahlna 3la had l'erreur! Ab3atli numéro ta3 la commande w nreglouhalek f lwa9t."
      : 'حقك علينا خويا ونعتذرو منك! ابعثلي رقم الطلبية ونريڤلوهالك فوراً بإذن الله.';
    return { reply, intent: 'COMPLAINT', script: resolvedScript, confidence: 0.85, source: 'intent_fallback' };
  }

  const defaultReply = resolvedScript === 'arabizi'
    ? 'We cv kho! Marhba bik, kifech n9edrou n3awnouk lyoum?'
    : 'مرحباً بيك خويا الغالي! كيفاش نقدرو نعاونوك اليوم في خدمتك؟';

  return {
    reply: defaultReply,
    intent: 'CASUAL_CHAT',
    script: resolvedScript,
    confidence: 0.75,
    source: 'default',
  };
}
