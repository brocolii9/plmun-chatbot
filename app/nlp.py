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
_TOKEN_ALIASES = {
    # Enrollment
    "register": "enroll",
    "registering": "enroll",
    "registered": "enroll",
    "enrolled": "enroll",
    "eenroll": "enroll",
    "enrolling": "enroll",
    # Enrollment wording
    "registration": "enrollment",
    "magsimula": "start",
    "magsisimula": "start",
    "simula": "start",
    "begin": "start",
    "beginning": "start",

    # Subjects / classes
    "class": "subject",
    "classes": "subject",
    "subjects": "subject",
    "klase": "subject",
    # Add/drop/change
    "alisin": "drop",
    "tanggalin": "drop",
    "remove": "drop",
    "removing": "drop",
    "replace": "change",
    "replacing": "change",
    "load": "schedule",
    "credentials": "transfercredential",
    "term": "semester",
    "collect": "receive",
    "collecting": "receive",
    "confirming": "proof",

    # Scholarship
    "scholar": "scholarship",
    "scholars": "scholarship",
    "scholarships": "scholarship",

    # Grades / records
    "grades": "grade",
    "records": "record",
    "discrepancy": "problem",
    "discrepancies": "problem",
    "misspelled": "error",
    "spelling": "error",
    "incorrect": "wrong",
    "mali": "wrong",

    # Requests
    "requesting": "request",
    "requested": "request",
    "requests": "request",

    # Transfer
    "transferring": "transfer",
    "transferred": "transfer",

    # Processing
    "pinoprocess": "process",
    "processes": "process",
    "processed": "process",
    "processing": "process",
    "fees": "fee",

    # Graduation
    "graduates": "graduate",
    "graduating": "graduate",
    "graduated": "graduate",
    "grumaduate": "graduate",
    "makagraduate": "graduate",
    "makapagtapos": "graduate",

    # Documents
    "documents": "document",
    "certificates": "certificate",
    "diplomas": "diploma",

    # Other word forms
    "completing": "complete",
    "completed": "complete",
    "proving": "proof",
    "unang": "first",
    "studying": "study",
    "studies": "study",
    "withdrawing": "withdraw",
    "withdrawal": "withdraw",
    "universities": "university",
    "colleges": "college",
}
_PHRASE_ALIASES = {
    "certificate of matriculation": "com",
    "matriculation certificate": "com",
    "certificate of grades": "cog",
    "transcript of records": "tor",
    "academic transcript": "transcript",
    "leave of absence": "loa",
    "honorable dismissal": "transfercredential",
    "transfer credentials": "transfercredential",
    "financial aid": "scholarship",
    "certificate of enrollment": "certification",
    "proof of enrollment": "certification",
    "financial assistance": "scholarship",
    "take a break": "leave",
    "leaving for another school": "transfer",
    "another school": "transfer school",
    "another college": "transfer college",
    "another university": "transfer university",
    "student information": "record",
    "school record": "record",
    "university record": "record",
    "date of birth": "birthdate",
}

def preprocess(text: str) -> str:
    text = (text or "").lower().strip()
    text = _PUNCT_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text)

    for phrase, replacement in sorted(
        _PHRASE_ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        text = text.replace(phrase, replacement)

    tokens = text.split()

    normalized_tokens = [
        _TOKEN_ALIASES.get(token, token)
        for token in tokens
    ]

    return " ".join(normalized_tokens)

_INC_WORDS = {"inc", "incomplete"}
_INC_COMPLETION_WORDS = {
    "complete",
    "completion",
    "remove",
    "removal",
    "drop",
    "finish",
    "resolve",
}

def _has_inc_completion_signal(text: str) -> bool:
    tokens = set(preprocess(text).split())
    return bool(tokens & _INC_WORDS) and bool(tokens & _INC_COMPLETION_WORDS)

def has_intent_signal(intent: str, text: str) -> bool:
    tokens = set(preprocess(text).split())

    if not tokens:
        return False

    # 1. Enrollment procedure
    if intent == "enrollment_procedure":
        procedure_words = {
            "start",
            "first",
            "process",
            "step",
            "enroll",
            "enrollment",
        }

        requirement_words = {
            "requirement",
            "requirements",
            "document",
            "paper",
            "papers",
            "prepare",
            "bring",
            "submit",
            "kailangan",
            "dalhin",
            "ipasa",
        }

        return (
            bool(tokens & {"enroll", "enrollment"})
            and bool(tokens & procedure_words)
            and not bool(tokens & requirement_words)
        )

    # 2. Enrollment requirements
    if intent == "enrollment_requirements":
        enrollment_words = {"enroll", "enrollment"}

        requirement_words = {
            "requirement",
            "requirements",
            "document",
            "paper",
            "papers",
            "prepare",
            "bring",
            "submit",
            "need",
            "kailangan",
            "dalhin",
            "ipasa",
        }

        return (
            bool(tokens & enrollment_words)
            and bool(tokens & requirement_words)
        )

    # 3. Add / drop / change subject
    if intent == "add_drop_change_subjects":
        subject_words = {"subject"}

        action_words = {
            "add",
            "drop",
            "change",
            "schedule",
            "load",
            "magpalit",
        }

        return (
            bool(tokens & subject_words)
            and bool(tokens & action_words)
        )

    # 4. LOA / shifting / withdrawal
    if intent == "leave_of_absence_shifting":
        if tokens & {
            "loa",
            "leave",
            "shift",
            "withdraw",
            "break",
        }:
            return True

        if (
            tokens & {"lumipat", "lilipat"}
            and tokens & {"course", "program"}
        ):
            return True

        if (
            "study" in tokens
            and tokens & {"semester", "term"}
        ):
            return True

        return False

    # 5. TOR
    if intent == "tor_request":
        return bool(tokens & {"tor", "transcript"})

    # 6. Certification
    if intent == "certification_request":
        if tokens & {"cog", "com"}:
            return False

        return bool(
            tokens
            & {
                "certification",
                "certificate",
                "proof",
                "letter",
            }
        )

    # 7. Transfer credentials
    if intent == "transfer_credentials":
        if tokens & {
            "transfer",
            "transfercredential",
        }:
            return True

        if (
            tokens & {"lumipat", "lilipat"}
            and tokens & {
                "school",
                "university",
                "college",
            }
        ):
            return True

        return False

    # 8. Document fees / processing time
    if intent == "document_fees_processing_time":
        document_words = {
            "document",
            "record",
        }

        process_words = {
            "fee",
            "cost",
            "process",
            "request",
            "release",
            "ready",
            "receive",
            "collect",
            "days",
            "day",
            "soon",
            "magkano",
            "katagal",
            "bayad",
            "kuha",
            "kumuha",
        }

        return (
            bool(tokens & document_words)
            and bool(tokens & process_words)
        )

    # 9. Correction of records
    if intent == "correction_of_records":
        record_words = {
            "record",
            "name",
            "surname",
            "birthdate",
            "birthday",
            "details",
            "information",
        }

        error_words = {
            "wrong",
            "error",
            "correct",
            "correction",
            "fix",
            "palitan",
            "ayusin",
            "mali",
        }

        record_correction = (
            bool(tokens & record_words)
            and bool(tokens & error_words)
        )

        return record_correction or _has_inc_completion_signal(text)

    # 10. Graduation
    if intent == "graduation_requirements":
        return bool(tokens & {"graduation", "graduate"})

    # 11. Diploma / clearance
    if intent == "diploma_and_clearance":
        return bool(tokens & {"diploma", "clearance"})

    # 12. Registrar information
    if intent == "registrar_info":
        # A Registrar mention inside a document request
        # should not automatically become registrar_info.
        if "registrar" not in tokens:
            return False

        document_context = {
            "document",
            "tor",
            "cog",
            "com",
            "certificate",
            "transcript",
            "fee",
        }

        return not bool(tokens & document_context)

    # 13. Scholarship
    if intent == "scholarship_concerns":
        return "scholarship" in tokens

    # 14. Grade concern
    if intent == "grade_concern":
        return (
            "grade" in tokens
            and "cog" not in tokens
        )

    # 15. COG
    if intent == "cog_request":
        return "cog" in tokens

    # 16. COM
    if intent == "com_request":
        return bool(tokens & {"com", "matriculation"})

    return False

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

        num_classes = len(class_sample_counts)

        for label in class_sample_counts:
            self.class_priors[label] = math.log(1.0 / num_classes)

        self._trained = True

    def predict_proba(self, text: str) -> Dict[str, float]:
        if not self._trained:
            return {}

        tokens = [
            token
            for token in preprocess(text).split()
            if token in self.vocab
        ]

        if not tokens:
            return {}

        scores: Dict[str, float] = {}
        vocab_size = len(self.vocab)

        for label in self.class_priors:
            score = self.class_priors[label]
            total_words = self.class_total_words.get(label, 0)
            word_counts = self.word_counts.get(label, {})
            
            for token in tokens:
                count = word_counts.get(token, 0)
                prob = (
                    count + self.alpha
                ) / (
                    total_words
                    + self.alpha * vocab_size
                )
                score += math.log(prob)
            
            scores[label] = score

        max_score = max(scores.values())
        exp_scores = {
            label: math.exp(score - max_score)
            for label, score in scores.items()
        }
        total = sum(exp_scores.values())

        return {
            label: value / total
            for label, value in exp_scores.items()
        }

    def predict(self, text: str) -> Tuple[Optional[str], float]:
        probabilities = self.predict_proba(text)

        if not probabilities:
            return None, 0.0

        best_label = max(
            probabilities,
            key=probabilities.get
        )

        return best_label, probabilities[best_label]

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
    normalized = preprocess(text)
    tokens = normalized.split()

    # High-precision COM rule
    if "com" in tokens:
        return "com_request", 1.0, True

    # High-precision document fee / processing-time rule
    document_process_words = {
        "fee",
        "cost",
        "process",
        "request",
        "release",
        "ready",
        "receive",
        "collect",
        "day",
        "days",
        "soon",
        "magkano",
        "katagal",
        "bayad",
        "kuha",
        "kumuha",
    }

    if (
        "document" in tokens
        and bool(set(tokens) & document_process_words)
    ):
        return "document_fees_processing_time", 1.0, True

    probabilities = classifier.predict_proba(text)

    if not probabilities:
        return None, 0.0, False

    ranked = sorted(
        probabilities.items(),
        key=lambda item: item[1],
        reverse=True
    )

    top_intent, top_confidence = ranked[0]

    # Find every supported intent whose domain-specific
    # signal is actually present in the user's question.
    signal_matches = [
        intent
        for intent in probabilities
        if has_intent_signal(intent, text)
    ]

    # No valid PLMun/Registrar signal:
    # reject even if Naive Bayes is confident.
    if not signal_matches:
        return None, top_confidence, False

    # If only one intent matches the domain rules,
    # use it even when NB confidence is modest.
    if len(signal_matches) == 1:
        intent = signal_matches[0]
        confidence = probabilities[intent]

        if confidence >= 0.08 or (
            intent == "correction_of_records"
            and _has_inc_completion_signal(text)
        ):
            return intent, confidence, True

        return None, top_confidence, False

    # If several intents are possible, let Naive Bayes
    # choose the strongest one among those valid intents.
    best_intent = max(
        signal_matches,
        key=lambda intent: probabilities[intent]
    )

    confidence = probabilities[best_intent]

    if confidence >= CONFIDENCE_THRESHOLD:
        return best_intent, confidence, True

    return None, top_confidence, False