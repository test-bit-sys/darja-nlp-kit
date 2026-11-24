"""Unified configurable NLP pipeline and convenience facade for Algerian Darja."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .agent import build_agent_context, format_agent_system_prompt
from .arabizi import ArabiziOptions, arabizi_to_arabic
from .cultural import (
    CulturalAnalysisResult,
    detect_cultural_references,
    detect_franco_darja,
)
from .dialect import DialectResult, detect_dialect
from .dialogue import DialogueResponse, DialogueStrategy, PersonaType, ScriptType, respond_to_darja
from .entities import EntitiesResult, extract_entities
from .escalation import EscalationResult, detect_escalation
from .intent import IntentResult, identify_intent
from .normalizer import NormalizeOptions, normalize
from .profanity import ProfanityResult, censor_profanity, detect_profanity
from .sentiment import SentimentMode, SentimentResult, analyze_sentiment
from .stopwords import remove_stopwords


@dataclass
class AnalysisReport:
    """Structured end-to-end NLP report for an Algerian Darja message."""
    raw_text: str
    normalized: Optional[str] = None
    arabic: Optional[str] = None
    cleaned: Optional[str] = None
    sentiment: Optional[SentimentResult] = None
    intent: Optional[IntentResult] = None
    dialect: Optional[DialectResult] = None
    entities: Optional[EntitiesResult] = None
    escalation: Optional[EscalationResult] = None
    profanity: Optional[ProfanityResult] = None
    cultural: Optional[CulturalAnalysisResult] = None
    franco_darja: Optional[List[Dict[str, Any]]] = None
    reply: Optional[DialogueResponse] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete analysis report to plain Python dict (JSON-ready)."""
        return asdict(self)


class DarjaPipeline:
    """Flexible, customizable NLP pipeline for Algerian Darja processing and automation."""

    ALL_TASKS = (
        'normalize',
        'arabizi',
        'clean',
        'sentiment',
        'intent',
        'dialect',
        'entities',
        'escalation',
        'profanity',
        'cultural',
        'franco',
        'reply',
    )

    def __init__(
        self,
        store_name: str = "Bazar El Djazair",
        persona: PersonaType = "casual",
        script: ScriptType = "auto",
        sentiment_mode: SentimentMode = "hybrid",
        dialogue_strategy: DialogueStrategy = "auto",
        preserve_french: bool = True,
        custom_positive: Optional[Dict[str, float]] = None,
        custom_negative: Optional[Dict[str, float]] = None,
        custom_stopwords: Optional[Iterable[str]] = None,
        custom_profanity: Optional[Iterable[str]] = None,
        custom_rules: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.store_name = store_name
        self.persona = persona
        self.script = script
        self.sentiment_mode = sentiment_mode
        self.dialogue_strategy = dialogue_strategy
        self.preserve_french = preserve_french
        self.custom_positive: Dict[str, float] = dict(custom_positive or {})
        self.custom_negative: Dict[str, float] = dict(custom_negative or {})
        self.custom_stopwords: set[str] = {w.lower() for w in (custom_stopwords or []) if w}
        self.custom_profanity: List[str] = list(custom_profanity or [])
        self.custom_rules: List[Dict[str, Any]] = list(custom_rules or [])

    def extend_lexicon(
        self,
        positive: Optional[Dict[str, float]] = None,
        negative: Optional[Dict[str, float]] = None,
    ) -> "DarjaPipeline":
        """Dynamically add custom positive or negative lexicon weights."""
        if positive:
            self.custom_positive.update(positive)
        if negative:
            self.custom_negative.update(negative)
        return self

    def add_stopwords(self, words: Iterable[str]) -> "DarjaPipeline":
        """Dynamically add domain-specific stopwords."""
        for w in words:
            if w and w.strip():
                self.custom_stopwords.add(w.strip().lower())
        return self

    def add_profanity(self, terms: Iterable[str]) -> "DarjaPipeline":
        """Dynamically register additional custom blocked/profane terms."""
        for t in terms:
            if t and t.strip() and t.strip() not in self.custom_profanity:
                self.custom_profanity.append(t.strip())
        return self

    def add_dialogue_rule(self, rule: Dict[str, Any]) -> "DarjaPipeline":
        """Register a custom conversational rule prioritized ahead of built-in rules."""
        self.custom_rules.append(rule)
        return self

    def clean(self, text: str) -> str:
        """Normalize text and remove both standard Darja and custom stopwords."""
        if not text:
            return ''
        base_cleaned = remove_stopwords(normalize(text))
        if not self.custom_stopwords:
            return base_cleaned
        return ' '.join(
            tok for tok in base_cleaned.split()
            if tok.lower() not in self.custom_stopwords
        )

    def moderate(self, text: str, mask: str = "***") -> ProfanityResult:
        """Run profanity detection and return result with masked censored_text."""
        res = detect_profanity(text, custom_terms=self.custom_profanity or None)
        if res.is_profane and mask != "***":
            res.censored_text = censor_profanity(text, mask=mask, custom_terms=self.custom_profanity or None)
        return res

    def reply(
        self,
        text: str,
        vary: bool = False,
        strategy: Optional[DialogueStrategy] = None,
        persona: Optional[PersonaType] = None,
        script: Optional[ScriptType] = None,
    ) -> DialogueResponse:
        """Generate an Algerian conversational reply using pipeline configuration."""
        return respond_to_darja(
            text,
            persona=persona or self.persona,
            script=script or self.script,
            strategy=strategy or self.dialogue_strategy,
            vary=vary,
            custom_rules=self.custom_rules or None,
        )

    def build_prompt(self, text: str) -> str:
        """Build grounded LLM system prompt ready for GPT-4o / Gemini / Claude / Llama."""
        ctx = build_agent_context(text, store_name=self.store_name)
        return format_agent_system_prompt(ctx)

    def analyze(
        self,
        text: str,
        tasks: Optional[Sequence[str]] = None,
        include_reply: bool = True,
    ) -> AnalysisReport:
        """Run end-to-end or selective NLP analysis on a single Darja message."""
        active = set(tasks) if tasks is not None else set(self.ALL_TASKS)
        if not include_reply and tasks is None:
            active.discard('reply')

        return AnalysisReport(
            raw_text=text,
            normalized=normalize(text, NormalizeOptions()) if 'normalize' in active else None,
            arabic=arabizi_to_arabic(text, ArabiziOptions(preserve_french=self.preserve_french)) if 'arabizi' in active else None,
            cleaned=self.clean(text) if 'clean' in active else None,
            sentiment=analyze_sentiment(
                text,
                mode=self.sentiment_mode,
                custom_positive=self.custom_positive or None,
                custom_negative=self.custom_negative or None,
            ) if 'sentiment' in active else None,
            intent=identify_intent(text) if 'intent' in active else None,
            dialect=detect_dialect(text) if 'dialect' in active else None,
            entities=extract_entities(text) if 'entities' in active else None,
            escalation=detect_escalation(text) if 'escalation' in active else None,
            profanity=detect_profanity(text, custom_terms=self.custom_profanity or None) if 'profanity' in active else None,
            cultural=detect_cultural_references(text) if 'cultural' in active else None,
            franco_darja=detect_franco_darja(text) if 'franco' in active else None,
            reply=self.reply(text) if 'reply' in active else None,
        )

    def analyze_batch(
        self,
        texts: Sequence[str],
        tasks: Optional[Sequence[str]] = None,
        include_reply: bool = True,
    ) -> List[AnalysisReport]:
        """Run pipeline analysis over a list of Darja messages."""
        return [self.analyze(t, tasks=tasks, include_reply=include_reply) for t in texts]


_default_pipeline: Optional[DarjaPipeline] = None


def analyze(
    text: str,
    *,
    tasks: Optional[Sequence[str]] = None,
    include_reply: bool = True,
    persona: PersonaType = "casual",
    sentiment_mode: SentimentMode = "hybrid",
) -> AnalysisReport:
    """One-call shortcut to analyze any Algerian Darja text across all NLP modules."""
    global _default_pipeline
    if persona == "casual" and sentiment_mode == "hybrid":
        if _default_pipeline is None:
            _default_pipeline = DarjaPipeline()
        return _default_pipeline.analyze(text, tasks=tasks, include_reply=include_reply)
    return DarjaPipeline(persona=persona, sentiment_mode=sentiment_mode).analyze(
        text, tasks=tasks, include_reply=include_reply
    )
