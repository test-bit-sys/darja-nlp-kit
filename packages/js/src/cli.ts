#!/usr/bin/env node
/**
 * Command-Line Interface (CLI) for darja-nlp-kit.
 *
 * Usage:
 *   darja-nlp parse "نحوس على 2 حبات مقاس XL نبعثهم لوهران 0661234567"
 *   darja-nlp intent "شحال التوصيل لسطيف؟"
 *   darja-nlp escalation "سراقين حشيتوهالي رجعولي دراهمي"
 *   darja-nlp server --port 8080
 */

import { extractEntities } from './entities';
import { identifyIntent } from './intent';
import { detectEscalation } from './escalation';
import { analyzeSentiment } from './sentiment';
import { detectDialect } from './dialect';
import { extractQuantities, extractProductAttributes } from './quantities';
import { buildAgentContext, formatAgentSystemPrompt } from './agent';
import { startServer } from './server';

function printHelp() {
  console.log(`
darja-nlp-kit CLI (Zero-dependency Algerian Darja NLP)

Usage:
  darja-nlp <command> [options] [text]

Commands:
  parse <text>         Extract Algerian entities (wilayas, communes, phones, prices, quantities)
  intent <text>        Identify customer business intent (ORDER, PRICE, DELIVERY, etc.)
  escalation <text>    Detect angry customers, legal threats, or human agent requests
  sentiment <text>     Analyze Algerian sentiment (POSITIVE, NEGATIVE, NEUTRAL)
  dialect <text>       Detect Algerian regional dialect (Center, East, West, South)
  quantities <text>    Extract colloquial quantities and product attributes
  agent-prompt <text>  Build grounded prompt for AI LLM agents (GPT-4o, Claude, etc.)
  server               Start zero-dependency HTTP microservice (for n8n, Make, Docker)

Options:
  --json               Output raw JSON
  --port <number>      Port for server (default: 8080)
  --host <string>      Host for server (default: 0.0.0.0)
  --store <string>     Store name for agent-prompt (default: "Bazar El Djazair")
`);
}

function parseArgs(args: string[]) {
  const flags: Record<string, string | boolean> = {};
  const positional: string[] = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--json') {
      flags.json = true;
    } else if (arg === '--port' && i + 1 < args.length) {
      flags.port = args[++i];
    } else if (arg === '--host' && i + 1 < args.length) {
      flags.host = args[++i];
    } else if (arg === '--store' && i + 1 < args.length) {
      flags.store = args[++i];
    } else if (!arg.startsWith('--')) {
      positional.push(arg);
    }
  }

  return { flags, positional };
}

function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || argv.includes('--help') || argv.includes('-h')) {
    printHelp();
    process.exit(0);
  }

  const { flags, positional } = parseArgs(argv);
  const command = positional[0];
  const text = positional.slice(1).join(' ');

  switch (command) {
    case 'parse': {
      if (!text) {
        console.error('Error: Please provide text to parse.');
        process.exit(1);
      }
      const entities = extractEntities(text);
      const res = {
        wilayas: entities.wilayas.map((w) => ({
          code: w.code,
          name_ar: w.nameAr,
          commune: w.commune,
        })),
        prices_dzd: entities.prices.map((p) => ({
          amount: p.amount,
          raw: p.raw,
        })),
        phones: (entities.phones || []).map((ph) => ({
          normalized: ph.normalized,
          operator: ph.operatorLabel,
          whatsapp: ph.whatsappUrl,
        })),
        quantities: (entities.quantities || []).map((q) => ({
          value: q.value,
          unit: q.unit,
          raw: q.raw,
        })),
        attributes: {
          colors: entities.attributes?.colors || [],
          sizes: entities.attributes?.sizes || [],
        },
        delivery: (entities.deliveries || []).map((d) => d.label),
      };

      if (flags.json) {
        console.log(JSON.stringify(res, null, 2));
      } else {
        console.log('=== Algerian Entities Extracted ===');
        if (res.wilayas.length > 0) {
          const wStr = res.wilayas
            .map((w) => `${w.name_ar} (${w.code})` + (w.commune ? ` - بلدية ${w.commune}` : ''))
            .join(', ');
          console.log(`📍 Wilayas: ${wStr}`);
        }
        if (res.prices_dzd.length > 0) {
          const pStr = res.prices_dzd
            .filter((p) => p.amount !== null)
            .map((p) => `${p.amount?.toLocaleString()} DZD (${p.raw})`)
            .join(', ');
          console.log(`💰 Prices: ${pStr}`);
        }
        if (res.phones.length > 0) {
          const phStr = res.phones.map((ph) => `${ph.normalized} [${ph.operator}]`).join(', ');
          console.log(`📞 Phones: ${phStr}`);
        }
        if (res.quantities.length > 0) {
          const qStr = res.quantities.map((q) => `${q.value} ${q.unit} (${q.raw})`).join(', ');
          console.log(`📦 Quantities: ${qStr}`);
        }
        if (res.attributes.colors.length > 0 || res.attributes.sizes.length > 0) {
          console.log(
            `🎨 Attributes: Colors=[${res.attributes.colors.join(', ')}], Sizes=[${res.attributes.sizes.join(', ')}]`
          );
        }
      }
      break;
    }

    case 'intent': {
      if (!text) {
        console.error('Error: Please provide text for intent classification.');
        process.exit(1);
      }
      const res = identifyIntent(text);
      if (flags.json) {
        console.log(
          JSON.stringify(
            {
              intent: res.intent,
              confidence: res.confidence,
              matched_keywords: res.matchedKeywords,
            },
            null,
            2
          )
        );
      } else {
        console.log(`🎯 Intent: ${res.intent} (Confidence: ${res.confidence.toFixed(2)})`);
        console.log(`🔑 Matched Keywords: ${res.matchedKeywords.join(', ')}`);
      }
      break;
    }

    case 'escalation': {
      if (!text) {
        console.error('Error: Please provide text for escalation check.');
        process.exit(1);
      }
      const res = detectEscalation(text);
      if (flags.json) {
        console.log(JSON.stringify(res, null, 2));
      } else {
        const status = res.needsEscalation ? '🚨 ESCALATION REQUIRED' : '✅ NORMAL (No Escalation)';
        console.log(`Status: ${status}`);
        console.log(`Reason: ${res.reason} | Urgency: ${res.urgency}`);
        console.log(`Guideline: ${res.guideline}`);
        if (res.matchedTriggers.length > 0) {
          console.log(`Keywords: ${res.matchedTriggers.join(', ')}`);
        }
      }
      break;
    }

    case 'sentiment': {
      if (!text) {
        console.error('Error: Please provide text for sentiment analysis.');
        process.exit(1);
      }
      const res = analyzeSentiment(text);
      if (flags.json) {
        console.log(JSON.stringify(res, null, 2));
      } else {
        const icon = res.label === 'POSITIVE' ? '😊' : res.label === 'NEGATIVE' ? '😡' : '😐';
        console.log(`Sentiment: ${icon} ${res.label} (Score: ${res.score.toFixed(2)})`);
        if (res.positiveTokens.length > 0) {
          console.log(`Positive terms: ${res.positiveTokens.join(', ')}`);
        }
        if (res.negativeTokens.length > 0) {
          console.log(`Negative terms: ${res.negativeTokens.join(', ')}`);
        }
      }
      break;
    }

    case 'dialect': {
      if (!text) {
        console.error('Error: Please provide text for dialect detection.');
        process.exit(1);
      }
      const res = detectDialect(text);
      if (flags.json) {
        console.log(JSON.stringify(res, null, 2));
      } else {
        console.log(`🗺️ Region: ${res.region} (Confidence: ${res.confidence.toFixed(2)})`);
        console.log(
          `Markers: ${res.detectedMarkers.length > 0 ? res.detectedMarkers.join(', ') : 'None'}`
        );
      }
      break;
    }

    case 'quantities': {
      if (!text) {
        console.error('Error: Please provide text for quantity extraction.');
        process.exit(1);
      }
      const quants = extractQuantities(text);
      const attrs = extractProductAttributes(text);
      if (flags.json) {
        console.log(
          JSON.stringify(
            {
              quantities: quants,
              attributes: attrs,
            },
            null,
            2
          )
        );
      } else {
        console.log(
          '📦 Quantities:',
          quants.map((q) => `${q.value} ${q.unit} (${q.raw})`).join(', ') || 'None'
        );
        console.log(`🎨 Colors: ${attrs.colors.join(', ') || 'None'}`);
        console.log(`📏 Sizes: ${attrs.sizes.join(', ') || 'None'}`);
      }
      break;
    }

    case 'agent-prompt': {
      if (!text) {
        console.error('Error: Please provide customer text for prompt generation.');
        process.exit(1);
      }
      const store = typeof flags.store === 'string' ? flags.store : 'Bazar El Djazair';
      const ctx = buildAgentContext(text, store);
      const prompt = formatAgentSystemPrompt(ctx);
      console.log(prompt);
      break;
    }

    case 'server': {
      const port = flags.port ? parseInt(String(flags.port), 10) : 8080;
      const host = typeof flags.host === 'string' ? flags.host : '0.0.0.0';
      startServer({ host, port });
      break;
    }

    default:
      console.error(`Unknown command: ${command}`);
      printHelp();
      process.exit(1);
  }
}

main();
