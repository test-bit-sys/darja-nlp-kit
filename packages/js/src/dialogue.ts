/**
 * Algerian Darja conversational dialogue response engine (Natural Algerian Chat).
 */
import * as path from 'path';
import * as fs from 'fs';
import { identifyIntent } from './intent';

export type DialoguePersona = 'casual' | 'merchant' | 'assistant';
export type DialogueScript = 'auto' | 'arabizi' | 'arabic';

export interface DialogueOptions {
  persona?: DialoguePersona;
  script?: DialogueScript;
}

export interface DialogueResponse {
  reply: string;
  intent: string;
  script: 'arabizi' | 'arabic';
  confidence: number;
  matchedPattern?: string;
}

interface DialogueRule {
  intent: string;
  patterns_arabizi: string[];
  patterns_arabic: string[];
  responses_arabizi: string[];
  responses_arabic: string[];
}

interface DialogueRulesDataset {
  rules: DialogueRule[];
}

let dialogueRulesData: DialogueRulesDataset | null = null;

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
  // Remove excessive punctuation
  t = t.replace(/[!?.,;:\-_/\\]+/g, ' ');
  // Remove tashkeel and tatweel
  t = t.replace(/[\u064B-\u065F\u0670\u0640]/g, '');
  // Collapse repetitive characters (3+ down to 1)
  t = t.replace(/(.)\1{2,}/g, '$1');
  // Collapse whitespace
  t = t.replace(/\s+/g, ' ').trim();
  return t;
}

export function respondToDarja(
  text: string,
  options?: DialogueOptions
): DialogueResponse {
  const persona = options?.persona || 'casual';
  const reqScript = options?.script || 'auto';

  if (!text || !text.trim()) {
    const defaultScript = reqScript === 'arabizi' ? 'arabizi' : 'arabic';
    return {
      reply: defaultScript === 'arabizi' ? 'We cv kho, kash ma khasek?' : 'مرحباً بيك خويا، كاش ما نسحقو نخدموك؟',
      intent: 'EMPTY',
      script: defaultScript,
      confidence: 1.0
    };
  }

  const resolvedScript = reqScript === 'auto' ? detectScript(text) : reqScript;
  const normInput = normalizeChatInput(text);
  const rules = loadDialogueRules().rules || [];

  // Check specific rules
  for (const rule of rules) {
    const patterns = resolvedScript === 'arabizi' ? rule.patterns_arabizi : rule.patterns_arabic;
    const altPatterns = resolvedScript === 'arabizi' ? rule.patterns_arabic : rule.patterns_arabizi;

    for (const p of patterns) {
      const normP = normalizeChatInput(p);
      if (normInput.includes(normP) || normP.includes(normInput)) {
        const responses = resolvedScript === 'arabizi' ? rule.responses_arabizi : rule.responses_arabic;
        let chosenReply = responses[0] || '';

        if (persona === 'merchant' && rule.intent === 'WELLBEING_INQUIRY') {
          chosenReply = resolvedScript === 'arabizi'
            ? 'We cv hamdoulah kho! Marhba bik f la boutique ta3na, kash ma khasek sel3a?'
            : 'لاباس الحمد لله ربي يحفظك خويا! مرحباً بيك في متجرنا، كاش ما راك تحوس سلعة؟';
        } else if (persona === 'assistant' && rule.intent === 'WELLBEING_INQUIRY') {
          chosenReply = resolvedScript === 'arabizi'
            ? 'Hamdoullah kolchi bkhir! Kifech n9der n3awnek lyoum kho?'
            : 'الحمد لله على خير خويا! كيفاش نقدر نعاونك اليوم في استفسارك؟';
        }

        return {
          reply: chosenReply,
          intent: rule.intent,
          script: resolvedScript,
          confidence: 0.95,
          matchedPattern: p
        };
      }
    }

    for (const p of altPatterns) {
      const normP = normalizeChatInput(p);
      if (normInput.includes(normP)) {
        const responses = resolvedScript === 'arabizi' ? rule.responses_arabizi : rule.responses_arabic;
        const chosenReply = responses[0] || '';
        return {
          reply: chosenReply,
          intent: rule.intent,
          script: resolvedScript,
          confidence: 0.90,
          matchedPattern: p
        };
      }
    }
  }

  // Fallback to intent classifier
  const intentResult = identifyIntent(text);
  const primary = intentResult.intent;

  if (primary === 'GREETING') {
    const reply = resolvedScript === 'arabizi'
      ? 'We cv hamdoulah w nta kho? Marhba bik!'
      : 'مرحباً بيك خويا العزيز! واش راك وكاش ما نسحقو نخدموك؟';
    return { reply, intent: 'GREETING', script: resolvedScript, confidence: 0.85 };
  }

  if (primary === 'PRICE_INQUIRY') {
    const reply = resolvedScript === 'arabizi'
      ? 'Marhba bik kho! Souma mrigla w kayna livraison rapide l ga3 69 wilaya.'
      : 'مرحباً بيك خويا! السومة مريڤلة بزاف والتوصيل متوفر لجميع 69 ولاية.';
    return { reply, intent: 'PRICE_INQUIRY', script: resolvedScript, confidence: 0.85 };
  }

  if (primary === 'COMPLAINT') {
    const reply = resolvedScript === 'arabizi'
      ? "Hassinek kho w smahlna 3la had l'erreur! Ab3atli numéro ta3 la commande w nreglouhalek f lwa9t."
      : 'حقك علينا خويا ونعتذرو منك! ابعثلي رقم الطلبية ونريڤلوهالك فوراً بإذن الله.';
    return { reply, intent: 'COMPLAINT', script: resolvedScript, confidence: 0.85 };
  }

  const defaultReply = resolvedScript === 'arabizi'
    ? 'We cv kho! Marhba bik, kifech n9edrou n3awnouk lyoum?'
    : 'مرحباً بيك خويا الغالي! كيفاش نقدرو نعاونوك اليوم في خدمتك؟';

  return {
    reply: defaultReply,
    intent: 'CASUAL_CHAT',
    script: resolvedScript,
    confidence: 0.75
  };
}
