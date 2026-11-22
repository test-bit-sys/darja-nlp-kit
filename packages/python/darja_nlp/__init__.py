"""darja-nlp-kit: Zero-dependency NLP toolkit for Algerian Darja."""
from .normalizer import normalize, NormalizeOptions
from .arabizi import arabizi_to_arabic, ArabiziOptions
from .stopwords import tokenize, remove_stopwords, is_stopword, get_stopwords, TokenizeResult, NegationInfo
from .sentiment import analyze_sentiment, SentimentResult

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
]
