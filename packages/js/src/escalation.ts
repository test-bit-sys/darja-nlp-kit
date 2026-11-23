export type EscalationUrgency = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NONE';
export type EscalationReason = 'ANGRY_CUSTOMER' | 'HUMAN_REQUESTED' | 'DISPUTE' | 'LEGAL_THREAT';

export interface EscalationResult {
  needsEscalation: boolean;
  urgency: EscalationUrgency;
  reason?: EscalationReason | null;
  matchedTriggers: string[];
  guideline: string;
}

const HUMAN_REQUEST_TRIGGERS = [
  'احكي مع بنادم', 'مع انسان', 'مع بنادم', 'كاش انسان', 'عطيني المدير', 'خدمة الزبائن',
  'خدمة العملاء', 'عيطلي', 'كلمني', 'كلموني', 'حاب نهدر مع واحد', 'نهدر مع بنادم',
  'عيطولي في الهاتف', 'واحد يفهم', 'انسان حقيقي',
  'appel moi', 'appelez moi', 'parler a un responsable', 'parler a un agent',
  'service client', 'responsable', 'humain', '3aytli', 'nahdar m3a bnadm', 'telephonez moi',
];

const ANGRY_CUSTOMER_TRIGGERS = [
  'حشيتوهالي', 'حشاوها لي', 'سراقين', 'سرقة عيني عينك', 'فضيحة', 'رجعولي دراهمي',
  'وكيلكم ربي', 'حقارين', 'الله لا يربحكم', 'بهدلتو بينا', 'سلعة ميتة ومفاتشة',
  'تندمو', 'ما تحشموش', 'خردة', 'تبهديلة', 'سراق',
  '7chawhali', 'ser9a', 'arnaqueurs', 'la pire boutique', 'fdiha', 'behdeltouna',
  'rej3oli drahmi', 'ma thechmouch', 'voleurs',
];

const DISPUTE_TRIGGERS = [
  'ما رديتوش عليا', 'ما حبيتوش تبدلو', 'روتور مبلوكي', 'سلعة غالطة وما رديتوش',
  'عندي سمانة نستنى', 'عندي شهر', 'ما وصلني والو', 'دراهمي ما رجعوش',
  'pas de reponse', 'bloque', 'bloquer', '1 mois', 'une semaine',
];

const LEGAL_THREAT_TRIGGERS = [
  'نشكي بيكم', 'لابوليس', 'حماية المستهلك', 'العدالة', 'نديرلكم شكوى', 'محكمة',
  'la police', 'protection du consommateur', 'plainte', 'tribunal',
];

export function detectEscalation(text: string): EscalationResult {
  if (!text) {
    return {
      needsEscalation: false,
      urgency: 'NONE',
      reason: null,
      matchedTriggers: [],
      guideline: '',
    };
  }

  const lower = text.toLowerCase();

  // 1. Legal / Police Threat (CRITICAL)
  const legalMatches = LEGAL_THREAT_TRIGGERS.filter((t) => lower.includes(t.toLowerCase()));
  if (legalMatches.length > 0) {
    return {
      needsEscalation: true,
      urgency: 'CRITICAL',
      reason: 'LEGAL_THREAT',
      matchedTriggers: legalMatches,
      guideline: '🚨 الزبون يهدد بمتابعة قانونية أو شكوى رسمية! يجب تحويل المحادثة فوراً للإدارة وتجنب أي جدال آلي.',
    };
  }

  // 2. Angry Customer / Severe Abuse (HIGH)
  const angryMatches = ANGRY_CUSTOMER_TRIGGERS.filter((t) => lower.includes(t.toLowerCase()));
  if (angryMatches.length > 0) {
    return {
      needsEscalation: true,
      urgency: 'HIGH',
      reason: 'ANGRY_CUSTOMER',
      matchedTriggers: angryMatches,
      guideline: '⚠️ الزبون غاضب جداً ويتهم المتجر بسوء النية أو السرقة. يجب تدخل عون بشري لامتصاص الغضب وتقديم تعويض/استرجاع.',
    };
  }

  // 3. Explicit Request for Human (HIGH / MEDIUM)
  const humanMatches = HUMAN_REQUEST_TRIGGERS.filter((t) => lower.includes(t.toLowerCase()));
  if (humanMatches.length > 0) {
    return {
      needsEscalation: true,
      urgency: 'HIGH',
      reason: 'HUMAN_REQUESTED',
      matchedTriggers: humanMatches,
      guideline: '👤 الزبون يطلب التحدث مع شخص حقيقي أو مسؤول. تجنب الردود الآلية الطويلة وسهّل تواصل ممثل خدمة العملاء معه.',
    };
  }

  // 4. Long-standing Dispute / No Response (MEDIUM)
  const disputeMatches = DISPUTE_TRIGGERS.filter((t) => lower.includes(t.toLowerCase()));
  if (disputeMatches.length > 0) {
    return {
      needsEscalation: true,
      urgency: 'MEDIUM',
      reason: 'DISPUTE',
      matchedTriggers: disputeMatches,
      guideline: '📦 نزاع بخصوص تأخر كبير أو عدم استجابة في الاستبدال. يحتاج مراجعة بشرية لحالة الطلبية وشركة التوصيل.',
    };
  }

  return {
    needsEscalation: false,
    urgency: 'NONE',
    reason: null,
    matchedTriggers: [],
    guideline: 'محادثة طبيعية، يمكن لوكيل الذكاء الاصطناعي الرد عليها مباشرة.',
  };
}
