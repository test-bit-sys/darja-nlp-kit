/**
 * Express.js Microservice Template for Algerian Darja NLP.
 * Requires: npm install express @types/express @dz-open-suite/darja-nlp-kit
 */

import express, { Request, Response } from 'express';
import {
  extractEntities,
  identifyIntent,
  detectEscalation,
  buildAgentContext,
  formatAgentSystemPrompt,
} from '../packages/js/src';

const app = express();
app.use(express.json());

app.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', service: 'darja-nlp-express' });
});

app.post('/api/parse', (req: Request, res: Response) => {
  const text: string = req.body.text || '';
  if (!text) {
    return res.status(400).json({ error: "Missing 'text' field" });
  }

  const entities = extractEntities(text);
  const intent = identifyIntent(text);
  const escalation = detectEscalation(text);

  return res.json({
    text,
    intent: intent.intent,
    needs_escalation: escalation.needsEscalation,
    wilayas: entities.wilayas.map((w) => ({ code: w.code, name_ar: w.nameAr, commune: w.commune })),
    phones: (entities.phones || []).map((ph) => ({
      normalized: ph.normalized,
      operator: ph.operatorLabel,
      whatsapp: ph.whatsappUrl,
    })),
    prices: entities.prices.map((p) => ({ amount: p.amount, raw: p.raw })),
    quantities: (entities.quantities || []).map((q) => ({ value: q.value, unit: q.unit })),
    attributes: {
      colors: entities.attributes?.colors || [],
      sizes: entities.attributes?.sizes || [],
    },
  });
});

app.post('/api/agent-context', (req: Request, res: Response) => {
  const text: string = req.body.text || '';
  const storeName: string = req.body.store_name || 'Bazar El Djazair';
  const ctx = buildAgentContext(text, storeName);
  const prompt = formatAgentSystemPrompt(ctx);

  return res.json({
    context: ctx,
    formatted_system_prompt: prompt,
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
