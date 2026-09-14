"""
NLP engine: preprocessing -> Pure Python Multinomial Naive Bayes -> confidence gate.
No numpy or scikit-learn required.
"""

import json
import re
import math
from typing import Dict, List, Optional, Tuple
from .config import CONFIDENCE_THRESHOLD

_PUNCT_RE = re.compile(r"[^\w\s\u00f1\u00e1\u00e9\u00ed\u00f3\u00fa\u00e0\u00e8\u00ec\u00f2\u00f9\u00e2\u00ea\u00ee\u00f4\u00fb]", re.UNICODE)
_WS_RE = re.compile(r"\s+")

def preprocess(text: str) -> str:
    text = (text or "").lower().strip()
    text = _PUNCT_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)
    return text

_FIL_MARKERS = {"paano", "ano", "mga", "ng", "sa", "ako", "ko", "kailangan", "gusto", "saan", "para", "makita", "kumuha", "mag", "ngayon", "ba", "po", "ang", "hindi", "pwede", "kelan", "kailan", "ito", "iyan", "yung", "naman", "salamat", "meron"}

def detect_language(text: str) -> str:
    tokens = set(preprocess(text).split())
    return "fil" if tokens & _FIL_MARKERS else "en"

_YEAR_RE = re.compile(r"\b(1st|2nd|3rd|4th|first|second|third|fourth)\s*(year|yr)\b", re.IGNORECASE)
_SEM_RE = re.compile(r"\b(1st|2nd|first|second)\s*(sem|semester)\b", re.IGNORECASE)
_DOC_TOKENS = ["tor", "cog", "certificate", "diploma", "form 137", "good moral"]

def extract_entities(text: str) -> Dict[str, str]:
    t = text.lower()
    ents: Dict[str, str] = {}
    m = _YEAR_RE.search(t)
    if m: ents["year_level"] = m.group(0).strip()
    m = _SEM_RE.search(t)
    if m: ents["semester"] = m.group(0).strip()
    for doc in _DOC_TOKENS:
        if doc in t:
            ents["document"] = doc.upper()
            break
    return ents

class IntentClassifier:
    def __init__(self):
        self.class_priors: Dict[str, float] = {}
        self.word_counts: Dict[str, Dict[str, int]] = {}
        self.class_total_words: Dict[str, int] = {}
        self.vocab: set = set()
        self._trained = False
        self.alpha = 1.0  # Laplace smoothing

    @property
    def is_trained(self) -> bool:
        return self._trained

    def train(self, samples: List[str], labels: List[str]) -> None:
        if not samples or len(set(labels)) < 2:
            self._trained = False
            return

        self.class_priors = {}
        self.word_counts = {}
        self.class_total_words = {}
        self.vocab = set()

        class_sample_counts: Dict[str, int] = {}
        total_samples = len(samples)

        for text, label in zip(samples, labels):
            class_sample_counts[label] = class_sample_counts.get(label, 0) + 1
            tokens = preprocess(text).split()
            self.vocab.update(tokens)

        for text, label in zip(samples, labels):
            tokens = preprocess(text).split()
            if label not in self.word_counts:
                self.word_counts[label] = {}
                self.class_total_words[label] = 0
            for token in tokens:
                self.word_counts[label][token] = self.word_counts[label].get(token, 0) + 1
                self.class_total_words[label] += 1

        for label, count in class_sample_counts.items():
            self.class_priors[label] = math.log(count / total_samples)

        self._trained = True

    def predict(self, text: str) -> Tuple[Optional[str], float]:
        if not self._trained:
            return None, 0.0

        tokens = preprocess(text).split()
        if not tokens:
            return None, 0.0

        scores: Dict[str, float] = {}
        vocab_size = len(self.vocab)

        for label in self.class_priors:
            score = self.class_priors[label]
            total_words = self.class_total_words.get(label, 0)
            word_counts = self.word_counts.get(label, {})
            
            for token in tokens:
                count = word_counts.get(token, 0)
                prob = (count + self.alpha) / (total_words + self.alpha * vocab_size)
                score += math.log(prob)
            
            scores[label] = score

        max_score = max(scores.values())
        exp_scores = {label: math.exp(score - max_score) for label, score in scores.items()}
        sum_exp = sum(exp_scores.values())
        
        best_label = max(exp_scores, key=lambda k: exp_scores[k])
        confidence = exp_scores[best_label] / sum_exp

        return best_label, confidence

classifier = IntentClassifier()

def retrain_from_db(db) -> int:
    from .models import Intent
    samples: List[str] = []
    labels: List[str] = []
    for intent in db.query(Intent).all():
        try: utterances = json.loads(intent.sample_utterances)
        except (json.JSONDecodeError, TypeError): continue
        for u in utterances:
            if isinstance(u, str) and u.strip():
                samples.append(u)
                labels.append(intent.name)
    classifier.train(samples, labels)
    return len(samples)

def classify(text: str) -> Tuple[Optional[str], float, bool]:
    intent, confidence = classifier.predict(text)
    passed = intent is not None and confidence >= CONFIDENCE_THRESHOLD
    return (intent if passed else None), confidence, passed