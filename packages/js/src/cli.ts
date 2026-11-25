#!/usr/bin/env node
/**
 * Command-Line Interface (CLI) for darja-nlp-kit.
 *
 * Usage:
 *   darja-nlp analyze "salam kho rani hab nchrih b 2 mlayen l wahran 0661234567"
 *   darja-nlp parse "نحوس على 2 حبات مقاس XL نبعثهم لوهران 0661234567"
 *   darja-nlp intent "شحال التوصيل لسطيف؟"
 *   darja-nlp escalation "سراقين حشيتوهالي رجعولي دراهمي"
 *   darja-nlp chat "wach ya khoy"
 *   darja-nlp eval
 *   darja-nlp server --port 8080
 */

import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import { normalize } from './normalizer';
import { arabiziToArabic } from './arabizi';
import { extractEntities } from './entities';
import { identifyIntent } from './intent';
import { detectEscalation } from './escalation';
import { analyzeSentiment } from './sentiment';
import { detectDialect } from './dialect';
import { extractQuantities, extractProductAttributes } from './quantities';
import { detectCulturalReferences, detectMemes } from './cultural';
import { respondToDarja, DialoguePersona, DialogueScript, DialogueStrategy } from './dialogue';
import { detectProfanity, censorProfanity } from './profanity';
import { analyze as runAnalyze } from './pipeline';
import { DarjaAIAgent, buildAgentContext, formatAgentSystemPrompt } from './agent';
import { runMcpServer } from './mcp';
import { startServer } from './server';
import { SentimentMode } from './types';

function printHelp() {
  console.log(`
darja-nlp-kit CLI (Zero-dependency Algerian Darja NLP)

Usage:
  darja-nlp <command> [options] [text]

Commands:
  analyze <text>       Run complete end-to-end NLP analysis
  normalize <text>     Normalize Arabic/Arabizi Darja text
  arabizi <text>       Convert Arabizi text to Arabic script
  parse <text>         Extract Algerian entities (wilayas, communes, phones, prices, quantities)
  intent <text>        Identify customer business intent (ORDER, PRICE, DELIVERY, etc.)
  escalation <text>    Detect angry customers, legal threats, or human agent requests
  sentiment <text>     Analyze Algerian sentiment (POSITIVE, NEGATIVE, NEUTRAL, MIXED)
  dialect <text>       Detect Algerian regional dialect (Center, East, West, South)
  quantities <text>    Extract colloquial quantities and product attributes
  culture <text>       Detect Algerian proverbs, viral memes, landmarks, dishes, and slang
  chat <text>          Generate natural Algerian Darja response (e.g. 'wach ya khoy' -> 'we cv')
  moderate <text>      Detect profanities, toxic slurs, and censor Algerian text
  memes <text>         Detect Algerian viral memes and TV comedy quotes
  eval                 Evaluate sentiment accuracy on held-out real Algerian benchmark
  agent [text]         Run plug-and-play AI Agent (interactive REPL if text omitted)
  mcp                  Start zero-dependency MCP stdio server (Claude/Cursor/Antigravity)
  agent-setup          Generate MCP client configuration & quick installation snippet
  agent-prompt <text>  Build grounded prompt for AI LLM agents (GPT-4o, Claude, etc.)
  server               Start zero-dependency HTTP microservice (for n8n, Make, Docker)

Options:
  --json               Output raw JSON
  --mode <mode>        Sentiment mode: hybrid | lexicon | ml (default: hybrid)
  --persona <p>        Chat persona: casual | merchant | assistant (default: casual)
  --script <s>         Chat script: auto | arabizi | arabic (default: auto)
  --strategy <st>      Chat strategy: auto | rules | retrieval (default: auto)
  --vary               Vary responses instead of picking the top deterministic reply
  --mask <str>         Censor mask for moderate (default: ***)
  --port <number>      Port for server (default: 8080)
  --host <string>      Host for server (default: 0.0.0.0)
  --store <string>     Store name for agent / agent-prompt (default: "Bazar El Djazair")
  --provider <name>    LLM provider: offline | openai | gemini | groq | deepseek | ollama
  --model <name>       Model override for agent command
  --api-key <key>      API key for agent command (or DARJA_API_KEY / OPENAI_API_KEY)
  --out <path>         Optional output JSON path for agent-setup
`);
}

function parseArgs(args: string[]) {
  const flags: Record<string, string | boolean> = {};
  const positional: string[] = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--json' || arg === '--vary') {
      flags[arg.slice(2)] = true;
    } else if (
      ['--port', '--host', '--store', '--mode', '--persona', '--script', '--strategy', '--mask', '--provider', '--model', '--api-key', '--base-url', '--client', '--out'].includes(arg) &&
      i + 1 < args.length
    ) {
      flags[arg.slice(2)] = args[++i];
    } else if (!arg.startsWith('--')) {
      positional.push(arg);
    }
  }

  return { flags, positional };
}

async function main() {
  const argv = process.argv.slice(2);
  if (argv.length === 0 || argv.includes('--help') || argv.includes('-h')) {
    printHelp();
    process.exit(0);
  }

  const { flags, positional } = parseArgs(argv);
  const command = positional[0];
  const text = positional.slice(1).join(' ');

  switch (command) {
    case 'analyze': {
      if (!text) {
        console.error('Error: Please provide text to analyze.');
        process.exit(1);
      }
      const persona = (typeof flags.persona === 'string' ? flags.persona : 'casual') as DialoguePersona;
      const mode = (typeof flags.mode === 'string' ? flags.mode : 'hybrid') as SentimentMode;
      const report = runAnalyze(text, { persona, sentimentMode: mode });
      if (flags.json) {
        console.log(JSON.stringify(report, null, 2));
      } else {
        console.log('=== Darja NLP Unified Analysis ===');
        console.log(`Normalized : ${report.normalized}`);
        if (report.arabic !== report.rawText) console.log(`Arabic     : ${report.arabic}`);
        if (report.sentiment) {
          console.log(`Sentiment  : ${report.sentiment.label} (${report.sentiment.score.toFixed(2)}) [${report.sentiment.method}]`);
        }
        if (report.intent) {
          console.log(`Intent     : ${report.intent.intent} (${report.intent.confidence.toFixed(2)})`);
        }
        if (report.dialect) {
          console.log(`Dialect    : ${report.dialect.region} (${report.dialect.confidence.toFixed(2)})`);
        }
        if (report.entities && report.entities.wilayas.length > 0) {
          console.log('Wilayas    :', report.entities.wilayas.map((w) => `${w.nameAr} (${w.code})`).join(', '));
        }
        if (report.entities && report.entities.prices.length > 0) {
          console.log(
            'Prices DZD :',
            report.entities.prices.filter((p) => p.amount !== null).map((p) => p.amount).join(', ')
          );
        }
        if (report.entities && report.entities.phones && report.entities.phones.length > 0) {
          console.log('Phones     :', report.entities.phones.map((p) => p.normalized).join(', '));
        }
        if (report.profanity && report.profanity.isProfane) {
          console.log(`Moderation : PROFANE (${report.profanity.severity}) -> ${report.profanity.censoredText}`);
        }
        if (report.reply) {
          console.log(`Reply      : ${report.reply.reply} [${report.reply.source}]`);
        }
      }
      break;
    }

    case 'normalize': {
      if (!text) {
        console.error('Error: Please provide text to normalize.');
        process.exit(1);
      }
      const res = normalize(text);
      console.log(flags.json ? JSON.stringify({ input: text, normalized: res }, null, 2) : res);
      break;
    }

    case 'arabizi': {
      if (!text) {
        console.error('Error: Please provide Arabizi text.');
        process.exit(1);
      }
      const res = arabiziToArabic(text);
      console.log(flags.json ? JSON.stringify({ input: text, arabic: res }, null, 2) : res);
      break;
    }

    case 'parse': {
      if (!text) {
        console.error('Error: Please provide text to parse.');
        process.exit(1);
      }
      const entities = extractEntities(text);
      const cult = detectCulturalReferences(text);
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
        cultural: {
          has_cultural_reference: cult.hasCulturalReference,
          summary: cult.hasCulturalReference ? cult.culturalSummary : null,
        },
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
        if (cult.hasCulturalReference) {
          console.log(`🏛️ Culture/Slang: ${cult.culturalSummary}`);
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
        const status = res.needsEscalation ? 'ESCALATION REQUIRED' : 'NORMAL (No Escalation)';
        console.log(`Status: ${status}`);
        console.log(`Reason: ${res.reason} | Urgency: ${res.urgency}`);
        console.log(`Guideline: ${res.guideline}`);
        if (res.matchedTriggers.length > 0) {
          console.log(`Triggers: ${res.matchedTriggers.join(', ')}`);
        }
      }
      break;
    }

    case 'sentiment': {
      if (!text) {
        console.error('Error: Please provide text for sentiment analysis.');
        process.exit(1);
      }
      const mode = (typeof flags.mode === 'string' ? flags.mode : 'hybrid') as SentimentMode;
      const res = analyzeSentiment(text, { mode });
      if (flags.json) {
        console.log(JSON.stringify(res, null, 2));
      } else {
        console.log(`Sentiment: ${res.label} (Score: ${res.score.toFixed(2)}, Method: ${res.method})`);
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

    case 'culture': {
      if (!text) {
        console.error('Error: Please provide text for cultural analysis.');
        process.exit(1);
      }
      const cult = detectCulturalReferences(text);
      const res = {
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
      };

      if (flags.json) {
        console.log(JSON.stringify(res, null, 2));
      } else {
        console.log('=== Algerian Cultural References & Slang ===');
        console.log(`Has Reference : ${res.has_cultural_reference ? 'Yes' : 'No'}`);
        console.log(`Summary       : ${res.cultural_summary}`);
        if (res.proverbs.length > 0) console.log(`Proverbs      : ${res.proverbs.map((p) => p.canonical_name).join(', ')}`);
        if (res.memes_and_trends.length > 0) console.log(`Memes/Trends  : ${res.memes_and_trends.map((m) => m.canonical_name).join(', ')}`);
        if (res.landmarks.length > 0) console.log(`Landmarks     : ${res.landmarks.map((l) => l.canonical_name).join(', ')}`);
        if (res.gastronomy.length > 0) console.log(`Gastronomy    : ${res.gastronomy.map((g) => g.canonical_name).join(', ')}`);
        if (res.slang_expressions.length > 0) console.log(`Slang Terms   : ${res.slang_expressions.map((s) => s.canonical_name).join(', ')}`);
      }
      break;
    }

    case 'chat': {
      if (!text) {
        console.error('Error: Please provide a message for chat response.');
        process.exit(1);
      }
      const persona = (typeof flags.persona === 'string' ? flags.persona : 'casual') as DialoguePersona;
      const script = (typeof flags.script === 'string' ? flags.script : 'auto') as DialogueScript;
      const strategy = (typeof flags.strategy === 'string' ? flags.strategy : 'auto') as DialogueStrategy;
      const vary = Boolean(flags.vary);
      const res = respondToDarja(text, { persona, script, strategy, vary });
      if (flags.json) {
        console.log(JSON.stringify(res, null, 2));
      } else {
        console.log('=== Algerian Conversational Response ===');
        console.log(`Reply          : ${res.reply}`);
        console.log(`Intent         : ${res.intent}`);
        console.log(`Script         : ${res.script}`);
        console.log(`Source         : ${res.source}`);
        console.log(`Confidence     : ${res.confidence.toFixed(2)}`);
      }
      break;
    }

    case 'moderate': {
      if (!text) {
        console.error('Error: Please provide text to moderate.');
        process.exit(1);
      }
      const mask = typeof flags.mask === 'string' ? flags.mask : '***';
      const res = detectProfanity(text);
      const censored = censor_profanity_compat(text, mask);
      const output = {
        is_profane: res.isProfane,
        severity: res.severity,
        matches_count: res.matches.length,
        matches: res.matches.map((m) => ({
          term: m.term,
          category: m.category,
          severity: m.severity,
          matched_text: m.matchedText,
        })),
        censored_text: censored,
      };
      if (flags.json) {
        console.log(JSON.stringify(output, null, 2));
      } else {
        console.log('=== Content Moderation & Profanity Check ===');
        console.log(`Is Profane     : ${res.isProfane ? 'Yes' : 'No'}`);
        console.log(`Severity       : ${res.severity.toUpperCase()}`);
        console.log(`Matches        : ${res.matches.length}`);
        console.log(`Censored Text  : ${censored}`);
      }
      break;
    }

    case 'memes': {
      if (!text) {
        console.error('Error: Please provide text to detect memes.');
        process.exit(1);
      }
      const memes = detectMemes(text);
      const output = memes.map((m) => ({
        phrase: m.canonicalName,
        meaning: m.meaning,
        metadata: m.metadata,
      }));
      if (flags.json) {
        console.log(JSON.stringify(output, null, 2));
      } else {
        console.log('=== Algerian Memes & Pop-Culture ===');
        if (memes.length === 0) {
          console.log('No viral memes detected in text.');
        }
        for (const m of memes) {
          console.log(`Meme: ${m.canonicalName}`);
          console.log(`  Meaning: ${m.meaning}`);
          if (m.metadata?.origin) console.log(`  Origin : ${m.metadata.origin}`);
        }
      }
      break;
    }

    case 'eval': {
      const mode = (typeof flags.mode === 'string' ? flags.mode : 'hybrid') as SentimentMode;
      const benchPath = path.resolve(__dirname, '../data/eval_benchmark.json');
      if (!fs.existsSync(benchPath)) {
        console.error('Error: eval_benchmark.json not found in package data.');
        process.exit(1);
      }
      const bench = JSON.parse(fs.readFileSync(benchPath, 'utf-8')).sentiment || [];
      const bySource: Record<string, { correct: number; total: number }> = {};
      let ok = 0;
      for (const row of bench) {
        let pred = analyzeSentiment(row.text, { mode }).label;
        if (pred === 'MIXED') pred = 'NEUTRAL';
        const src = row.source || 'unknown';
        if (!bySource[src]) bySource[src] = { correct: 0, total: 0 };
        bySource[src].total++;
        if (pred === row.label) {
          ok++;
          bySource[src].correct++;
        }
      }
      const acc = bench.length ? Math.round((ok / bench.length) * 10000) / 10000 : 0;
      const summary = {
        mode,
        total: bench.length,
        correct: ok,
        accuracy: acc,
        by_source: Object.fromEntries(
          Object.entries(bySource).map(([k, v]) => [
            k,
            { ...v, accuracy: Math.round((v.correct / v.total) * 10000) / 10000 },
          ])
        ),
      };
      if (flags.json) {
        console.log(JSON.stringify(summary, null, 2));
      } else {
        console.log(`=== Held-Out Sentiment Benchmark (mode=${mode}) ===`);
        console.log(`Overall Accuracy : ${ok}/${bench.length} (${(acc * 100).toFixed(2)}%)`);
        for (const [src, st] of Object.entries(summary.by_source)) {
          console.log(`  - ${src.padEnd(20)}: ${st.correct}/${st.total} (${(st.accuracy * 100).toFixed(2)}%)`);
        }
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

    case 'agent': {
      const agent = new DarjaAIAgent({
        storeName: typeof flags.store === 'string' ? flags.store : 'Bazar El Djazair',
        persona: (typeof flags.persona === 'string' ? flags.persona : 'merchant') as DialoguePersona,
        provider: typeof flags.provider === 'string' ? flags.provider : undefined,
        apiKey: typeof flags['api-key'] === 'string' ? flags['api-key'] : undefined,
        model: typeof flags.model === 'string' ? flags.model : undefined,
        baseUrl: typeof flags['base-url'] === 'string' ? flags['base-url'] : undefined,
      });
      if (text) {
        const res = await agent.ask(text);
        if (flags.json) {
          console.log(JSON.stringify(res, null, 2));
        } else {
          console.log(`[${res.provider}:${res.model}] (${res.intent} | ${res.dialect})`);
          console.log(`Agent > ${res.reply}`);
          if (res.missingSlots.length && !res.needsEscalation) {
            console.log(`Slots missing: ${res.missingSlots.join(', ')}`);
          }
        }
      } else {
        console.log(`=== DarjaAIAgent Interactive Chat (${agent.provider}:${agent.model}) ===`);
        console.log('Type customer messages in Arabic/Arabizi. Commands: /slots, /reset, /exit');
        const rl = readline.createInterface({ input: process.stdin, output: process.stdout, prompt: 'You > ' });
        rl.prompt();
        for await (const rawLine of rl) {
          const line = rawLine.trim();
          if (!line) { rl.prompt(); continue; }
          if (['/exit', 'exit', 'quit'].includes(line)) { rl.close(); break; }
          if (line === '/reset') { agent.reset(); console.log('[session reset]'); rl.prompt(); continue; }
          if (line === '/slots') { console.log(JSON.stringify(agent.slots, null, 2)); rl.prompt(); continue; }
          const res = await agent.ask(line);
          console.log(`Agent [${res.intent}] > ${res.reply}`);
          rl.prompt();
        }
      }
      break;
    }

    case 'mcp': {
      runMcpServer();
      break;
    }

    case 'agent-setup': {
      const cfg = {
        mcpServers: {
          'darja-nlp': {
            command: process.execPath,
            args: [path.resolve(__dirname, 'cli.js'), 'mcp'],
          },
        },
      };
      if (typeof flags.out === 'string') {
        const outPath = path.resolve(flags.out);
        fs.mkdirSync(path.dirname(outPath), { recursive: true });
        fs.writeFileSync(outPath, JSON.stringify(cfg, null, 2) + '\n', 'utf-8');
      }
      if (flags.json) {
        console.log(JSON.stringify(cfg, null, 2));
      } else {
        console.log('=== darja-nlp-kit AI Agent Setup (Node.js) ===');
        console.log('MCP Server Config (Claude Desktop / Cursor / VS Code / Antigravity):');
        console.log(JSON.stringify(cfg, null, 2));
        if (typeof flags.out === 'string') console.log(`\n[SAVED] Wrote MCP config to: ${flags.out}`);
      }
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

function censor_profanity_compat(text: string, mask: string): string {
  return censorProfanity(text, mask);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
