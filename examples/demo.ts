import {
  normalize,
  arabiziToArabic,
  tokenize,
  removeStopwords,
  analyzeSentiment,
} from '../packages/js/src';

const samples = [
  'السلعة هاااااايلة بزاااااف و الخدمة فور، يعطيك الصحة!',
  'produit mli7 bzaf walakin livraison rotar chwiya, prix 4500 DA',
  'سلعة عيانة و السيرفيس ماشي شباب قاع، ارناك كبيرة ما ننصحكمش',
  '2ana 9rib نوصل، wesh rak khoya?',
  'مافهمتش علاش هاد التيليفون ماشي مليح، ما عجبنيش',
];

console.log('='.repeat(60));
console.log('      DZ Open Suite - darja-nlp-kit TypeScript Demo');
console.log('='.repeat(60));

for (const text of samples) {
  console.log('\n' + '-'.repeat(60));
  console.log(`النص الأصلي (Original): ${text}`);
  console.log('-'.repeat(60));

  console.log(`1. التطبيع (Normalized)     : ${normalize(text)}`);
  console.log(`2. تحويل الأرابيزي (Arabic)  : ${arabiziToArabic(text)}`);

  const tok = tokenize(text);
  console.log(`3. التقطيع (Tokens)          : [${tok.tokens.join(', ')}]`);
  if (tok.negations.length > 0) {
    const negs = tok.negations.map((n) => `${n.original} -> جذر: ${n.root}`).join(', ');
    console.log(`   حالات النفي (ما..ش)       : ${negs}`);
  }

  console.log(`4. بدون كلمات شائعة          : ${removeStopwords(text)}`);

  const sent = analyzeSentiment(text);
  console.log(`5. تحليل المشاعر (Sentiment) : [${sent.label}] (Score: ${sent.score}, Negated: ${sent.negated})`);
  if (sent.positiveTokens.length > 0) console.log(`   الكلمات الإيجابية        : [${sent.positiveTokens.join(', ')}]`);
  if (sent.negativeTokens.length > 0) console.log(`   الكلمات السلبية          : [${sent.negativeTokens.join(', ')}]`);
}
