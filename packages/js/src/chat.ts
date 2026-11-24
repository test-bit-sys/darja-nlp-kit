/**
 * Stateful multi-turn conversational session manager for Algerian Darja e-commerce & AI bots.
 */
import { detectDialect } from './dialect';
import { DialoguePersona, DialogueRule, DialogueScript, respondToDarja } from './dialogue';
import { extractEntities } from './entities';
import { detectEscalation } from './escalation';
import { identifyIntent } from './intent';
import { DialectRegion, EscalationResult } from './types';

export interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  intent: string;
}

export interface ChatSlots {
  wilayas: Array<{ code: number; name_ar: string; name_fr: string; commune?: string | null }>;
  phones: Array<{ normalized: string; operator?: string | null; whatsapp?: string | null }>;
  deliveries: string[];
  delivery_mode: string | null;
  payments: string[];
  prices_dzd: number[];
  quantities: Array<{ value: number; unit: string; raw: string }>;
  colors: string[];
  sizes: string[];
}

export interface ChatTurnResult {
  reply: string;
  intent: string;
  script: 'arabizi' | 'arabic';
  dialect: DialectRegion;
  extractedSlots: ChatSlots;
  missingSlots: string[];
  readyToConfirm: boolean;
  escalation: EscalationResult;
  history: ChatMessage[];
}

export interface DarjaChatOptions {
  storeName?: string;
  persona?: DialoguePersona;
  script?: DialogueScript;
  customRules?: DialogueRule[];
}

export class DarjaChat {
  public storeName: string;
  public persona: DialoguePersona;
  public script: DialogueScript;
  public customRules: DialogueRule[];
  public history: ChatMessage[] = [];
  public detectedDialect: DialectRegion = 'GENERAL_DARJA';
  public preferredScript: 'arabizi' | 'arabic' | null = null;
  public activeIntent = 'UNKNOWN';
  public slots: ChatSlots = this.emptySlots();

  constructor(options?: DarjaChatOptions) {
    this.storeName = options?.storeName ?? 'Bazar El Djazair';
    this.persona = options?.persona ?? 'merchant';
    this.script = options?.script ?? 'auto';
    this.customRules = [...(options?.customRules || [])];
  }

  private emptySlots(): ChatSlots {
    return {
      wilayas: [],
      phones: [],
      deliveries: [],
      delivery_mode: null,
      payments: [],
      prices_dzd: [],
      quantities: [],
      colors: [],
      sizes: [],
    };
  }

  reset(): void {
    this.history = [];
    this.detectedDialect = 'GENERAL_DARJA';
    this.preferredScript = null;
    this.activeIntent = 'UNKNOWN';
    this.slots = this.emptySlots();
  }

  private detectTurnScript(text: string): 'arabizi' | 'arabic' {
    const latinCount = (text.match(/[a-zA-Z]/g) || []).length;
    const arabicCount = (text.match(/[\u0600-\u06FF]/g) || []).length;
    if (arabicCount === 0 && latinCount === 0 && this.preferredScript) {
      return this.preferredScript;
    }
    return arabicCount > latinCount ? 'arabic' : 'arabizi';
  }

  private mergeEntities(text: string): string[] {
    const ent = extractEntities(text);
    const newlyCaptured: string[] = [];

    const existingW = new Set(this.slots.wilayas.map((w) => w.code));
    for (const w of ent.wilayas) {
      if (!existingW.has(w.code)) {
        this.slots.wilayas.push({
          code: w.code,
          name_ar: w.nameAr,
          name_fr: w.nameFr,
          commune: w.commune ?? null,
        });
        existingW.add(w.code);
        if (!newlyCaptured.includes('wilaya')) newlyCaptured.push('wilaya');
      }
    }

    const existingP = new Set(this.slots.phones.map((p) => p.normalized));
    for (const p of ent.phones || []) {
      if (!existingP.has(p.normalized)) {
        this.slots.phones.push({
          normalized: p.normalized,
          operator: p.operatorLabel ?? null,
          whatsapp: p.whatsappUrl ?? null,
        });
        existingP.add(p.normalized);
        if (!newlyCaptured.includes('phone')) newlyCaptured.push('phone');
      }
    }

    for (const d of ent.deliveries || []) {
      if (!this.slots.deliveries.includes(d.label)) this.slots.deliveries.push(d.label);
    }

    if (ent.deliveryMode && !this.slots.delivery_mode) {
      this.slots.delivery_mode = ent.deliveryMode.label;
    }

    for (const pay of ent.payments) {
      if (!this.slots.payments.includes(pay.label)) this.slots.payments.push(pay.label);
    }

    for (const pr of ent.prices) {
      if (pr.amount !== null && !this.slots.prices_dzd.includes(pr.amount)) {
        this.slots.prices_dzd.push(pr.amount);
      }
    }

    for (const q of ent.quantities || []) {
      const exists = this.slots.quantities.some(
        (ex) => ex.raw === q.raw && ex.unit === q.unit && ex.value === q.value
      );
      if (!exists) {
        this.slots.quantities.push({ value: q.value, unit: q.unit, raw: q.raw });
        if (!newlyCaptured.includes('quantity')) newlyCaptured.push('quantity');
      }
    }

    if (ent.attributes) {
      for (const c of ent.attributes.colors) {
        if (!this.slots.colors.includes(c)) this.slots.colors.push(c);
      }
      for (const s of ent.attributes.sizes) {
        if (!this.slots.sizes.includes(s)) this.slots.sizes.push(s);
      }
    }

    return newlyCaptured;
  }

  send(message: string, options?: { vary?: boolean }): ChatTurnResult {
    const msg = (message || '').trim();
    const turnScript: 'arabizi' | 'arabic' =
      this.script === 'auto' ? this.detectTurnScript(msg) : this.script;
    if (msg) this.preferredScript = turnScript;

    const esc = detectEscalation(msg);
    const dia = detectDialect(msg);
    if (dia.region !== 'GENERAL_DARJA') this.detectedDialect = dia.region;

    const intentRes = identifyIntent(msg);
    if (intentRes.intent !== 'UNKNOWN') this.activeIntent = intentRes.intent;

    const newlyCaptured = this.mergeEntities(msg);
    this.history.push({ role: 'user', text: msg, intent: intentRes.intent });

    const missingSlots: string[] = [];
    if (this.slots.wilayas.length === 0) missingSlots.push('wilaya');
    if (this.slots.phones.length === 0) missingSlots.push('phone');
    const readyToConfirm = missingSlots.length === 0;

    const isOrderFlow =
      this.activeIntent === 'ORDER' ||
      this.activeIntent === 'DELIVERY_INQUIRY' ||
      newlyCaptured.length > 0;

    let replyText = '';
    let turnIntent = '';

    if (esc.needsEscalation) {
      replyText =
        turnScript === 'arabizi'
          ? "Smahlna bzaf kho! Rani n7awel had l'message drk l'responsable bach yreglihleek koulchi."
          : 'نعتذرو منك بزاف خويا! راني نحول رسالتك فوراً للمسؤول باش يتواصل معاك ويريڤليلك الإشكال.';
      turnIntent = `ESCALATION_${esc.reason || 'ALERT'}`;
    } else if (isOrderFlow && readyToConfirm && newlyCaptured.length > 0) {
      const w = this.slots.wilayas[this.slots.wilayas.length - 1];
      const ph = this.slots.phones[this.slots.phones.length - 1].normalized;
      const wLabel = turnScript === 'arabizi' ? `${w.name_fr} (${w.code})` : `${w.name_ar} (${w.code})`;
      replyText =
        turnScript === 'arabizi'
          ? `Sahit kho! La commande ta3ek mrigla w confirmée: wilaya ${wLabel}, téléphone ${ph}. Livraison f 24-48h!`
          : `صحيت خويا! طلبيتك مؤكدة ومسجلة: ولاية ${wLabel}، الهاتف ${ph}. التوصيل يوصلك خلال 24-48 ساعة!`;
      turnIntent = 'ORDER_CONFIRMED';
    } else if (
      this.activeIntent === 'ORDER' &&
      !readyToConfirm &&
      (newlyCaptured.length > 0 || intentRes.intent === 'ORDER')
    ) {
      if (missingSlots.includes('wilaya') && missingSlots.includes('phone')) {
        replyText =
          turnScript === 'arabizi'
            ? 'Marhba bik kho! Ab3atli bark lwilaya w numéro de téléphone bach nconfirmiwlek la commande.'
            : 'مرحباً بيك خويا! ابعثلي برك الولاية ورقم الهاتف باش نسجلو ونكونفيرميولك الطلبية.';
      } else if (missingSlots.includes('phone')) {
        const w = this.slots.wilayas[this.slots.wilayas.length - 1];
        const wLabel = turnScript === 'arabizi' ? w.name_fr : w.name_ar;
        replyText =
          turnScript === 'arabizi'
            ? `C'est bon lwilaya ${wLabel} msajla! Ba9i ghi numéro de téléphone kho bach nvalidiw la commande.`
            : `ممتاز، ولاية ${wLabel} مسجلة! بقالنا برك رقم الهاتف خويا باش نكونفيرميولك الطلبية.`;
      } else {
        const ph = this.slots.phones[this.slots.phones.length - 1].normalized;
        replyText =
          turnScript === 'arabizi'
            ? `Numéro ${ph} msajel kho! 9olli bark chmen wilaya w nwalou f lwa9t.`
            : `رقم الهاتف ${ph} مسجل خويا! قولي برك واش من ولاية باش نكملو الطلب.`;
      }
      turnIntent = 'ORDER_SLOT_FILLING';
    } else {
      const dRes = respondToDarja(msg, {
        persona: this.persona,
        script: turnScript,
        vary: options?.vary ?? false,
        customRules: this.customRules.length ? this.customRules : undefined,
      });
      replyText = dRes.reply;
      turnIntent = dRes.intent;
    }

    this.history.push({ role: 'assistant', text: replyText, intent: turnIntent });

    return {
      reply: replyText,
      intent: turnIntent,
      script: turnScript,
      dialect: this.detectedDialect,
      extractedSlots: JSON.parse(JSON.stringify(this.slots)) as ChatSlots,
      missingSlots,
      readyToConfirm,
      escalation: esc,
      history: [...this.history],
    };
  }
}
