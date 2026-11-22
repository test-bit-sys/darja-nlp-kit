"""Tests for darja-nlp-kit Python package."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from darja_nlp.normalizer import normalize, NormalizeOptions
from darja_nlp.arabizi import arabizi_to_arabic, ArabiziOptions
from darja_nlp.stopwords import tokenize, remove_stopwords, is_stopword
from darja_nlp.sentiment import analyze_sentiment


class TestNormalize:

    def test_unify_alef_variants(self) -> None:
        assert normalize('أحمد إبراهيم آمنة') == 'احمد ابراهيم امنه'

    def test_ta_marbuta_to_ha(self) -> None:
        assert normalize('مدرسة جميلة') == 'مدرسه جميله'

    def test_alef_maqsura_to_ya(self) -> None:
        assert normalize('على موسى') == 'علي موسي'

    def test_strip_tashkeel(self) -> None:
        assert normalize('بِسْمِ اللَّهِ') == 'بسم الله'

    def test_preserve_tashkeel(self) -> None:
        opts = NormalizeOptions(preserve_tashkeel=True)
        result = normalize('بِسْمِ', opts)
        assert '\u0650' in result

    def test_strip_tatweel(self) -> None:
        assert normalize('كتـــاب') == 'كتاب'

    def test_reduce_arabic_elongation(self) -> None:
        assert normalize('بزاااااف') == 'بزاف'

    def test_reduce_latin_elongation(self) -> None:
        assert normalize('haaaayel') == 'hayel'

    def test_preserve_valid_doubles(self) -> None:
        result = normalize('allahhh')
        assert result == 'allah'

    def test_normalize_whitespace(self) -> None:
        assert normalize('كلمة    كلمة') == 'كلمه كلمه'

    def test_normalize_punctuation(self) -> None:
        assert normalize('واش!!!') == 'واش!'

    def test_empty_string(self) -> None:
        assert normalize('') == ''


class TestArabiziToArabic:

    def test_basic_transliteration(self) -> None:
        result = arabizi_to_arabic('salam')
        assert result == 'سلام'

    def test_number_mappings(self) -> None:
        result = arabizi_to_arabic('3lach')
        assert 'ع' in result

    def test_digraphs(self) -> None:
        result = arabizi_to_arabic('chkoun')
        assert result.startswith('ش')

    def test_preserve_french_by_default(self) -> None:
        result = arabizi_to_arabic('merci livraison')
        assert 'merci' in result
        assert 'livraison' in result

    def test_transliterate_french_when_disabled(self) -> None:
        opts = ArabiziOptions(preserve_french=False)
        result = arabizi_to_arabic('merci', opts)
        assert 'merci' not in result

    def test_irregular_overrides(self) -> None:
        assert arabizi_to_arabic('slm') == 'سلام'
        assert arabizi_to_arabic('nchallah') == 'ان شاء الله'
        assert arabizi_to_arabic('hamdoulah') == 'الحمد لله'

    def test_standalone_numbers_preserved(self) -> None:
        result = arabizi_to_arabic('prix 4500 DA')
        assert '4500' in result

    def test_phone_numbers_preserved(self) -> None:
        result = arabizi_to_arabic('0550123456')
        assert result == '0550123456'

    def test_mixed_arabizi_and_arabic(self) -> None:
        result = arabizi_to_arabic('هادا hayel')
        assert result.startswith('هادا')

    def test_code_switching_sentence(self) -> None:
        result = arabizi_to_arabic('produit mli7 livraison rapide')
        assert 'produit' in result
        assert 'livraison' in result
        assert 'rapide' in result

    def test_french_suffix_heuristics(self) -> None:
        result = arabizi_to_arabic('information')
        assert result == 'information'

    def test_preserve_standalone_numbers_while_converting_digits(self) -> None:
        res_numbers = arabizi_to_arabic('Prix 2500 DA w livraison l 16')
        assert '2500' in res_numbers
        assert '16' in res_numbers

        res_digits = arabizi_to_arabic('2ana 9rib')
        assert res_digits == 'انا قريب'

    def test_preserve_french_words_containing_digraphs(self) -> None:
        words = [
            'achat', 'chambre', 'douche', 'marche', 'couleur',
            'bouton', 'retour', 'choix', 'chargeur', 'compte', 'boutique'
        ]
        for word in words:
            assert arabizi_to_arabic(word) == word, f'Expected {word} to be preserved'

    def test_empty_string(self) -> None:
        assert arabizi_to_arabic('') == ''


class TestTokenize:

    def test_arabic_text(self) -> None:
        result = tokenize('هادا المنتج هايل بزاف')
        assert len(result.tokens) >= 4

    def test_mixed_arabic_latin(self) -> None:
        result = tokenize('هادا produit مليح')
        assert len(result.tokens) >= 3

    def test_arabic_circumfix_negation(self) -> None:
        result = tokenize('مافهمتش الحاجة')
        assert len(result.negations) > 0
        assert result.negations[0].negated is True
        assert result.negations[0].root == 'فهمت'

    def test_arabizi_circumfix_negation(self) -> None:
        result = tokenize('mafhamtch hadik')
        assert len(result.negations) > 0
        assert result.negations[0].negated is True
        assert result.negations[0].root == 'fhamt'

    def test_punctuation_stripped(self) -> None:
        result = tokenize('واش هادا? مشي مليح!')
        for token in result.tokens:
            assert '?' not in token and '!' not in token


class TestRemoveStopwords:

    def test_remove_arabic_stopwords(self) -> None:
        result = remove_stopwords('هادا المنتج تاع هايل')
        assert 'هادا' not in result
        assert 'تاع' not in result
        assert 'هايل' in result

    def test_remove_arabizi_stopwords(self) -> None:
        result = remove_stopwords('had produit ta3 hayel')
        assert 'had' not in result
        assert 'ta3' not in result

    def test_empty_string(self) -> None:
        assert remove_stopwords('') == ''


class TestIsStopword:

    def test_arabic_stopwords(self) -> None:
        assert is_stopword('تاع')
        assert is_stopword('واش')
        assert is_stopword('هادا')

    def test_arabizi_stopwords(self) -> None:
        assert is_stopword('ta3')
        assert is_stopword('wesh')
        assert is_stopword('hada')

    def test_prefix_stopword_detection(self) -> None:
        assert is_stopword('بالزربة')
        assert remove_stopwords('المنتوج هايل بالزربة') == 'المنتوج هايل'

    def test_non_stopwords(self) -> None:
        assert not is_stopword('هايل')
        assert not is_stopword('منتج')


class TestAnalyzeSentiment:

    def test_positive_sentiment(self) -> None:
        result = analyze_sentiment('هايل')
        assert result.label == 'POSITIVE'
        assert result.score > 0
        assert 'هايل' in result.positive_tokens

    def test_negative_sentiment(self) -> None:
        result = analyze_sentiment('عيان')
        assert result.label == 'NEGATIVE'
        assert result.score < 0
        assert 'عيان' in result.negative_tokens

    def test_negation_inversion(self) -> None:
        result = analyze_sentiment('ماشي هايل')
        assert result.score < 0, f'Expected negative score, got {result.score}'
        assert result.negated is True

    def test_double_negation_inversion_to_positive(self) -> None:
        arabic_res = analyze_sentiment('ماشي عيان')
        assert arabic_res.label == 'POSITIVE'
        assert arabic_res.score > 0
        assert arabic_res.negated is True

        arabizi_res = analyze_sentiment('machi 3ayan')
        assert arabizi_res.label == 'POSITIVE'
        assert arabizi_res.score > 0
        assert arabizi_res.negated is True

    def test_arabic_prefix_sentiment(self) -> None:
        result = analyze_sentiment('المنتوج هايل')
        assert result.label == 'POSITIVE'
        assert result.score > 0

    def test_intensifier_scaling(self) -> None:
        plain = analyze_sentiment('هايل')
        intensified = analyze_sentiment('هايل بزاف')
        assert intensified.score >= plain.score, (
            f'Intensified {intensified.score} should be >= plain {plain.score}'
        )

    def test_mixed_sentiment(self) -> None:
        result = analyze_sentiment('هايل بصح غالي')
        assert result.label == 'MIXED'
        assert len(result.positive_tokens) > 0
        assert len(result.negative_tokens) > 0

    def test_arabizi_sentiment(self) -> None:
        result = analyze_sentiment('hayel')
        assert result.label == 'POSITIVE'

    def test_french_loanword_sentiment(self) -> None:
        result = analyze_sentiment('parfait')
        assert result.label == 'POSITIVE'
        assert result.score > 0

    def test_ecommerce_code_switching(self) -> None:
        result = analyze_sentiment('المنتج هايل merci')
        assert result.score > 0

    def test_ecommerce_with_price(self) -> None:
        result = analyze_sentiment('المنتج مليح prix 4500 DA')
        assert result.score > 0

    def test_empty_text_neutral(self) -> None:
        result = analyze_sentiment('')
        assert result.label == 'NEUTRAL'
        assert result.score == 0.0

    def test_no_sentiment_words(self) -> None:
        result = analyze_sentiment('المنتج وصل')
        assert result.label == 'NEUTRAL'
