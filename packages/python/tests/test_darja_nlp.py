"""Tests for darja-nlp-kit Python package."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from darja_nlp.normalizer import normalize, NormalizeOptions
from darja_nlp.arabizi import arabizi_to_arabic, ArabiziOptions
from darja_nlp.stopwords import tokenize, remove_stopwords, is_stopword
from darja_nlp.sentiment import analyze_sentiment
from darja_nlp.entities import extract_entities, get_wilayas, get_wilaya_by_code
from darja_nlp.dialect import detect_dialect, get_dialect_metadata
from darja_nlp.intent import identify_intent
from darja_nlp.quantities import extract_quantities, extract_product_attributes
from darja_nlp.escalation import detect_escalation
from darja_nlp.agent import (
    build_agent_context,
    format_agent_system_prompt,
    get_few_shot_dialogues,
    get_openai_tool_definitions,
)
from darja_nlp.cultural import detect_cultural_references, get_cultural_data, get_slang_data
from darja_nlp.dialogue import respond_to_darja
from darja_nlp.profanity import detect_profanity, is_profane, censor_profanity


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


class TestDialectDataAndFewShot:

    def test_get_dialect_metadata(self) -> None:
        west_meta = get_dialect_metadata('WEST')
        assert 'الغرب' in west_meta['name_ar']
        assert len(west_meta['markers']) > 0

        east_meta = get_dialect_metadata('EAST')
        assert 'الشرق' in east_meta['name_ar']

        south_meta = get_dialect_metadata('SOUTH')
        assert 'الجنوب' in south_meta['name_ar']

    def test_get_few_shot_dialogues(self) -> None:
        west_dialogues = get_few_shot_dialogues('WEST', limit=2)
        assert len(west_dialogues) == 2
        assert all(d['region'] == 'WEST' for d in west_dialogues)

        east_dialogues = get_few_shot_dialogues('EAST', intent='ORDER', limit=2)
        assert len(east_dialogues) == 2
        assert any(d['intent'] == 'ORDER' for d in east_dialogues)

    def test_agent_context_includes_few_shots(self) -> None:
        msg = 'salam khoya kirak ghaya baghi nchri sberdina'
        ctx = build_agent_context(msg)
        assert 'few_shot_examples' in ctx
        assert len(ctx['few_shot_examples']) > 0
        prompt = format_agent_system_prompt(ctx)
        assert 'أمثلة واقعية لنبرة الرد' in prompt


class TestCulturalKnowledge:

    def test_cultural_data_loaded(self) -> None:
        cdata = get_cultural_data()
        assert len(cdata['proverbs']) >= 20
        assert len(cdata['memes_and_trends']) >= 10
        assert len(cdata['landmarks']) >= 10
        assert len(cdata['gastronomy']) >= 10

    def test_slang_data_loaded(self) -> None:
        sdata = get_slang_data()
        assert len(sdata['expressions']) >= 20

    def test_detect_proverbs_and_memes(self) -> None:
        text = 'الحجرة في بلاصتها ثقيلة وراك فاهم يا خويا'
        res = detect_cultural_references(text)
        assert res.has_cultural_reference is True
        assert any(p.canonical_name == 'الحجرة في بلاصتها ثقيلة' for p in res.proverbs)
        assert any(m.canonical_name == 'راك فاهم' for m in res.memes_and_trends)

    def test_detect_landmarks_and_gastronomy(self) -> None:
        text = 'حاب ناكل رشتة عاصمية وكرانتيكا حامية في باب الواد'
        res = detect_cultural_references(text)
        assert res.has_cultural_reference is True
        assert any('رشتة' in f.canonical_name for f in res.gastronomy)
        assert any('كرانتيكا' in f.canonical_name for f in res.gastronomy)
        assert any('باب الواد' in l.canonical_name for l in res.landmarks)

    def test_detect_slang(self) -> None:
        text = 'سلعتكم كابا أصلية وسلعة لوز ماشي خردة'
        res = detect_cultural_references(text)
        assert res.has_cultural_reference is True
        assert any('سلعة كابا' in s.canonical_name for s in res.slang_expressions)
        assert any('خردة' in s.canonical_name for s in res.slang_expressions)

    def test_agent_context_includes_cultural_section(self) -> None:
        text = 'طاح الحك وصاب غطاه، ابعثلي رشتة عاصمية لباب الواد'
        ctx = build_agent_context(text)
        assert 'cultural' in ctx
        assert ctx['cultural']['has_cultural_reference'] is True
        prompt = format_agent_system_prompt(ctx)
        assert 'إشارات ثقافية وشعبية' in prompt

    def test_openai_tool_definitions(self) -> None:
        tools = get_openai_tool_definitions()
        assert len(tools) == 6
        names = [t["function"]["name"] for t in tools]
        assert "parse_algerian_message" in names
        assert "get_wilaya_details" in names
        assert "check_human_escalation" in names
        assert "detect_cultural_references" in names
        assert "respond_to_darja" in names
        assert "moderate_darja_text" in names


class TestAlgeriaGeo69Wilayas:

    def test_all_69_wilayas_loaded(self) -> None:
        wilayas = get_wilayas()
        assert len(wilayas) == 69
        assert wilayas[0]["code"] == 1
        assert wilayas[-1]["code"] == 69
        assert wilayas[-1]["name_ar"] == "الأبيض سيدي الشيخ"
        assert wilayas[-1]["name_fr"] == "El Abiodh Sidi Cheikh"

    def test_wilaya_59_aflou(self) -> None:
        w59 = get_wilaya_by_code(59)
        assert w59 is not None
        assert w59["name_ar"] == "أفلو"
        assert w59["name_fr"] == "Aflou"
        assert w59["era"] == 69
        assert len(w59["communes_sample"]) > 0

    def test_extract_entities_with_new_wilayas(self) -> None:
        text = "حاب توصيل لبلدية بريكة في باتنة أو لأفلو ولاية 59"
        res = extract_entities(text)
        codes = [w.code for w in res.wilayas]
        assert 59 in codes or 60 in codes or 5 in codes


class TestDialogueResponseEngine:

    def test_wach_ya_khoy_arabizi_reply(self) -> None:
        res = respond_to_darja("wach ya khoy")
        assert "cv" in res.reply.lower() or "hamdoulah" in res.reply.lower()
        assert res.script == "arabizi"
        assert res.intent == "WELLBEING_INQUIRY"

    def test_wach_rak_arabic_reply(self) -> None:
        res = respond_to_darja("واش يا خويا واش راك")
        assert res.script == "arabic"
        assert "الحمد لله" in res.reply or "لاباس" in res.reply

    def test_salam_alaykom_greeting(self) -> None:
        res = respond_to_darja("salam alaykom khoya")
        assert "wa alaykom" in res.reply.lower()

    def test_merchant_persona(self) -> None:
        res = respond_to_darja("wach ya khoy", persona="merchant")
        assert "boutique" in res.reply.lower() or "sel3a" in res.reply.lower() or "cv" in res.reply.lower()


class TestProfanityAndModeration:

    def test_detect_profanity_street_insult(self) -> None:
        res = detect_profanity("يا حمار راك غالط")
        assert res.is_profane is True
        assert res.severity in ("low", "medium")
        assert any(m.term == "hmar" for m in res.matches)

    def test_detect_profanity_arabizi_slur(self) -> None:
        res = detect_profanity("nik mok ya weld l9ahba")
        assert res.is_profane is True
        assert res.severity == "high"

    def test_censor_profanity(self) -> None:
        censored = censor_profanity("يا حمار ما تعيطش")
        assert "حمار" not in censored
        assert "***" in censored

    def test_clean_text_is_not_profane(self) -> None:
        res = detect_profanity("سلعة بزاف شابة يعطيكم الصحة نزيد نكوموندي")
        assert res.is_profane is False
        assert res.severity == "none"
        assert is_profane("سلعة بزاف شابة") is False


class TestMemesAndFrancoDarja:

    def test_detect_viral_memes(self) -> None:
        from darja_nlp.cultural import detect_memes
        text = "قالو فاك يا حشيشة و زوخ وطير و وان تو ثري فيفا لالجيري"
        memes = detect_memes(text)
        assert len(memes) >= 2
        phrases = [m.canonical_name for m in memes]
        assert "فاك يا حشيشة" in phrases or "زوخ وطير" in phrases

    def test_detect_franco_darja_loanwords(self) -> None:
        from darja_nlp.cultural import detect_franco_darja
        text = "حاب نكوموندي هاد السبردينة كابا ديسبو وبوانتير 42"
        matches = detect_franco_darja(text)
        assert len(matches) >= 3
        origins = [m["fr_origin"] for m in matches]
        assert "commander" in origins
        assert "disponible" in origins
        assert "cabas" in origins


class TestSentimentV2AndML:

    def test_multiword_lexicon_phrases(self) -> None:
        pos = analyze_sentiment("ما شاء الله خدمة متقونة يعطيكم الصحة")
        assert pos.label == "POSITIVE"
        assert pos.score > 0.5
        neg = analyze_sentiment("الله لا تربحك يا حقار")
        assert neg.label == "NEGATIVE"
        assert neg.score < -0.5

    def test_ml_fallback_on_unseen_arabizi(self) -> None:
        res = analyze_sentiment("Thbliiii bravo souade")
        assert res.label == "POSITIVE"
        assert res.score > 0
        assert res.method in ("ml", "hybrid")
        assert res.probabilities is not None

    def test_ml_and_lexicon_modes(self) -> None:
        ml_only = analyze_sentiment("حتى السعودية قاتلكم ماكمش عرب اتفوووو", mode="ml")
        assert ml_only.label == "NEGATIVE"
        assert ml_only.method == "ml"

        lex_only = analyze_sentiment("ماشي عيان", mode="lexicon")
        assert lex_only.label == "POSITIVE"
        assert lex_only.method == "lexicon"


class TestDialectAndEntitiesV2:

    def test_merged_dialects_json_markers(self) -> None:
        east = detect_dialect("جيبلي السنارية و المصلحة من فضلك")
        assert east.region == "EAST"
        west = detect_dialect("ڨارعلي عند الشرجم في تلمسان")
        assert west.region == "WEST"

    def test_doro_and_melyoun_prices(self) -> None:
        res1 = extract_entities("زيدني 50 دورو ولا مية دورو")
        amounts1 = [p.amount for p in res1.prices]
        assert 250.0 in amounts1
        assert 500.0 in amounts1

        res2 = extract_entities("pc gamer 15 melyoun")
        assert any(p.amount == 150000.0 for p in res2.prices)


class TestDialogueKBRetrieval:

    def test_intent_fallback_no_crash(self) -> None:
        res = respond_to_darja("شحال السومة تاع السبردينة؟", strategy="rules")
        assert res.intent in ("PRICE_INQUIRY", "DELIVERY_INQUIRY")
        assert len(res.reply) > 0

    def test_kb_retrieval_from_real_corpora(self) -> None:
        res = respond_to_darja("Khoya, had sabat chhal mellekher? Ghali chwiya.", strategy="retrieval")
        assert res.source == "kb_retrieval"
        assert len(res.reply) > 10
        assert res.confidence >= 0.7

    def test_vary_and_custom_rules(self) -> None:
        custom = [{
            "intent": "HOURS",
            "patterns_arabizi": ["wa9tech taftah"],
            "patterns_arabic": ["وقتاش تفتحو"],
            "responses_arabizi": ["Naftahou kol youm men 9h l 21h!"],
            "responses_arabic": ["نفتحو كل يوم من 9 صباحاً لـ 9 ليلاً!"],
        }]
        res = respond_to_darja("وقتاش تفتحو خويا؟", custom_rules=custom)
        assert res.intent == "HOURS"
        assert res.source == "custom_rule"


class TestDarjaPipelineUnified:

    def test_analyze_shortcut_and_to_dict(self) -> None:
        from darja_nlp import analyze
        report = analyze("salam kho hab nchri 2 hbat noir l wahran 0661234567")
        assert report.intent is not None and report.intent.intent == "ORDER"
        assert report.dialect is not None and report.dialect.region in ("WEST", "GENERAL_DARJA")
        assert report.entities is not None and any(w.code == 31 for w in report.entities.wilayas)
        d = report.to_dict()
        assert d["raw_text"].startswith("salam")
        assert "sentiment" in d and "entities" in d

    def test_custom_pipeline_configuration(self) -> None:
        from darja_nlp import DarjaPipeline
        nlp = DarjaPipeline(store_name="DzShop", persona="merchant")
        nlp.extend_lexicon(positive={"ممتازجدا": 0.95}, negative={"كارثي": -0.9})
        nlp.add_stopwords(["كلمةزايدة"])
        nlp.add_profanity(["منبوذ"])

        assert nlp.moderate("انت منبوذ").is_profane is True
        cleaned = nlp.clean("المنتج تاع كلمةزايدة ممتازجدا")
        assert "كلمةزايدة" not in cleaned
        batch = nlp.analyze_batch(["wach ya khoy", "سلعة ممتازجدا"])
        assert len(batch) == 2
        assert batch[1].sentiment is not None and batch[1].sentiment.label == "POSITIVE"


class TestDarjaClassifier:

    def test_fit_predict_evaluate_and_json_roundtrip(self) -> None:
        from darja_nlp import DarjaClassifier
        texts = [
            "سلام حاب نكوموندي حبة لوهران", "ابعثلي زوج حبات للجزائر", "راني باغي نشري",
            "شحال السومة تاعها", "بشحال يدير هذا", "شحال بري تاعو",
            "سلعة مكسرة رجعولي دراهمي", "خردة وحشيتوهالي", "ما وصلتش روتور",
        ]
        labels = ["ORDER", "ORDER", "ORDER", "PRICE", "PRICE", "PRICE", "COMPLAINT", "COMPLAINT", "COMPLAINT"]
        clf = DarjaClassifier().fit(texts, labels)
        pred = clf.predict("شحال السومة لوهران")
        assert pred.label in ("PRICE", "ORDER")
        assert abs(sum(pred.probabilities.values()) - 1.0) < 0.02

        metrics = clf.evaluate(texts, labels)
        assert metrics.accuracy >= 0.85

        clf.partial_fit(["حاب نحجز وحدة لسطيف"], ["ORDER"])
        restored = DarjaClassifier.from_dict(clf.to_dict())
        assert restored.predict("حشيتوهالي خردة").label == "COMPLAINT"


class TestDarjaChatSession:

    def test_multi_turn_slot_filling_and_confirmation(self) -> None:
        from darja_nlp import DarjaChat
        chat = DarjaChat(store_name="DzStore", persona="merchant")

        t1 = chat.send("salam kho hab nchri 2 hbat noir XL")
        assert t1.ready_to_confirm is False
        assert "wilaya" in t1.missing_slots and "phone" in t1.missing_slots

        t2 = chat.send("l wahran")
        assert t2.ready_to_confirm is False
        assert t2.missing_slots == ["phone"]
        assert any(w["code"] == 31 for w in t2.extracted_slots["wilayas"])

        t3 = chat.send("0661234567")
        assert t3.ready_to_confirm is True
        assert t3.missing_slots == []
        assert t3.intent == "ORDER_CONFIRMED"
        assert "0661234567" in t3.reply

        chat.reset()
        assert len(chat.history) == 0


class TestHTTPServerIntegration:

    def test_server_endpoints_and_fixes(self) -> None:
        import json
        import threading
        import urllib.request
        from http.server import HTTPServer
        from darja_nlp.server import DarjaRequestHandler

        httpd = HTTPServer(("127.0.0.1", 0), DarjaRequestHandler)
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/wilayas/16", timeout=5) as resp:
                w16 = json.loads(resp.read().decode("utf-8"))
                assert w16["code"] == 16 and w16["name_fr"] == "Alger"

            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/analyze",
                data=json.dumps({"text": "حاب نكوموندي لسطيف بسومة 2000 دج 0661234567"}).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                assert body["intent"]["intent"] == "ORDER"
                assert any(w["code"] == 19 for w in body["entities"]["wilayas"])
        finally:
            httpd.shutdown()
            httpd.server_close()


class TestDarjaAIAgentAndMCP:

    def test_execute_agent_tools_and_offline_agent(self) -> None:
        from darja_nlp import DarjaAIAgent, execute_agent_tool

        parsed = execute_agent_tool("parse_algerian_message", {"text": "hab nchri b 500 doro aflou 0661234567"})
        assert any(w["code"] == 59 for w in parsed["wilayas"])
        assert any(p["amount"] == 2500.0 for p in parsed["prices_dzd"])

        wil = execute_agent_tool("get_wilaya_details", {"code": 59})
        assert wil["name_fr"] == "Aflou"

        analyzed = execute_agent_tool("analyze_darja_message", {"text": "wach ya khoy"})
        assert "reply" in analyzed and "sentiment" in analyzed

        bot = DarjaAIAgent(store_name="DzTest")
        r1 = bot.ask("hab nchri 2 hbat noir l aflou")
        assert r1.provider == "offline"
        assert r1.ready_to_confirm is False
        assert "phone" in r1.missing_slots

        r2 = bot.ask("0661234567")
        assert r2.ready_to_confirm is True
        assert r2.intent == "ORDER_CONFIRMED"
        assert "mcpServers" in DarjaAIAgent.get_mcp_config()

    def test_mcp_jsonrpc_lifecycle(self) -> None:
        import json
        from darja_nlp import handle_mcp_message

        init_resp = handle_mcp_message({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        assert init_resp is not None
        assert init_resp["result"]["serverInfo"]["name"] == "darja-nlp-kit"

        notif_resp = handle_mcp_message({"jsonrpc": "2.0", "method": "notifications/initialized"})
        assert notif_resp is None

        list_resp = handle_mcp_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        assert list_resp is not None
        tool_names = [t["name"] for t in list_resp["result"]["tools"]]
        assert "analyze_darja_message" in tool_names
        assert "parse_algerian_message" in tool_names

        call_resp = handle_mcp_message({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "get_wilaya_details", "arguments": {"code": 16}},
        })
        assert call_resp is not None and call_resp["result"]["isError"] is False
        payload = json.loads(call_resp["result"]["content"][0]["text"])
        assert payload["name_fr"] == "Alger"






