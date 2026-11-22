import {
  normalize,
  arabiziToArabic,
  tokenize,
  removeStopwords,
  analyzeSentiment,
  extractEntities,
  detectDialect,
} from '../packages/js/src';

const samples = [
  'السلعة هاااااايلة بزاااااف و الخدمة فور، يعطيك الصحة! توصيل لبوسعادة',
  'produit mli7 bzaf livraison l wahran rotar chwiya, prix 4500 DA w khlass b baridimob',
  'سلعة عيانة و السيرفيس ماشي شباب قاع، ارناك كبيرة ما ننصحكمش',
  'شوالا راك باغي خوية غايا درك؟ كاين توصيل للسانية ولاية 31',
  'واشنهي هادا قداش يدير ياسر باهي سيرتا نخلصك كاش عند الاستلام بـ زوج ملاين',
];

console.log('='.repeat(65));
console.log('      DZ Open Suite - darja-nlp-kit TypeScript Demo');
console.log('='.repeat(65));

for (const text of samples) {
  console.log('\n' + '-'.repeat(65));
  console.log(`النص الأصلي (Original): ${text}`);
  console.log('-'.repeat(65));

  console.log(`1. التطبيع (Normalized)       : ${normalize(text)}`);
  console.log(`2. تحويل الأرابيزي (Arabic)    : ${arabiziToArabic(text)}`);

  const tok = tokenize(text);
  console.log(`3. التقطيع (Tokens)            : [${tok.tokens.join(', ')}]`);
  if (tok.negations.length > 0) {
    const negs = tok.negations.map((n) => `${n.original} -> جذر: ${n.root}`).join(', ');
    console.log(`   حالات النفي (ما..ش)         : ${negs}`);
  }

  console.log(`4. بدون كلمات شائعة            : ${removeStopwords(text)}`);

  const sent = analyzeSentiment(text);
  console.log(`5. تحليل المشاعر (Sentiment)   : [${sent.label}] (Score: ${sent.score})`);

  const entities = extractEntities(text);
  if (entities.wilayas.length > 0) {
    const wStr = entities.wilayas.map((w) => `${w.nameAr} / ${w.nameFr} (${w.codeStr})`).join(', ');
    console.log(`6. الولايات (Wilayas - 69)     : ${wStr}`);
  }
  if (entities.payments.length > 0) {
    console.log(`   طرق الدفع (Payments)        : ${entities.payments.map((p) => p.label).join(', ')}`);
  }
  if (entities.prices.length > 0) {
    console.log(`   الأسعار (Prices)            : ${entities.prices.map((p) => `${p.raw} -> ${p.amount} DZD`).join(', ')}`);
  }

  const dialect = detectDialect(text);
  console.log(`7. اللهجة الجهوية (Dialect)    : [${dialect.region}] (الثقة: ${Math.round(dialect.confidence * 100)}%)`);
}
