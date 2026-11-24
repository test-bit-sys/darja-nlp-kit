<div align="center">
  <a href="https://test-bit-sys.github.io/darja-nlp-kit/">
    <img src="https://raw.githubusercontent.com/test-bit-sys/darja-nlp-kit/main/assets/logo.jpg?v=2" alt="darja-nlp-kit logo" width="190" />
  </a>
  <h1>darja-nlp-kit</h1>
  <p><strong>Zero-dependency, dual-language (TypeScript & Python) NLP toolkit for Algerian Darja</strong></p>

  <p>
    <a href="https://github.com/test-bit-sys/darja-nlp-kit/actions/workflows/ci.yml"><img src="https://github.com/test-bit-sys/darja-nlp-kit/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
    <a href="https://test-bit-sys.github.io/darja-nlp-kit/"><img src="https://img.shields.io/badge/Live_Demo-Playground-10b981.svg" alt="Live Demo" /></a>
    <a href="https://www.npmjs.com/package/@dz-open-suite/darja-nlp-kit"><img src="https://img.shields.io/npm/v/@dz-open-suite/darja-nlp-kit.svg" alt="npm version" /></a>
    <a href="https://pypi.org/project/darja-nlp-kit/"><img src="https://img.shields.io/pypi/v/darja-nlp-kit.svg" alt="PyPI version" /></a>
    <a href="#"><img src="https://img.shields.io/badge/dependencies-0-brightgreen.svg" alt="Zero Dependencies" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" /></a>
  </p>
  <p>
    <strong><a href="https://test-bit-sys.github.io/darja-nlp-kit/">Interactive Web Playground &rarr;</a></strong>
  </p>
</div>

Zero-dependency, dual-language (TypeScript & Python) NLP toolkit for **Algerian Darja** (Derja) — part of the **DZ Open Suite** ecosystem.

Handles Arabic script, Arabizi (Latin transliteration with numbers), and French/Arabic code-switching common in Algerian e-commerce, social media, and daily communication.

## Features

- **Unified Ergonomic Pipeline (`DarjaPipeline` & `analyze()`)** — Run normalization, Arabizi transliteration, hybrid ML sentiment, intent, regional dialect, entities, escalation, moderation, cultural analysis, and natural replies in a single customizable call with `.extendLexicon()`, `.addStopwords()`, `.addProfanity()`, `.addDialogueRule()`, and batch support
- **Zero-Dependency Custom Classifier (`DarjaClassifier`)** — Built-in Naive Bayes (unigram, bigram, and character subword features) with `.fit()`, `.partialFit()` / `.partial_fit()`, `.evaluate()` (accuracy & macro-F1), and JSON serialization (`toJSON`/`fromJSON` and `to_dict`/`from_dict`) interoperable between Python and Node.js
- **Stateful Multi-Turn Chat Session (`DarjaChat`)** — Turn-by-turn customer session that accumulates entities (wilayas, phones, quantities, colors, sizes, prices, payments, carriers), tracks detected script/dialect, detects human escalation, and prompts only for missing order slots
- **Hybrid 55K-Trained Sentiment Engine + Built-In Benchmark** — Combines multi-word Darja lexicon rules (536 positive/negative entries, circumfix negation, double negation, intensifiers) with an 8,000-feature ML linear classifier (`data/sentiment_model.json`) trained on 55,732 authentic Algerian samples; configurable `mode` (`'hybrid' | 'ml' | 'lexicon'`) and reproducible CLI `eval` command (`70.83%` ML / `68.00%` hybrid across 600 held-out Algerian test samples)
- **Conversational Dialogue & KB Retrieval (`respondToDarja`)** — Authentic colloquial response engine (e.g., `wach ya khoy` $\rightarrow$ `We cv hamdoulah w nta kho? Koulchi mlih?`), automatic Arabic/Arabizi script parity, multiple personas (`casual`, `merchant`, `assistant`), `customRules`, and zero-dependency TF-IDF cosine retrieval over 599 grounded Algerian entries (`data/dialogue_kb.json` from `DziriAlign`, `DziriEval`, and e-commerce dialogues)
- **Content Moderation & Profanity Shield** — Filter and censor 36 categorized Algerian profanity entries (Arabic & Arabizi variants with 7/3/9/2/5 digit substitutions), severity grading (`low`, `medium`, `high`), and runtime `customTerms`
- **Algeria-Geo 69 Wilayas & 1,541 Communes** — 100% synchronized with [`algeria-geo`](https://github.com/test-bit-sys/algeria-geo), covering all 69 official Wilayas (Law 26-06 reform including 59–69: Aflou through El Abiodh Sidi Cheikh), 538 Dairas, and 1,541 Communes with fast pre-filtered extraction
- **Franco-Darja Lexicon & Algerian Memes** — 60 Franco-Darja loanwords and hybrid verbs (`ncommandi`, `caba`, `dispo`, `mrigel`, `pointure`), 30 iconic Algerian memes (`memes.json`), plus 76 cultural entries (29 proverbs, 15 viral trends, 17 landmarks/markets, 15 dishes) and 37 street/commercial slang expressions
- **Text Normalization & Arabizi-to-Arabic Transliteration** — Unify Arabic letter variants, strip diacritics, reduce elongation, preserve standalone prices/phones, and transliterate Arabizi using 157 irregular overrides and a 252-word French loanwords whitelist
- **Stopword Removal & Mixed-Script Tokenization** — 592 categorized Algerian Darja stopwords (Arabic script + Arabizi) with prefix stripping and `ما...ش` / `ma...ch` circumfix negation detection
- **Algerian Logistics, Operators & Darja Prices (`doro` / `melyoun`)** — Extract carriers (Yalidine, ZR Express, Maystro, Procolis, EMS, Kazitour, Guepex), delivery mode (Stop Desk / Home Delivery), phone operators (`MOBILIS`, `DJEZZY`, `OOREDOO`, `ALGERIE_TELECOM`) with WhatsApp deep links, payments (BaridiMob, Edahabia, CCP, COD), colloquial quantities (`دوزينة` = 12, `حبة`, `شكارة`), attributes (sizes/colors), and colloquial currencies (`50 دورو` $\rightarrow$ 250 DZD, `15 melyoun` $\rightarrow$ 150,000 DZD, `زوج ملاين` $\rightarrow$ 20,000 DZD)
- **Regional Dialect Identification** — Token-accurate detection across `WEST`, `EAST`, `CENTER`, `SOUTH`, and `GENERAL_DARJA` using merged regional markers from `data/dialects.json`
- **Smart Human Escalation Engine** — Detect angry customers, human-agent requests, and legal threats with urgency levels (`CRITICAL`, `HIGH`, `MEDIUM`)
- **Authentic Algerian LLM Fine-Tuning & DPO Corpora** — 8,628 supervised instruction/chat/cultural samples in Alpaca, ShareGPT, and OpenAI JSONL formats, plus 1,000 Algerian DPO preference pairs (`DziriAlign`) and 3,000 parallel Darja-English translation pairs
- **Zero-Dependency CLI & Local HTTP Microservice** — Ready-to-run CORS-enabled REST API (including `POST /api/analyze` and `POST /api/batch`) and CLI subcommands (`analyze`, `normalize`, `arabizi`, `parse`, `intent`, `escalation`, `sentiment`, `culture`, `eval`, `server`) for n8n, Make.com, webhooks, and AI agents (6 OpenAI Tool Definitions included)

## Installation

### Python

```bash
cd packages/python
pip install -e .
```

Or via PyPI:
```bash
pip install darja-nlp-kit
```

### TypeScript / JavaScript

```bash
cd packages/js
npm install
npm run build
```

Or via npm:
```bash
npm install @dz-open-suite/darja-nlp-kit
```

### Data Sync

Both packages consume shared linguistic data from `/data`. Run the sync script after any data changes:

```bash
python scripts/sync_data.py
```

## API Reference

### `normalize(text, options?)`

Normalizes Algerian Darja text by unifying Arabic letter forms and cleaning noise.

**Transformations:**
- Alef variants (أ, إ, آ) to bare alef (ا)
- Ta marbuta (ة) to ha (ه)
- Alef maqsura (ى) to ya (ي)
- Strip tashkeel (diacritics) and tatweel (kashida)
- Reduce character elongation (بزاااااف to بزاف, haaaayel to hayel)
- Normalize whitespace and punctuation

**TypeScript:**
```typescript
import { normalize } from '@dz-open-suite/darja-nlp-kit';

normalize('بِسْمِ اللَّهِ');
// => 'بسم الله'

normalize('كتـــاب');
// => 'كتاب'

normalize('بزاااااف');
// => 'بزاف'

normalize('haaaayel');
// => 'hayel'
```

**Python:**
```python
from darja_nlp import normalize

normalize('بِسْمِ اللَّهِ')
# => 'بسم الله'

normalize('بزاااااف')
# => 'بزاف'
```

**Options:**

| Option | Type | Default | Description |
|---|---|---|---|
| `preserveTashkeel` / `preserve_tashkeel` | boolean | `false` | Keep Arabic diacritics |
| `preserveLength` / `preserve_length` | boolean | `false` | Keep character repetitions |

---

### `arabiziToArabic(text, options?)` / `arabizi_to_arabic(text, options?)`

Converts Arabizi (Latin-script Algerian Arabic) to Arabic script with smart code-switching awareness.

**Features:**
- French loanword preservation via whitelist + suffix heuristics (`-tion`, `-ment`, `-eur`, `-ique`)
- French words containing Arabizi digraphs (`achat`, `chambre`, `douche`, `marche`, `couleur`, `bouton`, `retour`, `choix`, `chargeur`, `compte`, `boutique`) are preserved intact
- Irregular Darja dictionary overrides (`slm`, `cv`, `nchallah`, `hamdoulah`, `2ana`)
- Digraph mappings applied before single characters (`ch`, `kh`, `gh`, `sh`, `ou`, `th`, `dh`)
- Context-sensitive number conversion (`3` to ع, `7` to ح, `9` to ق) only when adjacent to letters
- Standalone numbers (prices, phone numbers, postal codes) are preserved intact

**TypeScript:**
```typescript
import { arabiziToArabic } from '@dz-open-suite/darja-nlp-kit';

arabiziToArabic('Prix 2500 DA w livraison l 16');
// => 'Prix 2500 دا و livraison ل 16' (numbers 2500 and 16 preserved)

arabiziToArabic('2ana 9rib');
// => 'انا قريب'

arabiziToArabic('produit mli7 livraison rapide');
// => 'produit مليح livraison rapide' (French words preserved)

arabiziToArabic('slm cv?');
// => 'سلام صافا?'
```

**Python:**
```python
from darja_nlp import arabizi_to_arabic

arabizi_to_arabic('Prix 2500 DA w livraison l 16')
# => 'Prix 2500 دا و livraison ل 16'

arabizi_to_arabic('2ana 9rib')
# => 'انا قريب'
```

**Options:**

| Option | Type | Default | Description |
|---|---|---|---|
| `preserveFrench` / `preserve_french` | boolean | `true` | Keep detected French words intact |

---

### `tokenize(text)`

Tokenizes mixed Arabic/Latin text and detects Algerian circumfix negation patterns (`ما...ش` / `ma...ch`).

**TypeScript:**
```typescript
import { tokenize } from '@dz-open-suite/darja-nlp-kit';

const result = tokenize('مافهمتش الحاجة');
// result.tokens => ['مافهمتش', 'الحاجة']
// result.negations => [{ original: 'مافهمتش', root: 'فهمت', negated: true }]
```

**Python:**
```python
from darja_nlp import tokenize

result = tokenize('مافهمتش الحاجة')
# result.tokens => ['مافهمتش', 'الحاجة']
# result.negations[0].root => 'فهمت'
```

---

### `removeStopwords(text)` / `remove_stopwords(text)`

Removes Algerian Darja stopwords from text with support for common Arabic prefix stripping (`ال`, `ب`, `و`, `ل`). Handles both Arabic script and Arabizi.

**TypeScript:**
```typescript
import { removeStopwords, isStopword } from '@dz-open-suite/darja-nlp-kit';

isStopword('بالزربة');
// => true

removeStopwords('المنتوج هايل بالزربة');
// => 'المنتوج هايل'

removeStopwords('had produit ta3 hayel');
// => 'produit hayel'
```

**Python:**
```python
from darja_nlp import remove_stopwords, is_stopword

is_stopword('بالزربة')
# => True

remove_stopwords('المنتوج هايل بالزربة')
# => 'المنتوج هايل'
```

---

### `analyzeSentiment(text)` / `analyze_sentiment(text)`

Analyzes sentiment with support for negation inversion, double negation, intensifiers, Arabic prefixes, and code-switching.

**Returns:**

| Field | Type | Description |
|---|---|---|
| `score` | number | Aggregated score between -1.0 and +1.0 |
| `label` | string | `POSITIVE`, `NEGATIVE`, `NEUTRAL`, or `MIXED` |
| `positiveTokens` / `positive_tokens` | string[] | Words contributing positively |
| `negativeTokens` / `negative_tokens` | string[] | Words contributing negatively |
| `negated` | boolean | Whether negation was detected |

**TypeScript:**
```typescript
import { analyzeSentiment } from '@dz-open-suite/darja-nlp-kit';

// Double negation: properly inverts negative to POSITIVE
analyzeSentiment('ماشي عيان');
// => { score: 0.68, label: 'POSITIVE', positiveTokens: ['عيان'], negativeTokens: [], negated: true }

analyzeSentiment('machi 3ayan');
// => { score: 0.68, label: 'POSITIVE', positiveTokens: ['3ayan'], negativeTokens: [], negated: true }

// Prefix support on nouns and adjectives
analyzeSentiment('المنتوج هايل');
// => { score: 0.9, label: 'POSITIVE', positiveTokens: ['هايل'], negativeTokens: [], negated: false }

// Intensifier scaling
analyzeSentiment('هايل بزاف');
// => { score: 0.9, label: 'POSITIVE', ... }

// Mixed reviews
analyzeSentiment('هايل بصح غالي');
// => { label: 'MIXED', positiveTokens: ['هايل'], negativeTokens: ['غالي'], ... }
```

**Python:**
```python
from darja_nlp import analyze_sentiment

result = analyze_sentiment('ماشي عيان')
# result.label == 'POSITIVE'
# result.score > 0
# result.negated == True

result = analyze_sentiment('المنتوج هايل')
# result.label == 'POSITIVE'
# result.score == 0.9
```

---

### `extractEntities(text)` / `extract_entities(text)`

Extracts Algerian entities:
- **Wilayas (69 Provinces) & 550+ Communes**: Matches by postal codes (`16`, `31`, `w16`), Arabic/French names (`الجزائر`, `Alger`, `بوسعادة`), popular aliases (`البهجة`, `الباهية`, `سيرتا`), and **550+ major Algerian communes** (e.g. `Rouiba`, `El Eulma`, `Ain El Turk`, `Hassi Messaoud`) which automatically resolve to their parent Wilaya with a `commune` property. Fully compliant with Law 26-06.
- **Payment Methods**: `BARIDIMOB`, `EDAHABIA` (البطاقة الذهبية), `CCP`, `COD` (الدفع عند الاستلام).
- **Compound Colloquial Prices**: Accurately parses compound Algerian centimes and dinars:
  - `زوج ملاين و خمسمية الف` / `2 mlayen w 500 alf` $\rightarrow$ 25,000 DZD
  - `زوج ملاين و خمسين الف` $\rightarrow$ 20,500 DZD
  - `مليون و ميتين الف` $\rightarrow$ 12,000 DZD
- **Delivery Carriers & Modes**: `YALIDINE`, `ZR_EXPRESS`, `MAYSTRO`, `PROCOLIS`, `EMS`, `KAZITOUR`, `GUEPEX`, plus `STOP_DESK` (استلام من المكتب) vs `HOME_DELIVERY` (توصيل للدار).
- **Phone Numbers**: Normalizes mobile/landline numbers (`05xx`, `06xx`, `07xx`, `+213`, `00213`) to standard 10-digit format.

**TypeScript:**
```typescript
import { extractEntities } from '@dz-open-suite/darja-nlp-kit';

const res = extractEntities('livrili l Rouiba b 2 mlayen w 500 alf b yalidine stop desk num: 0555123456');
// res.wilayas => [{ code: 16, codeStr: '16', nameAr: 'الجزائر', nameFr: 'Alger', commune: 'Rouiba', matchedText: 'Rouiba' }]
// res.prices => [{ raw: '2 mlayen w 500 alf', amount: 25000, currency: 'DZD' }]
// res.deliveries => [{ company: 'YALIDINE', label: 'Yalidine Express (ياليدين)', matchedText: 'yalidine' }]
// res.deliveryMode => { mode: 'STOP_DESK', label: 'Stop Desk (استلام من المكتب)' }
// res.phones => [{ raw: '0555123456', normalized: '0555123456' }]
```

**Python:**
```python
from darja_nlp import extract_entities

res = extract_entities('livrili l Rouiba b 2 mlayen w 500 alf b yalidine stop desk num: 0555123456')
# res.wilayas[0].code == 16
# res.wilayas[0].commune == 'Rouiba'
# res.prices[0].amount == 25000.0
# res.deliveries[0].company == 'YALIDINE'
# res.delivery_mode.mode == 'STOP_DESK'
# res.phones[0].normalized == '0555123456'
```

---

### `identifyIntent(text)` / `identify_intent(text)`

Classifies the customer's operational intent in Algerian Arabic / Arabizi / French code-switching:
- `ORDER`: طلب شراء أو حجز (e.g. *حاب نكوموندي*, *rani baghi nchri*, *ابعثوهالي للدار*)
- `PRICE_INQUIRY`: استفسار عن السعر (e.g. *بشحال هادي*, *شحال السومة*, *bch7al*, *c combien*)
- `AVAILABILITY_INQUIRY`: استفسار عن توفر السلعة والكمية (e.g. *كاينة منها*, *مازالت ديسبو*, *fih stock*)
- `DELIVERY_INQUIRY`: استفسار عن التوصيل والشحن (e.g. *شحال ليفريزون*, *وقتاش تلحق*, *كاين توصيل للدار*)
- `COMPLAINT`: شكوى أو استرجاع (e.g. *سلعة مكسرة*, *حشيتوهالي*, *روتور*, *سلعة عيانة*)
- `GREETING`: تحية وتواصل (e.g. *السلام عليكم*, *واش راك خويا*, *salam*, *azul*)
- `UNKNOWN`: غير محدد

**TypeScript:**
```typescript
import { identifyIntent } from '@dz-open-suite/darja-nlp-kit';

identifyIntent('سلام خاوتي حاب نكوموندي زوج حبات ابعثهالي للدار');
// => { intent: 'ORDER', confidence: 0.9, matchedKeywords: ['حاب', 'ابعثهالي'] }

identifyIntent('بشحال هاذي خاوة السومة تاعها؟');
// => { intent: 'PRICE_INQUIRY', confidence: 0.9, matchedKeywords: ['بشحال', 'السومة'] }
```

**Python:**
```python
from darja_nlp import identify_intent

res = identify_intent('سلام خاوتي حاب نكوموندي زوج حبات ابعثهالي للدار')
# res.intent == 'ORDER'
# res.confidence >= 0.8
```

---

### `detectDialect(text)` / `detect_dialect(text)`

Identifies regional Algerian dialect variants based on distinctive vocabulary:
- `WEST`: Oran, Tlemcen, Mostaganem (شوالا، شاكاين، غايا، باغي، حرز، درك، شراكم...)
- `EAST`: Constantine, Setif, Batna, Annaba (واشنهي، قداش، ياسر، ضرك، زي، باهي...)
- `CENTER`: Algiers, Blida, Tipaza, Boumerdes (واشنو، حكاية، دروك، هكدا، حوايج...)
- `SOUTH`: Adrar, Ghardaia, Ouargla, Bechar (واه، لاه، حتة...)
- `GENERAL_DARJA`: Neutral or common Algerian text

**TypeScript:**
```typescript
import { detectDialect } from '@dz-open-suite/darja-nlp-kit';

detectDialect('شوالا راك باغي خوية غايا؟');
// => { region: 'WEST', confidence: 0.9, detectedMarkers: ['شوالا', 'باغي', 'غايا'] }

detectDialect('واشنهي هادا قداش يدير ياسر باهي');
// => { region: 'EAST', confidence: 0.9, detectedMarkers: ['واشنهي', 'قداش', 'ياسر', 'باهي'] }
```

**Python:**
```python
from darja_nlp import detect_dialect

res = detect_dialect('شوالا راك باغي خوية غايا؟')
# res.region == 'WEST'
# res.confidence >= 0.9
```

## Data Files

All linguistic data lives in `/data` and is synced to both packages:

| File | Description |
|---|---|
| `wilayas.json` | All 69 Algerian Wilayas with Arabic/French names, codes, popular aliases, and **550+ commercial communes** |
| `dialects.json` | Dialect regions (WEST, EAST, CENTER, SOUTH, GENERAL_DARJA) with vocabulary markers, greetings, closure, and tone guides |
| `dialogues.json` | 100+ authentic multi-dialect Algerian customer-merchant dialogues across 7 intents and domains |
| `stopwords.json` | 590+ categorized regional and general stopwords across 13 grammatical categories |
| `lexicon.json` | Algerian sentiment dictionary with 410+ authentic positive/negative phrases, idioms, 33 negators, and 44 intensifiers |
| `arabizi_rules.json` | Transliteration rules, 240+ French whitelist terms, and 130+ irregular Darja overrides |
| `data/fine_tuning/` | Pre-exported AI training datasets: `alpaca_darja.json`, `sharegpt_darja.json`, `openai_finetune_darja.jsonl` |

### `getFewShotDialogues(region, intent, limit)` & Dialect Grounding

Retrieves real-world customer-merchant dialogues tailored to the customer's region and intent to anchor LLMs in authentic Algerian phrasing:

**TypeScript:**
```typescript
import { getFewShotDialogues, getDialectMetadata } from '@dz-open-suite/darja-nlp-kit';

// 1. Get regional metadata
const westInfo = getDialectMetadata('WEST');
// westInfo.name_ar => "لهجة الغرب الجزائري (الوهراني / التلمساني / المستغانمي)"

// 2. Retrieve authentic few-shot dialogues
const dialogues = getFewShotDialogues('WEST', 'ORDER', 2);
// dialogues[0].customerMessage => "خويا باغي نكوموندي زوج حبات كيت بلوتوث لوهران درك..."
// dialogues[0].merchantResponse => "مرحبا بيك خويا في وهران الباهية! زوج حبات نحسبهملك 4,400 دج..."
```

**Python:**
```python
from darja_nlp import get_few_shot_dialogues, get_dialect_metadata

# Retrieve real few-shot dialogues from the dataset
dialogues = get_few_shot_dialogues(region='EAST', intent='PRICE_INQUIRY', limit=2)
# dialogues[0]['customer_message'] -> "عيشك خويا قداش السومة تاع هاد لفيستا الكحلة؟"
# dialogues[0]['merchant_response'] -> "يعيشك خويا العزيز ومرحبا بيك! السومة تاع لفيستا راهي 6,800 دج..."
```

### LLM Fine-Tuning Pipeline (Alpaca, ShareGPT, OpenAI JSONL)

`darja-nlp-kit` provides ready-to-train datasets and fine-tuning scripts to train Llama-3, Mistral, Qwen, or OpenAI models on authentic Algerian Darja:

- **Alpaca Format**: `data/fine_tuning/alpaca_darja.json`
- **ShareGPT Format**: `data/fine_tuning/sharegpt_darja.json`
- **OpenAI Fine-Tuning**: `data/fine_tuning/openai_finetune_darja.jsonl`
- **Training Guide & Script**: `examples/fine_tune_llama_darja.py` (Unsloth & Hugging Face TRL SFTTrainer)

```bash
# Export or regenerate datasets
python scripts/export_datasets.py

# Run LoRA/QLoRA fine-tuning on Llama-3-8B
python examples/fine_tune_llama_darja.py
```

### `buildAgentContext(message)` & `formatAgentSystemPrompt(context)`

Empower AI models (GPT-4o, Claude, Gemini, Llama) to act as realistic Algerian customer representatives. Extracts grounded facts (exact DZD price, confirmed Wilaya, delivery carrier, phone) and generates a dialect-mirroring, tone-calibrated system prompt with zero hallucinations.

**Python:**
```python
from darja_nlp import build_agent_context, format_agent_system_prompt

# 1. Build structured ground-truth context
ctx = build_agent_context(
    "salam khoya hab nchrih b 2 mlayen l Constantine b yalidine stop desk. num: 0661234567"
)

# 2. Generate enriched system prompt for LLM
prompt = format_agent_system_prompt(ctx)
# -> Ready to be sent to OpenAI / Anthropic / Gemini API
```

**TypeScript:**
```typescript
import { buildAgentContext, formatAgentSystemPrompt } from '@dz-open-suite/darja-nlp-kit';

const ctx = buildAgentContext(
  'salam khoya hab nchrih b 2 mlayen l Constantine b yalidine stop desk. num: 0661234567'
);
const prompt = formatAgentSystemPrompt(ctx);
```

### `detectEscalation(text)` — Smart Human Escalation & Agent Handoff

Detects when an Algerian customer conversation requires human agent takeover, classifying urgency (`CRITICAL`, `HIGH`, `MEDIUM`, `NONE`) and reason (`LEGAL_THREAT`, `ANGRY_CUSTOMER`, `HUMAN_REQUESTED`, `DISPUTE`).

```typescript
import { detectEscalation } from '@dz-open-suite/darja-nlp-kit';

detectEscalation('سراقين حشيتوهالي رجعولي دراهمي');
// => {
//   needsEscalation: true,
//   urgency: 'HIGH',
//   reason: 'ANGRY_CUSTOMER',
//   matchedTriggers: ['سراقين', 'حشيتوهالي', 'رجعولي دراهمي'],
//   guideline: '⚠️ الزبون غاضب جداً ويتهم المتجر بسوء النية أو السرقة. يجب تدخل عون بشري...'
// }

detectEscalation('نشكي بيكم للعدالة ولابوليس');
// => { needsEscalation: true, urgency: 'CRITICAL', reason: 'LEGAL_THREAT', ... }
```

### `extractQuantities(text)` & `extractProductAttributes(text)`

Extracts colloquial Algerian quantities and product specifications (colors, clothing sizes XS-3XL, shoe sizes 35-48).

```typescript
import { extractQuantities, extractProductAttributes } from '@dz-open-suite/darja-nlp-kit';

extractQuantities('حاب زوج حبات و 3 شكاير و دوزينة');
// => [
//   { raw: 'زوج حبات', value: 2, unit: 'حبة' },
//   { raw: '3 شكاير', value: 3, unit: 'شكارة' },
//   { raw: 'دوزينة', value: 12, unit: 'دوزينة' }
// ]

extractProductAttributes('بيجاما كحلة وبيضا مقاس XL وبونتير 42');
// => {
//   colors: ['كحل / noir', 'بيض / blanc'],
//   sizes: ['XL', '42']
// }
```

### Telecom Operator Routing & WhatsApp Deep Links

Automatically classifies Algerian phone numbers by telecom operator and creates 1-click WhatsApp chat links:

```typescript
import { extractEntities } from '@dz-open-suite/darja-nlp-kit';

const res = extractEntities('اتصل بي على 0661234567');
// res.phones[0]:
// {
//   normalized: '0661234567',
//   operator: 'MOBILIS',
//   operatorLabel: 'Mobilis (موبيليس)',
//   formatted: '+213 661 23 45 67',
//   whatsappUrl: 'https://wa.me/213661234567'
// }
```

### `detectCulturalReferences(text)` — Proverbs, Memes, Landmarks, Gastronomy & Slang

Zero-dependency cultural and linguistic knowledge extraction. Detects classic proverbs, viral memes, historical landmarks/markets, traditional gastronomy dishes, and street/commercial slang expressions.

**Python:**
```python
from darja_nlp import detect_cultural_references

res = detect_cultural_references("طاح الحك وصاب غطاه ابعثلي رشتة عاصمية لباب الواد")
# res.has_cultural_reference -> True
# res.proverbs[0].canonical_name -> "طاح الحك وصاب غطاه"
# res.landmarks[0].canonical_name -> "ساحة الشهداء وباب الواد"
# res.gastronomy[0].canonical_name -> "الرشتة العاصمية"
# res.cultural_summary -> "أمثال شعبية: 'طاح الحك وصاب غطاه' | معالم وأسواق: 'ساحة الشهداء وباب الواد' | مأكولات جزائرية: 'الرشتة العاصمية'"
```

**TypeScript:**
```typescript
import { detectCulturalReferences } from '@dz-open-suite/darja-nlp-kit';

const res = detectCulturalReferences('تيكي تاكا يا خويا الكولي وصلني وسلعتكم كابا أصلية');
// res.hasCulturalReference -> true
// res.memesAndTrends[0].canonicalName -> 'تيكي تاكا'
// res.slangExpressions[0].canonicalName -> 'سلعة كابا'
```

### `DarjaPipeline` & `analyze(text)` — Unified Customizable Pipeline

Run full Algerian NLP analysis in one call, or configure a domain-specific pipeline with custom sentiment lexicons, stopwords, profanity filters, and dialogue rules.

**Python:**
```python
from darja_nlp import DarjaPipeline, analyze

# 1. One-line full analysis
report = analyze("salam kho hab nchri 2 hbat noir l wahran 0661234567")
print(report.intent.intent)                 # "ORDER"
print(report.entities.wilayas[0].name_ar)   # "وهران"
print(report.entities.phones[0].whatsapp_url)
print(report.reply.reply)                   # Authentic Arabizi order response

# 2. Custom e-commerce pipeline with batching
nlp = (
    DarjaPipeline(store_name="DzShop", persona="merchant")
    .extend_lexicon(positive={"ممتازجدا": 0.95}, negative={"كارثي": -0.9})
    .add_stopwords(["كلمةزايدة"])
    .add_profanity(["منبوذ"])
)
reports = nlp.analyze_batch(["wach ya khoy", "سلعة ممتازجدا"])
```

**TypeScript:**
```typescript
import { DarjaPipeline, analyze } from '@dz-open-suite/darja-nlp-kit';

const report = analyze('salam kho hab nchri 2 hbat noir l wahran 0661234567');
console.log(report.intent?.intent); // 'ORDER'

const nlp = new DarjaPipeline({ storeName: 'DzShop', persona: 'merchant' })
  .extendLexicon({ ممتازجدا: 0.95 }, { كارثي: -0.9 })
  .addStopwords(['كلمةزايدة'])
  .addProfanity(['منبوذ']);
const batch = nlp.analyzeBatch(['wach ya khoy', 'سلعة ممتازجدا']);
```

### `DarjaClassifier` — Zero-Dependency Trainable Classifier

Train custom Darja classifiers (intent routing, spam filtering, domain tags) with zero external ML libraries, incremental `partial_fit` / `partialFit`, and portable JSON serialization across Python and Node.js.

**Python:**
```python
from darja_nlp import DarjaClassifier

clf = DarjaClassifier().fit(
    ["سلام حاب نكوموندي", "شحال السومة تاعها", "خردة وحشيتوهالي"],
    ["ORDER", "PRICE", "COMPLAINT"],
)
pred = clf.predict("بشحال التوصيل لوهران؟")
metrics = clf.evaluate(val_texts, val_labels)  # accuracy & macro_f1
clf.save("custom_intent_model.json")
```

**TypeScript:**
```typescript
import { DarjaClassifier } from '@dz-open-suite/darja-nlp-kit';

const clf = new DarjaClassifier().fit(
  ['سلام حاب نكوموندي', 'شحال السومة تاعها', 'خردة وحشيتوهالي'],
  ['ORDER', 'PRICE', 'COMPLAINT'],
);
const restored = DarjaClassifier.fromJSON(clf.toJSON());
console.log(restored.predict('حشيتوهالي خردة').label); // 'COMPLAINT'
```

### `DarjaChat` — Stateful Multi-Turn Conversation Session

Automatically tracks extracted slots (`wilaya`, `phone`, `quantity`, `colors`, `sizes`, `payment`, `carrier`, `price_dzd`), customer script/dialect, and escalation flags across multiple turns.

**Python:**
```python
from darja_nlp import DarjaChat

chat = DarjaChat(store_name="DzShop", persona="merchant")
t1 = chat.send("salam hab nchri 2 hbat noir")
t2 = chat.send("l wahran 0661234567 b yalidine")
print(t2.slots["wilaya"])     # "وهران"
print(t2.missing_slots)       # [] when all required slots are filled
```

**TypeScript:**
```typescript
import { DarjaChat } from '@dz-open-suite/darja-nlp-kit';

const chat = new DarjaChat({ storeName: 'DzShop', persona: 'merchant' });
chat.send('salam hab nchri 2 hbat noir');
const t2 = chat.send('l wahran 0661234567 b yalidine');
console.log(t2.slots.wilaya); // 'وهران'
```

## Zero-Dependency CLI

`darja-nlp-kit` comes with an instant command-line tool requiring zero extra dependencies:

```bash
# Unified full-pipeline analysis (entities, sentiment, dialect, intent, reply)
darja-nlp analyze "salam kho hab nchri 2 hbat noir l wahran 0661234567"

# Run the built-in 600-sample held-out Algerian sentiment benchmark
darja-nlp eval --mode hybrid
darja-nlp eval --mode ml

# Normalize Darja text & transliterate Arabizi
darja-nlp normalize "بزاااااف هاااايل"
darja-nlp arabizi "slm cv? 2ana 9rib"

# Parse all Algerian entities (Wilayas, communes, phones, prices, quantities)
darja-nlp parse "نحوس على 2 حبات مقاس XL نبعثهم لوهران 0661234567"

# Check human escalation & sentiment
darja-nlp escalation "سراقين حشيتوهالي رجعولي دراهمي"
darja-nlp sentiment "هايل بزاف بصح غالي شوية" --mode hybrid

# Intent & cultural analysis
darja-nlp intent "شحال التوصيل لسطيف؟"
darja-nlp culture "طاح الحك وصاب غطاه ابعثلي رشتة عاصمية لباب الواد"

# Start local HTTP microservice server (for n8n, Make, Docker)
darja-nlp server --port 8080
```

## Zero-Dependency HTTP Microservice (for n8n, Make.com, Webhooks)

Run a high-performance local microservice using standard library HTTP servers:

```bash
# In Python
python -m darja_nlp.server

# Or in Node.js
node dist/cli.js server --port 8080
```

### Endpoints:
- `GET  /api/health` — Service status, version, and active capabilities
- `POST /api/analyze` — Unified full-pipeline analysis report (all modules in one request)
- `POST /api/batch` — Batch process an array of `texts` through `DarjaPipeline`
- `POST /api/agent-context` — Complete context & formatted prompt for LLMs (GPT-4o, Gemini)
- `POST /api/parse` — Entities, wilayas, phones, operator, prices, quantities, and attributes
- `POST /api/intent` — Customer intent classification
- `POST /api/escalation` — Human takeover detection
- `POST /api/quantities` — Algerian quantities & product attributes
- `POST /api/culture` — Detect Algerian proverbs, viral memes, landmarks, gastronomy, and slang
- `POST /api/sentiment` — Hybrid/ML/lexicon sentiment score, label, and token breakdown (`mode`)
- `POST /api/dialect` — Regional dialect detection (`WEST`, `EAST`, `CENTER`, `SOUTH`)
- `GET  /api/culture` — Cultural dataset statistics and coverage
- `GET  /api/wilayas` — List all 69 official Algerian Wilayas
- `GET  /api/wilayas/:code` — Wilaya details by code (1 to 69)

## Algerian AI Automation Blueprints (`/examples`)

Ready-to-use blueprints for Algerian developers and automation engineers:

| Blueprint | Description |
|---|---|
| `examples/whatsapp_ecommerce_bot.py` | Production WhatsApp Cloud API webhook bot with human escalation and grounded Darja replies |
| `examples/n8n_algerian_ecommerce_workflow.json` | Importable n8n workflow file connecting incoming leads, darja-nlp-kit, and Telegram/WhatsApp alerts |
| `examples/langchain_agent_tools.py` | OpenAI & LangChain function calling definitions for Algerian NLP |
| `examples/fastapi_ecommerce_service.py` | FastAPI microservice template |
| `examples/express_ecommerce_service.ts` | Express.js microservice template |

## Algerian LLM Fine-Tuning & ML Corpora (`data/`)

To power both zero-dependency classical inference and LLM fine-tuning (Llama 3.1, Mistral, Qwen 2.5, Gemma 2), `darja-nlp-kit` provides curated open-source datasets built from authentic Algerian sources:

- **`data/fine_tuning/algerian_corpus_alpaca.json`** — **8,628** supervised instruction/conversation/cultural samples in Stanford Alpaca format (`instruction`, `input`, `output`).
- **`data/fine_tuning/algerian_corpus_sharegpt.json`** — **8,628** multi-turn conversation samples in ShareGPT format (Unsloth, Axolotl, LLaMA-Factory).
- **`data/fine_tuning/algerian_corpus_openai.jsonl`** — **8,628** samples in OpenAI Chat Completions JSONL format.
- **`data/fine_tuning/algerian_dpo_align.jsonl`** — **1,000** authentic Algerian DPO preference pairs (`prompt`, `chosen`, `rejected`) from `touati-kamel/DziriAlign`.
- **`data/fine_tuning/algerian_translation_pairs.json`** — **3,000** parallel bilingual pairs (Algerian Darja ↔ English).
- **`data/sentiment_model.json`** — 8,000 Chi2-selected unigram/bigram/subword linear sentiment model trained on **55,732** authentic Algerian samples (verified **70.83% ML / 68.00% hybrid** accuracy across 600 held-out samples in `data/eval_benchmark.json`).
- **`data/dialogue_kb.json`** — **599** grounded Algerian response entries used by the zero-dependency TF-IDF retriever.

### Authentic Algerian Data Sources Integrated:
1. **`Abdou/dz-sentiment-yt-comments` (`ADArabic`)**: 50,016 real labeled Algerian YouTube comments (Negative / Neutral / Positive).
2. **`alger-ia/dziribert`**: 9,437 labeled Algerian sentiment tweets/comments (`train` + `test` splits).
3. **`touati-kamel/DziriAlign`**: 1,000 Algerian Darja preference alignment pairs (`DPO`) for natural conversational grounding.
4. **`touati-kamel/DziriEval`**: 1,000 Algerian cultural & linguistic QA benchmarks across 20 domains.
5. **`asce3/algerian-chat-messages`**: Authentic Algerian human-to-human chat exchanges.
6. **`touati-kamel/algerian-arabic-english-translation-50k`**: Parallel bilingual Algerian Darja <-> English sentences.
7. **`sepidmnorozy/Algerian_sentiment`**: Labeled real-world Algerian social media sentiment comments.
8. **`test-bit-sys/algeria-geo`**: Official logistics ground truth covering all 69 Wilayas, 538 Dairas, and 1,541 Communes.

### Ready-to-Use LoRA / Unsloth Training Script:
```bash
python scripts/train_fine_tuning.py --model_name unsloth/llama-3-8b-Instruct-bnb-4bit
```

## Running Tests

### Python
```bash
cd packages/python
python -m pytest tests/ -v
```

### TypeScript
```bash
cd packages/js
npm run build
npm test
```

## Project Structure

```
darja-nlp-kit/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # GitHub Actions CI workflow (sync check + Py & JS tests)
│       └── publish.yml            # Release publishing to npm & PyPI
├── data/                          # Shared linguistic, ML, and cultural datasets
│   ├── sentiment_model.json       # 8,000-feature Chi2+SGD model (55.7K training samples)
│   ├── dialogue_kb.json           # 599 grounded Algerian KB retrieval entries
│   ├── eval_benchmark.json        # 600 held-out Algerian sentiment evaluation samples
│   ├── stopwords.json             # 592 categorized Darja stopwords
│   ├── lexicon.json               # 536 sentiment terms + negators + intensifiers
│   ├── arabizi_rules.json         # 157 overrides + 252 French loanwords whitelist
│   ├── wilayas.json               # All 69 Algerian Wilayas (Law 26-06) + 1,541 Communes
│   ├── dialects.json              # Regional dialect markers & metadata (WEST, EAST, CENTER, SOUTH)
│   ├── dialogues.json             # 158 customer-merchant few-shot dialogues
│   ├── franco_darja.json          # 60 Franco-Darja loanwords & hybrid verbs
│   ├── memes.json                 # 30 iconic Algerian memes
│   ├── profanity.json             # 36 categorized profanity entries (Arabic & Arabizi forms)
│   ├── culture.json               # 76 proverbs, viral trends, landmarks, and dishes
│   ├── slang.json                 # 37 street, youth, and e-commerce slang expressions
│   └── fine_tuning/               # 8,628 SFT (Alpaca/ShareGPT/OpenAI) + 1,000 DPO + 3,000 translations
├── docs/                          # Standalone GitHub Pages interactive web playground
├── packages/
│   ├── js/                        # TypeScript/JavaScript package (@dz-open-suite/darja-nlp-kit)
│   │   ├── src/                   # pipeline, classifier, chat, sentiment, dialogue, entities, server, cli, ...
│   │   ├── tests/
│   │   └── package.json
│   └── python/                    # Python package (darja-nlp-kit)
│       ├── darja_nlp/             # pipeline, classifier, chat, sentiment, dialogue, entities, server, cli, ...
│       ├── tests/
│       └── pyproject.toml
├── scripts/
│   ├── build_v2_data_and_models.py # Trains sentiment_model.json, builds KB/benchmark & SFT/DPO corpora
│   ├── build_playground.py        # Builds zero-dep HTML web playground (docs/index.html)
│   ├── train_fine_tuning.py       # LoRA / SFT fine-tuning starter script
│   └── sync_data.py               # Syncs all 15 JSON files & README across Python & JS packages
└── README.md
```

## License

MIT
