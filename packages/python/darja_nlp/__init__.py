"""darja-nlp-kit: Zero-dependency NLP toolkit for Algerian Darja."""
from .normalizer import normalize, NormalizeOptions
from .arabizi import arabizi_to_arabic, ArabiziOptions
from .stopwords import (
    tokenize,
    remove_stopwords,
    is_stopword,
    get_stopwords,
    TokenizeResult,
    NegationInfo,
)
from .sentiment import analyze_sentiment, SentimentResult
from .entities import (
    extract_entities,
    get_wilayas,
    get_wilaya_by_code,
    EntitiesResult,
    WilayaEntity,
    PaymentEntity,
    PriceEntity,
    DeliveryEntity,
    DeliveryModeEntity,
    PhoneEntity,
    TelecomOperator,
)
from .quantities import (
    QuantityEntity,
    ProductAttributes,
    extract_quantities,
    extract_product_attributes,
)
from .escalation import (
    detect_escalation,
    EscalationResult,
    EscalationUrgency,
    EscalationReason,
)
from .dialect import detect_dialect, DialectResult, get_dialect_metadata
from .intent import identify_intent, IntentResult, IntentType
from .agent import (
    build_agent_context,
    format_agent_system_prompt,
    get_openai_tool_definitions,
    get_few_shot_dialogues,
)
from .server import start_server

__version__ = '1.0.0'

__all__ = [
    'normalize',
    'NormalizeOptions',
    'arabizi_to_arabic',
    'ArabiziOptions',
    'tokenize',
    'remove_stopwords',
    'is_stopword',
    'get_stopwords',
    'TokenizeResult',
    'NegationInfo',
    'analyze_sentiment',
    'SentimentResult',
    'extract_entities',
    'get_wilayas',
    'get_wilaya_by_code',
    'EntitiesResult',
    'WilayaEntity',
    'PaymentEntity',
    'PriceEntity',
    'DeliveryEntity',
    'DeliveryModeEntity',
    'PhoneEntity',
    'TelecomOperator',
    'QuantityEntity',
    'ProductAttributes',
    'extract_quantities',
    'extract_product_attributes',
    'detect_escalation',
    'EscalationResult',
    'EscalationUrgency',
    'EscalationReason',
    'detect_dialect',
    'DialectResult',
    'get_dialect_metadata',
    'identify_intent',
    'IntentResult',
    'IntentType',
    'build_agent_context',
    'format_agent_system_prompt',
    'get_openai_tool_definitions',
    'get_few_shot_dialogues',
    'start_server',
]
