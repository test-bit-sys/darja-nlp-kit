"""Zero-dependency trainable Naive Bayes n-gram text classifier for Algerian Darja."""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .normalizer import normalize


_RE_TOK = re.compile(r"[a-zA-Z0-9\u0621-\u064A\u0671-\u06D3]+|[\U0001F300-\U0001FAFF\u2600-\u27BF]+")
_RE_ALPHA = re.compile(r"^[a-zA-Z\u0621-\u064A\u0671-\u06D3]+$")


@dataclass
class ClassificationPrediction:
    label: str
    confidence: float
    probabilities: Dict[str, float] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    accuracy: float
    macro_f1: float
    total: int
    correct: int
    per_class: Dict[str, Dict[str, float]] = field(default_factory=dict)


class DarjaClassifier:
    """Zero-dependency, Darja-aware Multinomial Naive Bayes classifier.

    Supports unigrams, bigrams, and 3-char prefix/suffix subword features
    so conjugated Darja/Arabizi verbs and prefixed nouns generalize naturally.
    Models serialize cleanly to JSON and can be shared between Python and Node.js.
    """

    def __init__(
        self,
        alpha: float = 1.0,
        use_bigrams: bool = True,
        use_subwords: bool = True,
    ) -> None:
        self.alpha = float(alpha)
        self.use_bigrams = bool(use_bigrams)
        self.use_subwords = bool(use_subwords)
        self.class_counts: Dict[str, int] = {}
        self.token_counts: Dict[str, Dict[str, int]] = {}
        self.class_totals: Dict[str, int] = {}
        self.vocab: set[str] = set()

    def _extract_features(self, text: str) -> List[str]:
        if not text:
            return []
        normed = normalize(text.lower())
        toks = _RE_TOK.findall(normed)
        feats: List[str] = list(toks)
        if self.use_bigrams and len(toks) > 1:
            for i in range(len(toks) - 1):
                feats.append(f"{toks[i]}_{toks[i + 1]}")
        if self.use_subwords:
            for w in toks:
                if len(w) >= 5 and _RE_ALPHA.match(w):
                    feats.append(f"p3:{w[:3]}")
                    feats.append(f"s3:{w[-3:]}")
        return feats

    def fit(self, texts: Sequence[str], labels: Sequence[str]) -> "DarjaClassifier":
        """Train classifier from scratch on texts and labels."""
        if len(texts) != len(labels):
            raise ValueError("texts and labels must have the same length")
        self.class_counts = {}
        self.token_counts = {}
        self.class_totals = {}
        self.vocab = set()
        return self.partial_fit(texts, labels)

    def partial_fit(self, texts: Sequence[str], labels: Sequence[str]) -> "DarjaClassifier":
        """Incrementally update classifier with additional training samples."""
        if len(texts) != len(labels):
            raise ValueError("texts and labels must have the same length")
        for text, label in zip(texts, labels):
            lbl = str(label)
            if lbl not in self.class_counts:
                self.class_counts[lbl] = 0
                self.token_counts[lbl] = {}
                self.class_totals[lbl] = 0
            self.class_counts[lbl] += 1
            feats = self._extract_features(text)
            c_map = self.token_counts[lbl]
            for f in feats:
                c_map[f] = c_map.get(f, 0) + 1
                self.class_totals[lbl] += 1
                self.vocab.add(f)
        return self

    def predict(self, text: str) -> ClassificationPrediction:
        """Predict label and calibrated class probabilities for a Darja text."""
        if not self.class_counts:
            raise ValueError("Classifier has not been fitted yet")

        labels = sorted(self.class_counts.keys())
        total_docs = sum(self.class_counts.values())
        v_size = max(1, len(self.vocab))
        feats = self._extract_features(text)

        log_scores: Dict[str, float] = {}
        for lbl in labels:
            prior = math.log(self.class_counts[lbl] / total_docs)
            denom = self.class_totals[lbl] + self.alpha * v_size
            c_map = self.token_counts[lbl]
            score = prior
            for f in feats:
                if f in self.vocab:
                    score += math.log((c_map.get(f, 0) + self.alpha) / denom)
            log_scores[lbl] = score

        max_s = max(log_scores.values())
        exps = {lbl: math.exp(max(-50.0, s - max_s)) for lbl, s in log_scores.items()}
        exp_sum = sum(exps.values()) or 1.0
        probs = {lbl: round(v / exp_sum, 4) for lbl, v in exps.items()}
        best_label = max(labels, key=lambda l: (probs[l], log_scores[l]))
        return ClassificationPrediction(
            label=best_label,
            confidence=probs[best_label],
            probabilities=probs,
        )

    def predict_batch(self, texts: Sequence[str]) -> List[ClassificationPrediction]:
        return [self.predict(t) for t in texts]

    def evaluate(self, texts: Sequence[str], labels: Sequence[str]) -> EvaluationResult:
        """Evaluate accuracy, precision, recall, and macro-F1 on labeled samples."""
        if len(texts) != len(labels):
            raise ValueError("texts and labels must have the same length")
        if not texts:
            return EvaluationResult(accuracy=0.0, macro_f1=0.0, total=0, correct=0)

        tp: Counter[str] = Counter()
        fp: Counter[str] = Counter()
        fn: Counter[str] = Counter()
        correct = 0
        all_labels = sorted(set(str(l) for l in labels) | set(self.class_counts.keys()))

        for text, true_l in zip(texts, labels):
            true_str = str(true_l)
            pred = self.predict(text).label
            if pred == true_str:
                correct += 1
                tp[true_str] += 1
            else:
                fp[pred] += 1
                fn[true_str] += 1

        per_class: Dict[str, Dict[str, float]] = {}
        f1_sum = 0.0
        present_classes = 0
        for lbl in all_labels:
            support = tp[lbl] + fn[lbl]
            prec = tp[lbl] / (tp[lbl] + fp[lbl]) if (tp[lbl] + fp[lbl]) > 0 else 0.0
            rec = tp[lbl] / support if support > 0 else 0.0
            f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
            if support > 0:
                f1_sum += f1
                present_classes += 1
            per_class[lbl] = {
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1": round(f1, 4),
                "support": float(support),
            }

        total = len(texts)
        return EvaluationResult(
            accuracy=round(correct / total, 4),
            macro_f1=round(f1_sum / present_classes, 4) if present_classes else 0.0,
            total=total,
            correct=correct,
            per_class=per_class,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "alpha": self.alpha,
            "use_bigrams": self.use_bigrams,
            "use_subwords": self.use_subwords,
            "class_counts": self.class_counts,
            "class_totals": self.class_totals,
            "token_counts": self.token_counts,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DarjaClassifier":
        obj = cls(
            alpha=float(data.get("alpha", 1.0)),
            use_bigrams=bool(data.get("use_bigrams", True)),
            use_subwords=bool(data.get("use_subwords", True)),
        )
        obj.class_counts = {str(k): int(v) for k, v in data.get("class_counts", {}).items()}
        obj.class_totals = {str(k): int(v) for k, v in data.get("class_totals", {}).items()}
        obj.token_counts = {
            str(lbl): {str(tok): int(cnt) for tok, cnt in tmap.items()}
            for lbl, tmap in data.get("token_counts", {}).items()
        }
        vocab: set[str] = set()
        for tmap in obj.token_counts.values():
            vocab.update(tmap.keys())
        obj.vocab = vocab
        return obj

    def save(self, filepath: Union[str, Path]) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "DarjaClassifier":
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
