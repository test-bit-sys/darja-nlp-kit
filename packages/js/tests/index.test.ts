import { describe, it } from 'node:test';
import * as assert from 'node:assert/strict';
import { normalize } from '../src/normalizer';
import { arabiziToArabic } from '../src/arabizi';
import { tokenize, removeStopwords, isStopword } from '../src/stopwords';
import { analyzeSentiment } from '../src/sentiment';
import { extractEntities, getWilayas, getWilayaByCode } from '../src/entities';
import { detectDialect } from '../src/dialect';
import { buildAgentContext, formatAgentSystemPrompt } from '../src/agent';

describe('normalize', () => {
  it('should unify alef variants', () => {
    assert.equal(normalize('أحمد إبراهيم آمنة'), 'احمد ابراهيم امنه');
  });

  it('should convert ta marbuta to ha', () => {
    assert.equal(normalize('مدرسة جميلة'), 'مدرسه جميله');
  });

  it('should convert alef maqsura to ya', () => {
    assert.equal(normalize('على موسى'), 'علي موسي');
  });

  it('should strip tashkeel by default', () => {
    assert.equal(normalize('بِسْمِ اللَّهِ'), 'بسم الله');
  });

  it('should preserve tashkeel when option is set', () => {
    const result = normalize('بِسْمِ', { preserveTashkeel: true });
    assert.ok(result.includes('\u0650'));
  });

  it('should strip tatweel', () => {
    assert.equal(normalize('كتـــاب'), 'كتاب');
  });

  it('should reduce Arabic character elongation', () => {
    assert.equal(normalize('بزاااااف'), 'بزاف');
  });

  it('should reduce Latin character elongation', () => {
    assert.equal(normalize('haaaayel'), 'hayel');
  });

  it('should preserve valid double consonants', () => {
    const result = normalize('allahhh');
    assert.equal(result, 'allah');
  });

  it('should normalize whitespace', () => {
    assert.equal(normalize('كلمة    كلمة'), 'كلمه كلمه');
  });

  it('should normalize repeated punctuation', () => {
    assert.equal(normalize('واش!!!'), 'واش!');
  });

  it('should handle empty string', () => {
    assert.equal(normalize(''), '');
  });
});

describe('arabiziToArabic', () => {
  it('should transliterate basic Arabizi', () => {
    const result = arabiziToArabic('salam');
    assert.equal(result, 'سلام');
  });

  it('should handle number-to-letter mappings', () => {
    const result = arabiziToArabic('3lach');
    assert.ok(result.includes('ع'));
  });

  it('should handle digraphs', () => {
    const result = arabiziToArabic('chkoun');
    assert.ok(result.startsWith('ش'));
  });

  it('should preserve French words by default', () => {
    const result = arabiziToArabic('merci livraison');
    assert.ok(result.includes('merci'));
    assert.ok(result.includes('livraison'));
  });

  it('should transliterate French words when preserveFrench is false', () => {
    const result = arabiziToArabic('merci', { preserveFrench: false });
    assert.ok(!result.includes('merci'));
  });

  it('should apply irregular overrides', () => {
    assert.equal(arabiziToArabic('slm'), 'سلام');
    assert.equal(arabiziToArabic('nchallah'), 'ان شاء الله');
    assert.equal(arabiziToArabic('hamdoulah'), 'الحمد لله');
  });

  it('should NOT convert standalone numbers', () => {
    const result = arabiziToArabic('prix 4500 DA');
    assert.ok(result.includes('4500'));
  });

  it('should NOT convert phone numbers', () => {
    const result = arabiziToArabic('0550123456');
    assert.equal(result, '0550123456');
  });

  it('should handle mixed Arabizi and Arabic', () => {
    const result = arabiziToArabic('هادا hayel');
    assert.ok(result.startsWith('هادا'));
  });

  it('should handle code-switching sentence', () => {
    const result = arabiziToArabic('produit mli7 livraison rapide');
    assert.ok(result.includes('produit'));
    assert.ok(result.includes('livraison'));
    assert.ok(result.includes('rapide'));
  });

  it('should detect French words by suffix heuristics', () => {
    const result = arabiziToArabic('information');
    assert.equal(result, 'information');
  });

  it('should preserve standalone numbers while converting arabizi digits', () => {
    const resNumbers = arabiziToArabic('Prix 2500 DA w livraison l 16');
    assert.ok(resNumbers.includes('2500'));
    assert.ok(resNumbers.includes('16'));

    const resDigits = arabiziToArabic('2ana 9rib');
    assert.equal(resDigits, 'انا قريب');
  });

  it('should preserve French words containing Arabizi digraphs', () => {
    const words = [
      'achat', 'chambre', 'douche', 'marche', 'couleur',
      'bouton', 'retour', 'choix', 'chargeur', 'compte', 'boutique'
    ];
    for (const word of words) {
      assert.equal(arabiziToArabic(word), word, `Expected ${word} to be preserved`);
    }
  });

  it('should handle empty string', () => {
    assert.equal(arabiziToArabic(''), '');
  });
});

describe('tokenize', () => {
  it('should tokenize Arabic text', () => {
    const result = tokenize('هادا المنتج هايل بزاف');
    assert.ok(result.tokens.length >= 4);
  });

  it('should tokenize mixed Arabic/Latin', () => {
    const result = tokenize('هادا produit مليح');
    assert.ok(result.tokens.length >= 3);
  });

  it('should detect Arabic circumfix negation', () => {
    const result = tokenize('مافهمتش الحاجة');
    assert.ok(result.negations.length > 0);
    assert.equal(result.negations[0].negated, true);
    assert.equal(result.negations[0].root, 'فهمت');
  });

  it('should detect Arabizi circumfix negation', () => {
    const result = tokenize('mafhamtch hadik');
    assert.ok(result.negations.length > 0);
    assert.equal(result.negations[0].negated, true);
    assert.equal(result.negations[0].root, 'fhamt');
  });

  it('should handle punctuation correctly', () => {
    const result = tokenize('واش هادا? مشي مليح!');
    assert.ok(result.tokens.every((t: string) => !t.includes('?') && !t.includes('!')));
  });
});

describe('removeStopwords', () => {
  it('should remove Darja stopwords', () => {
    const result = removeStopwords('هادا المنتج تاع هايل');
    assert.ok(!result.includes('هادا'));
    assert.ok(!result.includes('تاع'));
    assert.ok(result.includes('هايل'));
  });

  it('should remove Arabizi stopwords', () => {
    const result = removeStopwords('had produit ta3 hayel');
    assert.ok(!result.includes('had'));
    assert.ok(!result.includes('ta3'));
  });

  it('should handle empty string', () => {
    assert.equal(removeStopwords(''), '');
  });
});

describe('isStopword', () => {
  it('should identify Arabic stopwords', () => {
    assert.ok(isStopword('تاع'));
    assert.ok(isStopword('واش'));
    assert.ok(isStopword('هادا'));
  });

  it('should identify Arabizi stopwords', () => {
    assert.ok(isStopword('ta3'));
    assert.ok(isStopword('wesh'));
    assert.ok(isStopword('hada'));
  });

  it('should identify non-stopwords with prefixes as not stopwords unless base is stopword', () => {
    assert.ok(isStopword('بالزربة'));
    assert.equal(removeStopwords('المنتوج هايل بالزربة'), 'المنتوج هايل');
  });

  it('should return false for non-stopwords', () => {
    assert.ok(!isStopword('هايل'));
    assert.ok(!isStopword('منتج'));
  });
});

describe('analyzeSentiment', () => {
  it('should detect positive sentiment', () => {
    const result = analyzeSentiment('هايل');
    assert.equal(result.label, 'POSITIVE');
    assert.ok(result.score > 0);
    assert.ok(result.positiveTokens.includes('هايل'));
  });

  it('should detect negative sentiment', () => {
    const result = analyzeSentiment('عيان');
    assert.equal(result.label, 'NEGATIVE');
    assert.ok(result.score < 0);
    assert.ok(result.negativeTokens.includes('عيان'));
  });

  it('should handle negation inversion', () => {
    const result = analyzeSentiment('ماشي هايل');
    assert.ok(result.score < 0, `Expected negative score, got ${result.score}`);
    assert.equal(result.negated, true);
  });

  it('should invert negative word to POSITIVE on double negation', () => {
    const arabicRes = analyzeSentiment('ماشي عيان');
    assert.equal(arabicRes.label, 'POSITIVE');
    assert.ok(arabicRes.score > 0);
    assert.equal(arabicRes.negated, true);

    const arabiziRes = analyzeSentiment('machi 3ayan');
    assert.equal(arabiziRes.label, 'POSITIVE');
    assert.ok(arabiziRes.score > 0);
    assert.equal(arabiziRes.negated, true);
  });

  it('should detect sentiment with Arabic prefixes on nouns and adjectives', () => {
    const result = analyzeSentiment('المنتوج هايل');
    assert.equal(result.label, 'POSITIVE');
    assert.ok(result.score > 0);
  });

  it('should handle intensifier scaling', () => {
    const plain = analyzeSentiment('هايل');
    const intensified = analyzeSentiment('هايل بزاف');
    assert.ok(intensified.score >= plain.score,
      `Intensified ${intensified.score} should be >= plain ${plain.score}`);
  });

  it('should detect mixed sentiment', () => {
    const result = analyzeSentiment('هايل بصح غالي');
    assert.equal(result.label, 'MIXED');
    assert.ok(result.positiveTokens.length > 0);
    assert.ok(result.negativeTokens.length > 0);
  });

  it('should handle Arabizi sentiment words', () => {
    const result = analyzeSentiment('hayel');
    assert.equal(result.label, 'POSITIVE');
  });

  it('should handle French loanword sentiment', () => {
    const result = analyzeSentiment('parfait');
    assert.equal(result.label, 'POSITIVE');
    assert.ok(result.score > 0);
  });

  it('should handle e-commerce review with code-switching', () => {
    const result = analyzeSentiment('المنتج هايل merci');
    assert.ok(result.score > 0);
  });

  it('should handle e-commerce review with price (numbers ignored)', () => {
    const result = analyzeSentiment('المنتج مليح prix 4500 DA');
    assert.ok(result.score > 0);
  });

  it('should return NEUTRAL for empty text', () => {
    const result = analyzeSentiment('');
    assert.equal(result.label, 'NEUTRAL');
    assert.equal(result.score, 0);
  });

  it('should return NEUTRAL for text with no sentiment words', () => {
    const result = analyzeSentiment('المنتج وصل');
    assert.equal(result.label, 'NEUTRAL');
  });
});

describe('wilayas & entities', () => {
  it('should register exactly 69 wilayas according to latest reform', () => {
    const all = getWilayas();
    assert.equal(all.length, 69);
  });

  it('should find wilaya by code including new wilayas (59-69)', () => {
    const alger = getWilayaByCode(16);
    assert.equal(alger?.name_fr, 'Alger');

    const bousaada = getWilayaByCode(68);
    assert.equal(bousaada?.name_ar, 'بوسعادة');

    const elabiodh = getWilayaByCode('69');
    assert.equal(elabiodh?.name_fr, 'El Abiodh Sidi Cheikh');
  });

  it('should extract wilaya by code, name, and alias', () => {
    const res1 = extractEntities('livraison l 16');
    assert.ok(res1.wilayas.some((w) => w.code === 16));

    const res2 = extractEntities('حاب نشري في وهران و نبعث لسطيف');
    assert.ok(res2.wilayas.some((w) => w.code === 31));
    assert.ok(res2.wilayas.some((w) => w.code === 19));

    const res3 = extractEntities('توصيل لبوسعادة و البهجة');
    assert.ok(res3.wilayas.some((w) => w.code === 68));
    assert.ok(res3.wilayas.some((w) => w.code === 16));
  });

  it('should extract Algerian payment methods', () => {
    const text = 'نخلصك عبر baridimob او كاش عند الاستلام او بالذهبية';
    const res = extractEntities(text);
    assert.ok(res.payments.some((p) => p.type === 'BARIDIMOB'));
    assert.ok(res.payments.some((p) => p.type === 'COD'));
    assert.ok(res.payments.some((p) => p.type === 'EDAHABIA'));
  });

  it('should extract numeric and colloquial Darja prices', () => {
    const text1 = 'السعر 4500 DA و التوصيل بـ 500 دج';
    const res1 = extractEntities(text1);
    assert.ok(res1.prices.some((p) => p.amount === 4500));
    assert.ok(res1.prices.some((p) => p.amount === 500));

    const text2 = 'سلعة شريتها بـ زوج ملاين و بقاتلي مية الف';
    const res2 = extractEntities(text2);
    assert.ok(res2.prices.some((p) => p.amount === 20000));
    assert.ok(res2.prices.some((p) => p.amount === 1000));

    const text3 = 'سومتها 3 mlayen و سلعة ثانية 5 ملاين';
    const res3 = extractEntities(text3);
    assert.ok(res3.prices.some((p) => p.amount === 30000));
    assert.ok(res3.prices.some((p) => p.amount === 50000));
  });

  it('should extract Algerian delivery companies and modes', () => {
    const text = 'ابعثهالي مع yalidine stop desk و خلاص كاش';
    const res = extractEntities(text);
    assert.ok(res.deliveries?.some((d) => d.company === 'YALIDINE'));
    assert.equal(res.deliveryMode?.mode, 'STOP_DESK');

    const text2 = 'livraison a domicile zr express';
    const res2 = extractEntities(text2);
    assert.ok(res2.deliveries?.some((d) => d.company === 'ZR_EXPRESS'));
    assert.equal(res2.deliveryMode?.mode, 'HOME_DELIVERY');
  });

  it('should extract and normalize Algerian phone numbers', () => {
    const text = 'عيطلي في 0661234567 ولا +213 555 12 34 56';
    const res = extractEntities(text);
    assert.equal(res.phones?.length, 2);
    assert.ok(res.phones?.some((p) => p.normalized === '0661234567'));
    assert.ok(res.phones?.some((p) => p.normalized === '0555123456'));
  });
});

describe('AI Agent Integration', () => {
  it('should build complete structured agent context', () => {
    const msg = 'salam khoya rani baghi had lproduit b 2 mlayen l Constantine wla nversilk f baridimob? num ta3i 0770112233';
    const ctx = buildAgentContext(msg);
    assert.ok(ctx.groundedFacts.wilayas.some((w) => w.includes('قسنطينة')));
    assert.ok(ctx.groundedFacts.pricesDzd.some((p) => p.includes('20,000')));
    assert.ok(ctx.groundedFacts.payments.some((p) => p.includes('BaridiMob')));
    assert.ok(ctx.groundedFacts.phones.includes('0770112233'));
    assert.equal(ctx.dialect.region, 'WEST');
  });

  it('should format realistic ground-truth system prompt', () => {
    const msg = 'khedma 3ayana w sil3a khorda 7chawhali';
    const ctx = buildAgentContext(msg);
    const prompt = formatAgentSystemPrompt(ctx);
    assert.ok(prompt.includes('NEGATIVE'));
    assert.ok(prompt.includes('⚠️ الزبون غاضب أو يشتكي'));
  });
});

describe('detectDialect', () => {
  it('should detect Western Algerian dialect', () => {
    const res = detectDialect('شوالا راك باغي خوية غايا درك؟');
    assert.equal(res.region, 'WEST');
    assert.ok(res.confidence > 0.6);
  });

  it('should detect Eastern Algerian dialect', () => {
    const res = detectDialect('واشنهي هادا قداش يدير ياسر باهي');
    assert.equal(res.region, 'EAST');
    assert.ok(res.confidence > 0.6);
  });

  it('should detect Central Algerian dialect', () => {
    const res = detectDialect('واشنو هكداك حوايج العاصمة دروك');
    assert.equal(res.region, 'CENTER');
    assert.ok(res.confidence > 0.6);
  });

  it('should return GENERAL_DARJA when no regional markers found', () => {
    const res = detectDialect('سلام عليكم شكرا');
    assert.equal(res.region, 'GENERAL_DARJA');
  });
});
