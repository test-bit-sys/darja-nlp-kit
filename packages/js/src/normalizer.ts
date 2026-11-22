import { NormalizeOptions } from './types';

const ALEF_VARIANTS = /[\u0622\u0623\u0625]/g;
const TA_MARBUTA = /\u0629/g;
const ALEF_MAQSURA = /\u0649/g;
const TASHKEEL = /[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]/g;
const TATWEEL = /\u0640/g;
const ARABIC_ELONGATION = /(.)\1{2,}/g;
const LATIN_ELONGATION = /([a-zA-Z])\1{2,}/g;
const MULTI_SPACE = /\s+/g;
const MULTI_PUNCT = /([!?.]){2,}/g;

const VALID_DOUBLES = new Set([
  'll', 'ss', 'mm', 'nn', 'dd', 'tt', 'rr', 'ff', 'cc', 'pp', 'bb', 'gg', 'zz',
  'ee', 'oo', 'aa'
]);

function reduceArabicElongation(text: string): string {
  return text.replace(ARABIC_ELONGATION, '$1');
}

function reduceLatinElongation(text: string): string {
  return text.replace(LATIN_ELONGATION, (_match: string, char: string) => {
    const doubled = char.toLowerCase() + char.toLowerCase();
    if (VALID_DOUBLES.has(doubled)) {
      return char + char;
    }
    return char;
  });
}

export function normalize(text: string, options?: NormalizeOptions): string {
  if (!text) {
    return '';
  }

  let result = text;

  result = result.replace(ALEF_VARIANTS, '\u0627');

  result = result.replace(TA_MARBUTA, '\u0647');

  result = result.replace(ALEF_MAQSURA, '\u064A');

  if (!options?.preserveTashkeel) {
    result = result.replace(TASHKEEL, '');
  }

  result = result.replace(TATWEEL, '');

  if (!options?.preserveLength) {
    result = reduceArabicElongation(result);
    result = reduceLatinElongation(result);
  }

  result = result.replace(MULTI_SPACE, ' ');
  result = result.replace(MULTI_PUNCT, '$1');
  result = result.trim();

  return result;
}
