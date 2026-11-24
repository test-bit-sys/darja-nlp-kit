/**
 * Zero-dependency HTTP Microservice Server for Algerian Darja NLP.
 * Ideal for n8n, Make.com, Flowise, local Docker containers, and webhooks.
 * Uses standard Node.js http module only.
 */

import http from 'http';
import { parse as parseUrl } from 'url';
import { normalize } from './normalizer';
import { arabiziToArabic } from './arabizi';
import { analyzeSentiment } from './sentiment';
import { extractEntities, getWilayas, getWilayaByCode } from './entities';
import { extractQuantities, extractProductAttributes } from './quantities';
import { detectEscalation } from './escalation';
import { detectDialect } from './dialect';
import { identifyIntent } from './intent';
import {
  detectCulturalReferences,
  getCulturalData,
  getSlangData,
  getMemesData,
  getFrancoDarjaData,
  detectMemes,
  detectFrancoDarja,
} from './cultural';
import { respondToDarja, DialoguePersona, DialogueScript } from './dialogue';
import { detectProfanity, censorProfanity } from './profanity';
import { buildAgentContext, formatAgentSystemPrompt } from './agent';

export interface ServerOptions {
  host?: string;
  port?: number;
}

export function startServer(options: ServerOptions = {}): http.Server {
  const host = options.host || '0.0.0.0';
  const port = options.port || 8080;

  const server = http.createServer((req, res) => {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    if (req.method === 'OPTIONS') {
      res.writeHead(204);
      res.end();
      return;
    }

    const parsedUrl = parseUrl(req.url || '', true);
    const pathname = (parsedUrl.pathname || '').replace(/\/+$/, '');

    const sendJson = (data: unknown, statusCode = 200) => {
      res.writeHead(statusCode, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify(data, null, 2));
    };

    const sendError = (msg: string, statusCode = 400) => {
      sendJson({ error: msg }, statusCode);
    };

    if (req.method === 'GET') {
      if (pathname === '' || pathname === '/api' || pathname === '/api/health') {
        sendJson({
          service: 'darja-nlp-kit',
          status: 'online',
          version: '1.0.0',
          endpoints: [
            'POST /api/parse',
            'POST /api/intent',
            'POST /api/sentiment',
            'POST /api/dialect',
            'POST /api/escalation',
            'POST /api/quantities',
            'POST /api/culture',
            'POST /api/agent-context',
            'GET  /api/wilayas',
            'GET  /api/wilayas/:code',
            'GET  /api/culture',
          ],
        });
        return;
      }

      if (pathname === '/api/culture') {
        const cData = getCulturalData();
        const sData = getSlangData();
        sendJson({
          service: 'darja-nlp-kit cultural knowledge engine',
          proverbs_count: (cData.proverbs || []).length,
          memes_count: (cData.memes_and_trends || []).length,
          landmarks_count: (cData.landmarks || []).length,
          gastronomy_count: (cData.gastronomy || []).length,
          slang_count: (sData.expressions || []).length,
        });
        return;
      }

      if (pathname === '/api/wilayas') {
        const wilayas = getWilayas();
        sendJson({
          count: wilayas.length,
          wilayas: wilayas.map((w) => ({
            code: w.code,
            code_str: w.code_str,
            name_ar: w.name_ar,
            name_fr: w.name_fr,
            communes_sample: w.communes_sample,
          })),
        });
        return;
      }

      if (pathname.startsWith('/api/wilayas/')) {
        const param = pathname.split('/').pop() || '';
        const codeNum = parseInt(param, 10);
        if (!isNaN(codeNum)) {
          const w = getWilayaByCode(codeNum);
          if (w) {
            sendJson({
              code: w.code,
              code_str: w.code_str,
              name_ar: w.name_ar,
              name_fr: w.name_fr,
              communes_sample: w.communes_sample,
              communes_fr_sample: w.communes_fr_sample,
            });
          } else {
            sendError(`Wilaya ${codeNum} not found (must be 1-69)`, 404);
          }
        } else {
          sendError('Invalid wilaya code (expected integer 1-69)', 400);
        }
        return;
      }

      if (pathname === '/api/memes') {
        sendJson(getMemesData());
        return;
      }

      if (pathname === '/api/franco') {
        sendJson(getFrancoDarjaData());
        return;
      }

      sendError('Endpoint not found', 404);
      return;
    }

    if (req.method === 'POST') {
      let bodyStr = '';
      req.on('data', (chunk) => {
        bodyStr += chunk;
      });

      req.on('end', () => {
        let body: Record<string, any> = {};
        if (bodyStr) {
          try {
            body = JSON.parse(bodyStr);
          } catch {
            sendError('Invalid JSON body in request', 400);
            return;
          }
        }

        const text = typeof body.text === 'string' ? body.text : '';
        if (!text && pathname !== '/api/agent-context') {
          sendError("Field 'text' is required in JSON body", 400);
          return;
        }

        if (pathname === '/api/parse') {
          const entities = extractEntities(text);
          const cult = detectCulturalReferences(text);
          sendJson({
            input: text,
            wilayas: entities.wilayas.map((w) => ({
              code: w.code,
              code_str: w.codeStr,
              name_ar: w.nameAr,
              name_fr: w.nameFr,
              commune: w.commune,
            })),
            prices: entities.prices.map((p) => ({
              raw: p.raw,
              amount: p.amount,
              currency: p.currency,
            })),
            phones: (entities.phones || []).map((ph) => ({
              raw: ph.raw,
              normalized: ph.normalized,
              operator: ph.operator,
              operator_label: ph.operatorLabel,
              formatted: ph.formatted,
              whatsapp_url: ph.whatsappUrl,
            })),
            payments: (entities.payments || []).map((p) => ({
              method: p.type,
              label: p.label,
              matched_text: p.matchedText,
            })),
            deliveries: (entities.deliveries || []).map((d) => ({
              company: d.company,
              label: d.label,
              matched_text: d.matchedText,
            })),
            delivery_mode: entities.deliveryMode
              ? {
                  mode: entities.deliveryMode.mode,
                  label: entities.deliveryMode.label,
                  matched_text: entities.deliveryMode.matchedText,
                }
              : null,
            quantities: (entities.quantities || []).map((q) => ({
              raw: q.raw,
              value: q.value,
              unit: q.unit,
            })),
            attributes: {
              colors: entities.attributes?.colors || [],
              sizes: entities.attributes?.sizes || [],
            },
            cultural: {
              has_cultural_reference: cult.hasCulturalReference,
              summary: cult.hasCulturalReference ? cult.culturalSummary : null,
            },
          });
          return;
        }

        if (pathname === '/api/intent') {
          const res = identifyIntent(text);
          sendJson({
            input: text,
            intent: res.intent,
            confidence: res.confidence,
            matched_keywords: res.matchedKeywords,
          });
          return;
        }

        if (pathname === '/api/sentiment') {
          const res = analyzeSentiment(text);
          sendJson({
            input: text,
            label: res.label,
            score: res.score,
            positive_tokens: res.positiveTokens,
            negative_tokens: res.negativeTokens,
          });
          return;
        }

        if (pathname === '/api/dialect') {
          const res = detectDialect(text);
          sendJson({
            input: text,
            region: res.region,
            confidence: res.confidence,
            detected_markers: res.detectedMarkers,
          });
          return;
        }

        if (pathname === '/api/escalation') {
          const res = detectEscalation(text);
          sendJson({
            input: text,
            needs_escalation: res.needsEscalation,
            reason: res.reason,
            urgency: res.urgency,
            matched_triggers: res.matchedTriggers,
            guideline: res.guideline,
          });
          return;
        }

        if (pathname === '/api/quantities') {
          const quants = extractQuantities(text);
          const attrs = extractProductAttributes(text);
          sendJson({
            input: text,
            quantities: quants.map((q) => ({ raw: q.raw, value: q.value, unit: q.unit })),
            attributes: { colors: attrs.colors, sizes: attrs.sizes },
          });
          return;
        }

        if (pathname === '/api/culture' || pathname === '/api/cultural') {
          const cult = detectCulturalReferences(text);
          sendJson({
            input: text,
            has_cultural_reference: cult.hasCulturalReference,
            proverbs: cult.proverbs.map((p) => ({
              canonical_name: p.canonicalName,
              meaning: p.meaning,
              region: p.metadata?.region,
            })),
            memes_and_trends: cult.memesAndTrends.map((m) => ({
              canonical_name: m.canonicalName,
              meaning: m.meaning,
              tone: m.metadata?.tone,
            })),
            landmarks: cult.landmarks.map((l) => ({
              canonical_name: l.canonicalName,
              city: l.metadata?.city,
              wilaya_code: l.metadata?.wilaya_code,
              description: l.meaning,
            })),
            gastronomy: cult.gastronomy.map((g) => ({
              canonical_name: g.canonicalName,
              origin: g.metadata?.origin,
              category: g.metadata?.category,
            })),
            slang_expressions: cult.slangExpressions.map((s) => ({
              canonical_name: s.canonicalName,
              meaning: s.meaning,
              polarity: s.metadata?.polarity,
            })),
            cultural_summary: cult.culturalSummary,
          });
          return;
        }

        if (pathname === '/api/agent-context') {
          const storeName = body.store_name || body.storeName || 'Bazar El Djazair';
          const ctx = buildAgentContext(text, storeName);
          const systemPrompt = formatAgentSystemPrompt(ctx);
          sendJson({
            context: ctx,
            formatted_system_prompt: systemPrompt,
          });
          return;
        }

        if (pathname === '/api/normalize') {
          sendJson({ input: text, normalized: normalize(text) });
          return;
        }

        if (pathname === '/api/arabizi') {
          sendJson({ input: text, arabic: arabiziToArabic(text) });
          return;
        }

        if (pathname === '/api/chat') {
          const persona = (body.persona || 'casual') as DialoguePersona;
          const script = (body.script || 'auto') as DialogueScript;
          const res = respondToDarja(text, { persona, script });
          sendJson({
            input: text,
            reply: res.reply,
            intent: res.intent,
            script: res.script,
            confidence: res.confidence,
            matched_pattern: res.matchedPattern,
          });
          return;
        }

        if (pathname === '/api/moderate') {
          const mask = typeof body.mask === 'string' ? body.mask : '***';
          const res = detectProfanity(text);
          const censored = censorProfanity(text, mask);
          sendJson({
            input: text,
            is_profane: res.isProfane,
            severity: res.severity,
            matches: res.matches.map((m) => ({
              term: m.term,
              category: m.category,
              severity: m.severity,
              matched_text: m.matchedText,
            })),
            censored_text: censored,
          });
          return;
        }

        if (pathname === '/api/memes') {
          const memes = detectMemes(text);
          sendJson({
            input: text,
            memes: memes.map((m) => ({
              phrase: m.canonicalName,
              meaning: m.meaning,
              metadata: m.metadata,
            })),
          });
          return;
        }

        if (pathname === '/api/franco') {
          const matches = detectFrancoDarja(text);
          sendJson({
            input: text,
            matches,
          });
          return;
        }

        sendError(`Endpoint '${pathname}' not found`, 404);
      });
      return;
    }

    sendError(`Method ${req.method} not allowed`, 405);
  });

  server.listen(port, host, () => {
    console.log(`🚀 darja-nlp-kit Microservice running on http://${host}:${port}`);
    console.log(`📦 Ready for n8n, Make.com, webhooks, and local AI automations.`);
    console.log(`Endpoints:`);
    console.log(`  • GET  http://${host}:${port}/api/health`);
    console.log(`  • GET  http://${host}:${port}/api/wilayas`);
    console.log(`  • POST http://${host}:${port}/api/parse`);
    console.log(`  • POST http://${host}:${port}/api/intent`);
    console.log(`  • POST http://${host}:${port}/api/sentiment`);
    console.log(`  • POST http://${host}:${port}/api/dialect`);
    console.log(`  • POST http://${host}:${port}/api/escalation`);
    console.log(`  • POST http://${host}:${port}/api/agent-context`);
  });

  return server;
}
