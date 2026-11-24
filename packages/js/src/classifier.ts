/**
 * Zero-dependency trainable Naive Bayes n-gram text classifier for Algerian Darja.
 * Models serialize cleanly to JSON and are 100% interoperable with Python DarjaClassifier.
 */
import * as fs from 'fs';
import { normalize } from './normalizer';

const RE_TOK = /[a-zA-Z0-9\u0621-\u064A\u0671-\u06D3]+|[\u{1F300}-\u{1FAFF}\u2600-\u27BF]+/gu;
const RE_ALPHA = /^[a-zA-Z\u0621-\u064A\u0671-\u06D3]+$/;

export interface ClassifierOptions {
  alpha?: number;
  useBigrams?: boolean;
  useSubwords?: boolean;
}

export interface ClassificationPrediction {
  label: string;
  confidence: number;
  probabilities: Record<string, number>;
}

export interface ClassMetrics {
  precision: number;
  recall: number;
  f1: number;
  support: number;
}

export interface EvaluationResult {
  accuracy: number;
  macroF1: number;
  total: number;
  correct: number;
  perClass: Record<string, ClassMetrics>;
}

export interface SerializedClassifier {
  version: string;
  alpha: number;
  use_bigrams: boolean;
  use_subwords: boolean;
  class_counts: Record<string, number>;
  class_totals: Record<string, number>;
  token_counts: Record<string, Record<string, number>>;
}

export class DarjaClassifier {
  public alpha: number;
  public useBigrams: boolean;
  public useSubwords: boolean;
  public classCounts: Record<string, number> = {};
  public tokenCounts: Record<string, Record<string, number>> = {};
  public classTotals: Record<string, number> = {};
  public vocab: Set<string> = new Set();

  constructor(options?: ClassifierOptions) {
    this.alpha = options?.alpha ?? 1.0;
    this.useBigrams = options?.useBigrams ?? true;
    this.useSubwords = options?.useSubwords ?? true;
  }

  private extractFeatures(text: string): string[] {
    if (!text) return [];
    const normed = normalize(text.toLowerCase());
    const toks = normed.match(RE_TOK) || [];
    const feats: string[] = [...toks];
    if (this.useBigrams && toks.length > 1) {
      for (let i = 0; i < toks.length - 1; i++) {
        feats.push(`${toks[i]}_${toks[i + 1]}`);
      }
    }
    if (this.useSubwords) {
      for (const w of toks) {
        if (w.length >= 5 && RE_ALPHA.test(w)) {
          feats.push(`p3:${w.slice(0, 3)}`);
          feats.push(`s3:${w.slice(-3)}`);
        }
      }
    }
    return feats;
  }

  fit(texts: string[], labels: string[]): this {
    if (texts.length !== labels.length) {
      throw new Error('texts and labels must have the same length');
    }
    this.classCounts = {};
    this.tokenCounts = {};
    this.classTotals = {};
    this.vocab = new Set();
    return this.partialFit(texts, labels);
  }

  partialFit(texts: string[], labels: string[]): this {
    if (texts.length !== labels.length) {
      throw new Error('texts and labels must have the same length');
    }
    for (let i = 0; i < texts.length; i++) {
      const lbl = String(labels[i]);
      if (this.classCounts[lbl] === undefined) {
        this.classCounts[lbl] = 0;
        this.tokenCounts[lbl] = {};
        this.classTotals[lbl] = 0;
      }
      this.classCounts[lbl]++;
      const feats = this.extractFeatures(texts[i]);
      const cMap = this.tokenCounts[lbl];
      for (const f of feats) {
        cMap[f] = (cMap[f] || 0) + 1;
        this.classTotals[lbl]++;
        this.vocab.add(f);
      }
    }
    return this;
  }

  predict(text: string): ClassificationPrediction {
    const labels = Object.keys(this.classCounts).sort();
    if (labels.length === 0) {
      throw new Error('Classifier has not been fitted yet');
    }

    const totalDocs = Object.values(this.classCounts).reduce((a, b) => a + b, 0);
    const vSize = Math.max(1, this.vocab.size);
    const feats = this.extractFeatures(text);

    const logScores: Record<string, number> = {};
    for (const lbl of labels) {
      const prior = Math.log(this.classCounts[lbl] / totalDocs);
      const denom = this.classTotals[lbl] + this.alpha * vSize;
      const cMap = this.tokenCounts[lbl];
      let score = prior;
      for (const f of feats) {
        if (this.vocab.has(f)) {
          score += Math.log(((cMap[f] || 0) + this.alpha) / denom);
        }
      }
      logScores[lbl] = score;
    }

    const maxS = Math.max(...Object.values(logScores));
    const exps: Record<string, number> = {};
    let expSum = 0;
    for (const lbl of labels) {
      const e = Math.exp(Math.max(-50, logScores[lbl] - maxS));
      exps[lbl] = e;
      expSum += e;
    }
    expSum = expSum || 1;

    const probabilities: Record<string, number> = {};
    let bestLabel = labels[0];
    for (const lbl of labels) {
      probabilities[lbl] = Math.round((exps[lbl] / expSum) * 10000) / 10000;
      if (
        probabilities[lbl] > probabilities[bestLabel] ||
        (probabilities[lbl] === probabilities[bestLabel] && logScores[lbl] > logScores[bestLabel])
      ) {
        bestLabel = lbl;
      }
    }

    return {
      label: bestLabel,
      confidence: probabilities[bestLabel],
      probabilities,
    };
  }

  predictBatch(texts: string[]): ClassificationPrediction[] {
    return texts.map((t) => this.predict(t));
  }

  evaluate(texts: string[], labels: string[]): EvaluationResult {
    if (texts.length !== labels.length) {
      throw new Error('texts and labels must have the same length');
    }
    if (texts.length === 0) {
      return { accuracy: 0, macroF1: 0, total: 0, correct: 0, perClass: {} };
    }

    const tp: Record<string, number> = {};
    const fp: Record<string, number> = {};
    const fn: Record<string, number> = {};
    let correct = 0;

    const labelSet = new Set([...labels.map(String), ...Object.keys(this.classCounts)]);
    const allLabels = Array.from(labelSet).sort();

    for (let i = 0; i < texts.length; i++) {
      const trueStr = String(labels[i]);
      const pred = this.predict(texts[i]).label;
      if (pred === trueStr) {
        correct++;
        tp[trueStr] = (tp[trueStr] || 0) + 1;
      } else {
        fp[pred] = (fp[pred] || 0) + 1;
        fn[trueStr] = (fn[trueStr] || 0) + 1;
      }
    }

    const perClass: Record<string, ClassMetrics> = {};
    let f1Sum = 0;
    let presentClasses = 0;

    for (const lbl of allLabels) {
      const cTp = tp[lbl] || 0;
      const cFp = fp[lbl] || 0;
      const cFn = fn[lbl] || 0;
      const support = cTp + cFn;
      const prec = cTp + cFp > 0 ? cTp / (cTp + cFp) : 0;
      const rec = support > 0 ? cTp / support : 0;
      const f1 = prec + rec > 0 ? (2 * prec * rec) / (prec + rec) : 0;
      if (support > 0) {
        f1Sum += f1;
        presentClasses++;
      }
      perClass[lbl] = {
        precision: Math.round(prec * 10000) / 10000,
        recall: Math.round(rec * 10000) / 10000,
        f1: Math.round(f1 * 10000) / 10000,
        support,
      };
    }

    const total = texts.length;
    return {
      accuracy: Math.round((correct / total) * 10000) / 10000,
      macroF1: presentClasses > 0 ? Math.round((f1Sum / presentClasses) * 10000) / 10000 : 0,
      total,
      correct,
      perClass,
    };
  }

  toJSON(): SerializedClassifier {
    return {
      version: '1.0.0',
      alpha: this.alpha,
      use_bigrams: this.useBigrams,
      use_subwords: this.useSubwords,
      class_counts: this.classCounts,
      class_totals: this.classTotals,
      token_counts: this.tokenCounts,
    };
  }

  static fromJSON(data: SerializedClassifier): DarjaClassifier {
    const clf = new DarjaClassifier({
      alpha: data.alpha ?? 1.0,
      useBigrams: data.use_bigrams ?? true,
      useSubwords: data.use_subwords ?? true,
    });
    clf.classCounts = { ...(data.class_counts || {}) };
    clf.classTotals = { ...(data.class_totals || {}) };
    clf.tokenCounts = {};
    clf.vocab = new Set();
    for (const [lbl, tmap] of Object.entries(data.token_counts || {})) {
      clf.tokenCounts[lbl] = { ...tmap };
      for (const tok of Object.keys(tmap)) {
        clf.vocab.add(tok);
      }
    }
    return clf;
  }

  save(filepath: string): void {
    fs.writeFileSync(filepath, JSON.stringify(this.toJSON(), null, 2), 'utf-8');
  }

  static load(filepath: string): DarjaClassifier {
    const raw = fs.readFileSync(filepath, 'utf-8');
    return DarjaClassifier.fromJSON(JSON.parse(raw) as SerializedClassifier);
  }
}
