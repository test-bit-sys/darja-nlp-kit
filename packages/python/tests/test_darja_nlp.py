"""Tests for darja-nlp-kit Python package."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from darja_nlp.normalizer import normalize, NormalizeOptions
from darja_nlp.arabizi import arabizi_to_arabic, ArabiziOptions
from darja_nlp.stopwords import tokenize, remove_stopwords, is_stopword
from darja_nlp.sentiment import analyze_sentiment
from darja_nlp.entities import extract_entities, get_wilayas, get_wilaya_by_code
from darja_nlp.dialect import detect_dialect
from darja_nlp.intent import identify_intent
from darja_nlp.quantities import extract_quantities, extract_product_attributes
from darja_nlp.escalation import detect_escalation
from darja_nlp.agent import build_agent_context, format_agent_system_prompt


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


class TestEntities:

    def test_register_69_wilayas(self) -> None:
        wilayas = get_wilayas()
        assert len(wilayas) == 69

    def test_find_wilaya_by_code(self) -> None:
        alger = get_wilaya_by_code(16)
        assert alger is not None
        assert alger['name_fr'] == 'Alger'

        bousaada = get_wilaya_by_code(68)
        assert bousaada is not None
        assert bousaada['name_ar'] == 'بوسعادة'

        elabiodh = get_wilaya_by_code('69')
        assert elabiodh is not None
        assert elabiodh['name_fr'] == 'El Abiodh Sidi Cheikh'

    def test_extract_wilaya_entities(self) -> None:
        res1 = extract_entities('livraison l 16')
        assert any(w.code == 16 for w in res1.wilayas)

        res2 = extract_entities('حاب نشري في وهران و نبعث لسطيف')
        assert any(w.code == 31 for w in res2.wilayas)
        assert any(w.code == 19 for w in res2.wilayas)

        res3 = extract_entities('توصيل لبوسعادة و البهجة')
        assert any(w.code == 68 for w in res3.wilayas)
        assert any(w.code == 16 for w in res3.wilayas)

    def test_extract_payment_methods(self) -> None:
        text = 'نخلصك عبر baridimob او كاش عند الاستلام او بالذهبية'
        res = extract_entities(text)
        assert any(p.type == 'BARIDIMOB' for p in res.payments)
        assert any(p.type == 'COD' for p in res.payments)
        assert any(p.type == 'EDAHABIA' for p in res.payments)

    def test_extract_prices(self) -> None:
        text1 = 'السعر 4500 DA و التوصيل بـ 500 دج'
        res1 = extract_entities(text1)
        assert any(p.amount == 4500.0 for p in res1.prices)
        assert any(p.amount == 500.0 for p in res1.prices)

        text2 = 'سلعة شريتها بـ زوج ملاين و بقاتلي مية الف'
        res2 = extract_entities(text2)
        assert any(p.amount == 20000.0 for p in res2.prices)
        assert any(p.amount == 1000.0 for p in res2.prices)

        text3 = 'سومتها 3 mlayen و سلعة ثانية 5 ملاين'
        res3 = extract_entities(text3)
        assert any(p.amount == 30000.0 for p in res3.prices)
        assert any(p.amount == 50000.0 for p in res3.prices)

    def test_extract_delivery_companies_and_mode(self) -> None:
        text = 'ابعثهالي مع yalidine stop desk و خلاص كاش'
        res = extract_entities(text)
        assert any(d.company == 'YALIDINE' for d in res.deliveries)
        assert res.delivery_mode is not None
        assert res.delivery_mode.mode == 'STOP_DESK'

        text2 = 'livraison a domicile zr express'
        res2 = extract_entities(text2)
        assert any(d.company == 'ZR_EXPRESS' for d in res2.deliveries)
        assert res2.delivery_mode is not None
        assert res2.delivery_mode.mode == 'HOME_DELIVERY'

    def test_extract_algerian_phones(self) -> None:
        text = 'عيطلي في 0661234567 ولا +213 555 12 34 56'
        res = extract_entities(text)
        assert len(res.phones) == 2
        assert any(p.normalized == '0661234567' for p in res.phones)
        assert any(p.normalized == '0555123456' for p in res.phones)

    def test_resolve_algerian_communes(self) -> None:
        res1 = extract_entities('livrili l Rouiba svp')
        assert any(w.code == 16 and w.commune == 'Rouiba' for w in res1.wilayas)

        res2 = extract_entities('حاب نشري سلعة في العلمة')
        assert any(w.code == 19 and w.commune == 'العلمة' for w in res2.wilayas)

        res3 = extract_entities('livraison l عين الترك')
        assert any(w.code == 31 and w.commune == 'عين الترك' for w in res3.wilayas)

        res4 = extract_entities('rani f حاسي مسعود')
        assert any(w.code == 30 and w.commune == 'حاسي مسعود' for w in res4.wilayas)

    def test_compound_darja_prices(self) -> None:
        res1 = extract_entities('سومة هاذي زوج ملاين و خمسمية الف')
        assert any(p.amount == 25000 for p in res1.prices)

        res2 = extract_entities('chrit b 3 mlayen w 500 alf')
        assert any(p.amount == 35000 for p in res2.prices)

        res3 = extract_entities('حسابك زوج ملاين و خمسين الف')
        assert any(p.amount == 20500 for p in res3.prices)

        res4 = extract_entities('سعرها مليون و ميتين الف')
        assert any(p.amount == 12000 for p in res4.prices)


class TestIntent:

    def test_order_intent(self) -> None:
        res = identify_intent('سلام خاوتي حاب نكوموندي زوج حبات ابعثهالي للدار')
        assert res.intent == 'ORDER'
        assert res.confidence >= 0.7

    def test_price_inquiry_intent(self) -> None:
        res = identify_intent('بشحال هادي خاوة شحال السومة تاعها؟')
        assert res.intent == 'PRICE_INQUIRY'
        assert res.confidence >= 0.7

    def test_availability_inquiry_intent(self) -> None:
        res = identify_intent('سلام عليكم كاين منها هادي مازالت ديسبو عندكم؟')
        assert res.intent == 'AVAILABILITY_INQUIRY'
        assert res.confidence >= 0.7

    def test_delivery_inquiry_intent(self) -> None:
        res = identify_intent('شحال التوصيل لوهران و وقتاش تلحق؟')
        assert res.intent == 'DELIVERY_INQUIRY'
        assert res.confidence >= 0.7

    def test_complaint_intent(self) -> None:
        res = identify_intent('سلعة مكسرة ومفاتشة حشيتوهالي رجعولي دراهمي روتور')
        assert res.intent == 'COMPLAINT'
        assert res.confidence >= 0.7

    def test_greeting_intent(self) -> None:
        res = identify_intent('السلام عليكم واش راك خويا لعزيز')
        assert res.intent == 'GREETING'
        assert res.confidence >= 0.7

    def test_unknown_intent(self) -> None:
        res = identify_intent('طاولة خشبية زرقاء 123')
        assert res.intent == 'UNKNOWN'
        assert res.confidence == 0.0


class TestAIAgent:

    def test_build_agent_context(self) -> None:
        msg = 'salam khoya rani baghi had lproduit b 2 mlayen l Constantine wla nversilk f baridimob? num ta3i 0770112233'
        ctx = build_agent_context(msg)
        assert any('قسنطينة' in w for w in ctx['grounded_facts']['wilayas'])
        assert any('20,000' in p for p in ctx['grounded_facts']['prices_dzd'])
        assert any('BaridiMob' in p for p in ctx['grounded_facts']['payments'])
        assert any('0770112233' in p for p in ctx['grounded_facts']['phones'])
        assert ctx['dialect']['region'] == 'WEST'
        assert ctx['intent']['intent'] == 'ORDER'
        assert 'طلب شراء' in ctx['intent']['guideline']

    def test_format_system_prompt(self) -> None:
        msg = 'khedma 3ayana w sil3a khorda 7chawhali'
        ctx = build_agent_context(msg)
        prompt = format_agent_system_prompt(ctx)
        assert 'NEGATIVE' in prompt
        assert 'COMPLAINT' in prompt
        assert 'Escalation Triggered' in prompt


class TestDialect:

    def test_western_dialect(self) -> None:
        res = detect_dialect('شوالا راك باغي خوية غايا درك؟')
        assert res.region == 'WEST'
        assert res.confidence > 0.6

    def test_eastern_dialect(self) -> None:
        res = detect_dialect('واشنهي هادا قداش يدير ياسر باهي')
        assert res.region == 'EAST'
        assert res.confidence > 0.6

    def test_central_dialect(self) -> None:
        res = detect_dialect('واشنو هكداك حوايج العاصمة دروك')
        assert res.region == 'CENTER'
        assert res.confidence > 0.6

    def test_general_dialect(self) -> None:
        res = detect_dialect('سلام عليكم شكرا')
        assert res.region == 'GENERAL_DARJA'


class TestTelecomOperators:

    def test_mobilis_detection(self) -> None:
        res = extract_entities('اتصل بي على 0661234567')
        assert len(res.phones) == 1
        ph = res.phones[0]
        assert ph.operator == 'MOBILIS'
        assert 'Mobilis' in ph.operator_label
        assert ph.formatted == '+213 661 23 45 67'
        assert ph.whatsapp_url == 'https://wa.me/213661234567'

    def test_djezzy_detection(self) -> None:
        res = extract_entities('mon numero 0770112233')
        assert len(res.phones) == 1
        ph = res.phones[0]
        assert ph.operator == 'DJEZZY'
        assert 'Djezzy' in ph.operator_label
        assert ph.whatsapp_url == 'https://wa.me/213770112233'

    def test_ooredoo_detection(self) -> None:
        res = extract_entities('0550998877')
        assert len(res.phones) == 1
        ph = res.phones[0]
        assert ph.operator == 'OOREDOO'
        assert 'Ooredoo' in ph.operator_label
        assert ph.whatsapp_url == 'https://wa.me/213550998877'

    def test_landline_algerie_telecom(self) -> None:
        res = extract_entities('fixe 021 23 45 67')
        assert len(res.phones) == 1
        ph = res.phones[0]
        assert ph.operator == 'ALGERIE_TELECOM'
        assert ph.whatsapp_url is None


class TestQuantitiesAndAttributes:

    def test_colloquial_arabic_quantities(self) -> None:
        quants = extract_quantities('حاب 2 حبات و 3 شكاير و دوزينة')
        assert len(quants) == 3
        assert quants[0].value == 2 and quants[0].unit == 'حبة'
        assert quants[1].value == 3 and quants[1].unit == 'شكارة'
        assert quants[2].value == 12 and quants[2].unit == 'دوزينة'

    def test_colloquial_arabizi_quantities(self) -> None:
        quants = extract_quantities('zouj hbat w tlata boites w douzina')
        assert len(quants) == 3
        assert quants[0].value == 2 and quants[0].unit == 'حبة'
        assert quants[1].value == 3 and quants[1].unit == 'باكية'
        assert quants[2].value == 12 and quants[2].unit == 'دوزينة'

    def test_product_attributes_colors_and_sizes(self) -> None:
        attrs = extract_product_attributes('بيجاما كحلة وبيضا مقاس XL وبونتير 42')
        assert any('كحل' in c for c in attrs.colors)
        assert any('بيض' in c for c in attrs.colors)
        assert 'XL' in attrs.sizes
        assert '42' in attrs.sizes


class TestEscalationDetection:

    def test_legal_threat_escalation(self) -> None:
        res = detect_escalation('نشكي بيكم للعدالة ولابوليس')
        assert res.needs_escalation is True
        assert res.urgency == 'CRITICAL'
        assert res.reason == 'LEGAL_THREAT'

    def test_angry_customer_escalation(self) -> None:
        res = detect_escalation('سراقين حشيتوهالي رجعولي دراهمي')
        assert res.needs_escalation is True
        assert res.urgency == 'HIGH'
        assert res.reason == 'ANGRY_CUSTOMER'

    def test_human_requested_escalation(self) -> None:
        res = detect_escalation('حاب نهدر مع بنادم عيطولي')
        assert res.needs_escalation is True
        assert res.urgency == 'HIGH'
        assert res.reason == 'HUMAN_REQUESTED'

    def test_no_escalation_on_normal_message(self) -> None:
        res = detect_escalation('سلام عليكم متوفر هذا الموديل؟')
        assert res.needs_escalation is False
        assert res.urgency == 'NONE'
        assert res.reason is None


class TestAgentContextWithEscalation:

    def test_agent_context_includes_new_features(self) -> None:
        msg = 'حاب 2 حبات كحلة مقاس XL لوهران 0661234567'
        ctx = build_agent_context(msg)
        assert 'escalation' in ctx
        assert ctx['escalation']['needs_escalation'] is False
        assert any('Mobilis' in p for p in ctx['grounded_facts']['phones'])
        assert any('2' in q and 'حبة' in q for q in ctx['grounded_facts']['quantities'])
        assert any('كحل' in c for c in ctx['grounded_facts']['product_attributes']['colors'])
        assert 'XL' in ctx['grounded_facts']['product_attributes']['sizes']

    def test_system_prompt_escalation_alert(self) -> None:
        msg = 'سراقين حشيتوهالي رجعولي دراهمي'
        ctx = build_agent_context(msg)
        prompt = format_agent_system_prompt(ctx)
        assert 'Escalation Triggered' in prompt
        assert 'ANGRY_CUSTOMER' in prompt
