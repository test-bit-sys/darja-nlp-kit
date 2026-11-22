# darja-nlp-kit

[![CI](https://github.com/dz-open-suite/darja-nlp-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/dz-open-suite/darja-nlp-kit/actions/workflows/ci.yml)
[![npm version](https://img.shields.io/npm/v/@dz-open-suite/darja-nlp-kit.svg)](https://www.npmjs.com/package/@dz-open-suite/darja-nlp-kit)
[![PyPI version](https://img.shields.io/pypi/v/darja-nlp-kit.svg)](https://pypi.org/project/darja-nlp-kit/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Zero-dependency, dual-language (TypeScript & Python) NLP toolkit for **Algerian Darja** (Derja) — part of the **DZ Open Suite** ecosystem.

Handles Arabic script, Arabizi (Latin transliteration with numbers), and French/Arabic code-switching common in Algerian e-commerce, social media, and daily communication.

## Features

- **Text Normalization** — Unify Arabic letter variants, strip diacritics, reduce character elongation
- **Arabizi-to-Arabic Transliteration** — Smart conversion with French loanword detection, digraph mappings, and context-sensitive number handling
- **Stopword Removal** — 500+ categorized Algerian Darja stopwords (Arabic script + Arabizi) with prefix stripping
- **Tokenization** — Mixed-script tokenization with circumfix negation detection (ما...ش / ma...ch)
- **Sentiment Analysis** — Score-based analysis with negation inversion, double negation, intensifier scaling, and code-switching support

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

## Data Files

All linguistic data lives in `/data` and is synced to both packages:

| File | Description |
|---|---|
| `stopwords.json` | 500+ categorized stopwords (prepositions, pronouns, conjunctions, adverbs, etc.) |
| `lexicon.json` | Sentiment dictionary with positive/negative scores, negators, intensifiers |
| `arabizi_rules.json` | Transliteration rules, French whitelist, and irregular overrides |

## Running Tests

### Python
```bash
cd packages/python
python -m pytest tests/ -v
```

### TypeScript
```bash
cd packages/js
npx tsx --test tests/index.test.ts
```

## Project Structure

```
darja-nlp-kit/
├── .github/
│   └── workflows/
│       ├── ci.yml             # GitHub Actions CI workflow
│       └── publish.yml        # Release publishing to npm & PyPI
├── data/                      # Shared linguistic datasets
│   ├── stopwords.json
│   ├── lexicon.json
│   └── arabizi_rules.json
├── packages/
│   ├── js/                    # TypeScript/JavaScript package
│   │   ├── src/
│   │   ├── tests/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── python/                # Python package
│       ├── darja_nlp/
│       ├── tests/
│       └── pyproject.toml
├── scripts/
│   └── sync_data.py           # Data sync utility
└── README.md
```

## License

MIT
