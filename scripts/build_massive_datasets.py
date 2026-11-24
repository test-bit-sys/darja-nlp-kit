"""Generate massive datasets for darja-nlp-kit:
- 69 Wilayas synced with algeria-geo
- Profanity & Content Moderation Lexicon
- French-Darja (Franco-Arabe) Loanwords
- Algerian Memes & Pop-Culture Expressions
- Conversational Dialogue & Greeting Rules
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY_DATA = ROOT / "packages" / "python" / "darja_nlp" / "data"
JS_DATA = ROOT / "packages" / "js" / "data"

# 1. Fetch official 69 wilayas & communes from algeria-geo
print("Fetching 69 wilayas and communes from test-bit-sys/algeria-geo...")
remote_wilayas = json.loads(urllib.request.urlopen('https://raw.githubusercontent.com/test-bit-sys/algeria-geo/main/data/wilayas.json').read().decode('utf-8'))
communes = json.loads(urllib.request.urlopen('https://raw.githubusercontent.com/test-bit-sys/algeria-geo/main/data/communes.json').read().decode('utf-8'))
local_wilayas = json.load(open(PY_DATA / 'wilayas.json', encoding='utf-8'))

communes_by_w = {}
communes_fr_by_w = {}
for c in communes:
    wc = c['wilaya_code']
    communes_by_w.setdefault(wc, []).append(c['name_ar'])
    communes_fr_by_w.setdefault(wc, []).append(c['name_fr'])

synced_wilayas = []
for rw in remote_wilayas:
    code_int = int(rw['code'])
    code_str = f"{code_int:02d}"
    loc = next((w for w in local_wilayas if int(w['code']) == code_int), {})
    
    aliases = list(loc.get('aliases', []))
    for name in [rw['name_ar'], rw['name_fr'], rw.get('name_en')]:
        if name and name.lower() not in [a.lower() for a in aliases]:
            aliases.append(name.lower())
    
    # Specific dialectal / historical aliases
    if rw['name_ar'].startswith('إن '):
        alt = rw['name_ar'].replace('إن ', 'عين ')
        if alt not in aliases: aliases.append(alt)
    if rw['name_ar'].startswith('عين '):
        alt = rw['name_ar'].replace('عين ', 'إن ')
        if alt not in aliases: aliases.append(alt)
    if 'تامنغست' in rw['name_ar'] or 'تمنراست' in rw['name_ar']:
        aliases.extend(['تمنراست', 'تامنغست', 'tamanrasset', 'tamanghasset', 'hoggar', 'الهقار'])
    if rw['name_ar'] == 'أفلو' or rw['name_ar'] == 'آفلو':
        aliases.extend(['آفلو', 'أفلو', 'aflou'])
    if rw['name_ar'] == 'بوسعادة':
        aliases.extend(['bou saada', 'bousaada', 'مدينة السعادة', 'بوابة الصحراء'])
    if rw['name_ar'] == 'بريكة':
        aliases.extend(['barika'])
    if rw['name_ar'] == 'القنطرة':
        aliases.extend(['el kantara', 'kantara'])
    if rw['name_ar'] == 'بئر العاتر':
        aliases.extend(['bir el ater', 'el ater'])
    if rw['name_ar'] == 'العريشة':
        aliases.extend(['el aricha', 'aricha'])
    if rw['name_ar'] == 'قصر الشلالة':
        aliases.extend(['ksar chellala', 'chellala'])
    if rw['name_ar'] == 'عين وسارة':
        aliases.extend(['ain ouessara', 'ouessara'])
    if rw['name_ar'] == 'مسعد':
        aliases.extend(['messaad'])
    if rw['name_ar'] == 'قصر البخاري':
        aliases.extend(['ksar el boukhari', 'el boukhari'])
    if rw['name_ar'] == 'الأبيض سيدي الشيخ':
        aliases.extend(['el abiodh sidi cheikh', 'sidi cheikh', 'el abiodh'])

    # merge existing curated samples with full algeria-geo communes
    existing_c_ar = loc.get('communes_sample', [])
    existing_c_fr = loc.get('communes_fr_sample', [])
    geo_c_ar = communes_by_w.get(code_str, [])
    geo_c_fr = communes_fr_by_w.get(code_str, [])

    all_c_ar = []
    for c in existing_c_ar + geo_c_ar:
        if c and c not in all_c_ar:
            all_c_ar.append(c)

    all_c_fr = []
    for c in existing_c_fr + geo_c_fr:
        if c and c not in all_c_fr:
            all_c_fr.append(c)

    seen = set()
    dedup_aliases = []
    for a in aliases:
        if a and a.lower() not in seen and a.lower() != rw['name_ar'].lower() and a.lower() != rw['name_fr'].lower():
            seen.add(a.lower())
            dedup_aliases.append(a)

    synced_wilayas.append({
        'code': code_int,
        'code_str': code_str,
        'name_ar': rw['name_ar'],
        'name_fr': rw['name_fr'],
        'name_en': rw.get('name_en', rw['name_fr']),
        'phone_code': rw.get('phone_code', ''),
        'era': rw.get('era', 69 if code_int > 58 else (58 if code_int > 48 else 48)),
        'aliases': dedup_aliases,
        'communes_sample': all_c_ar,
        'communes_fr_sample': all_c_fr
    })

print(f"Synced {len(synced_wilayas)} wilayas with algeria-geo.")

# 2. Profanity & Content Moderation Lexicon
profanity_dataset = {
    "version": "1.0.0",
    "description": "Algerian Darja profanity, vulgarities, slurs, and toxic keywords in Arabic script and Arabizi.",
    "severity_levels": ["low", "medium", "high"],
    "categories": ["severe_vulgarity", "insult_street", "religious_curse", "harassment_toxic", "provocation"],
    "terms": [
        # High severity - severe vulgarity / sexual / genital terms
        {"term": "nik", "ar": "نيك", "arabizi": ["nik", "nyk", "neek", "nique"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "nik mok", "ar": "نيك موك", "arabizi": ["nik mok", "nik mouk", "nik omok", "nyk mk"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "zebi", "ar": "زبي", "arabizi": ["zebi", "zbi", "zzebi", "zebb"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "kahba", "ar": "قحبة", "arabizi": ["kahba", "9ahba", "9a7ba", "qahba", "kehba"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "wald kahba", "ar": "ولد القحبة", "arabizi": ["weld l9ahba", "wld 9ahba", "wald kahba", "wld lkahba"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "9lawi", "ar": "قلاوي", "arabizi": ["9lawi", "qlawi", "klawi", "9laywa"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "tiz", "ar": "طيز", "arabizi": ["tiz", "tyz", "teez", "tizi"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "zamel", "ar": "زامل", "arabizi": ["zamel", "zammel", "zwaml", "zamla"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "nayek", "ar": "نايك", "arabizi": ["nayek", "nayeq", "mnayek", "mneiyek"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "mnayek", "ar": "منيك", "arabizi": ["mnayek", "mneyek", "mnayak"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "hchewa", "ar": "حشوة", "arabizi": ["hchewa", "7chwa", "hchwa", "hchewhalkoum"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "mhashi", "ar": "محشي", "arabizi": ["mhashi", "m7achi", "m7achya"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "attay", "ar": "عطاي", "arabizi": ["attay", "3atay", "3attay", "3ataya"], "category": "severe_vulgarity", "severity": "high"},
        {"term": "9ahbat", "ar": "قحاب", "arabizi": ["9ahbat", "9hab", "khab"], "category": "severe_vulgarity", "severity": "high"},
        
        # Religious curses (High severity due to cultural offensiveness)
        {"term": "din rabek", "ar": "دين ربك", "arabizi": ["din rabek", "din rbek", "rabek", "rabk"], "category": "religious_curse", "severity": "high"},
        {"term": "din mok", "ar": "دين موك", "arabizi": ["din mok", "din mouk", "din mmak"], "category": "religious_curse", "severity": "high"},
        {"term": "yen3al", "ar": "ينعل", "arabizi": ["yen3al", "yenal", "yn3al"], "category": "religious_curse", "severity": "high"},
        {"term": "ne3lat", "ar": "لعنة", "arabizi": ["ne3lat", "naalat"], "category": "religious_curse", "severity": "medium"},

        # Medium severity - Street insults
        {"term": "tahhan", "ar": "طحان", "arabizi": ["tahhan", "ta7an", "ta77an", "t7an", "thhan"], "category": "insult_street", "severity": "medium"},
        {"term": "tahana", "ar": "طحانة", "arabizi": ["tahana", "ta7ana", "thana"], "category": "insult_street", "severity": "medium"},
        {"term": "chmata", "ar": "شماطة", "arabizi": ["chmata", "chmat", "chmitta"], "category": "insult_street", "severity": "medium"},
        {"term": "hmar", "ar": "حمار", "arabizi": ["hmar", "7mar", "7maar", "hmar kbir"], "category": "insult_street", "severity": "medium"},
        {"term": "kelb", "ar": "كلب", "arabizi": ["kelb", "kalb", "kleb"], "category": "insult_street", "severity": "medium"},
        {"term": "khra", "ar": "خرا", "arabizi": ["khra", "5ra", "khera", "khrayen"], "category": "insult_street", "severity": "medium"},
        {"term": "khnara", "ar": "خنارة", "arabizi": ["khnara", "5nara", "khenzira"], "category": "insult_street", "severity": "medium"},
        {"term": "rakhis", "ar": "رخيس", "arabizi": ["rakhis", "rkhes", "rkhiss", "rkhes menk ma choftech"], "category": "insult_street", "severity": "medium"},
        {"term": "bahloul", "ar": "بهلول", "arabizi": ["bahloul", "behloul", "bhayeel"], "category": "insult_street", "severity": "low"},
        {"term": "habes", "ar": "حابس", "arabizi": ["habes", "7abes", "habes f rassek"], "category": "insult_street", "severity": "low"},
        {"term": "jahel", "ar": "جاهل", "arabizi": ["jahel", "johl"], "category": "insult_street", "severity": "low"},
        {"term": "mweffakh", "ar": "موسخ", "arabizi": ["mweffakh", "mwessakh", "mwasakh"], "category": "insult_street", "severity": "low"},
        {"term": "hayawan", "ar": "حيوان", "arabizi": ["hayawan", "7ayawan"], "category": "insult_street", "severity": "low"},
        {"term": "sere9", "ar": "سراق", "arabizi": ["sere9", "sarra9", "saraq", "sere9 lkhobz"], "category": "harassment_toxic", "severity": "medium"},
        {"term": "kedab", "ar": "كذاب", "arabizi": ["kedab", "keddab", "kaddab"], "category": "harassment_toxic", "severity": "low"},
        {"term": "hram", "ar": "حرامي", "arabizi": ["hrami", "weld lhram", "wld l7ram"], "category": "insult_street", "severity": "medium"},
        {"term": "maskhout", "ar": "مسخوط", "arabizi": ["maskhout", "maskhot"], "category": "insult_street", "severity": "low"},
        {"term": "fassed", "ar": "فاسد", "arabizi": ["fassed", "fassed"], "category": "insult_street", "severity": "low"}
    ]
}

# 3. Franco-Arabe (French-Darja) Loanwords Dataset
franco_darja_dataset = {
    "version": "1.0.0",
    "description": "Massive lexicon of French loanwords, hybrid verbs, and expressions heavily used in Algerian Darja.",
    "count": 0,
    "words": [
        # Hybrid Verbs (Darja conjugated forms of French verbs)
        {"darja_ar": "نكوموندي", "arabizi": "ncommandi", "fr_origin": "commander", "category": "verbs_commerce", "meaning_ar": "أطلب أو أشتري عبر الطلبية", "example": "حاب نكوموندي هاد السبردينة"},
        {"darja_ar": "نليفري", "arabizi": "nlivri", "fr_origin": "livrer", "category": "verbs_commerce", "meaning_ar": "أوصل البضاعة", "example": "نليفريولك غدوا للدار"},
        {"darja_ar": "نكونفيرمي", "arabizi": "nconfirmi", "fr_origin": "confirmer", "category": "verbs_commerce", "meaning_ar": "أؤكد الطلب", "example": "عيطلي باش نكونفيرمي الكوموند"},
        {"darja_ar": "نانولي", "arabizi": "nannuler", "fr_origin": "annuler", "category": "verbs_commerce", "meaning_ar": "ألغي الطلب", "example": "سمحلي راني حاب نانولي الكوموند"},
        {"darja_ar": "نبلوكي", "arabizi": "nbloqui", "fr_origin": "bloquer", "category": "verbs_tech", "meaning_ar": "أحظر أو أعطل", "example": "النميرو تبلوكا"},
        {"darja_ar": "نريباري", "arabizi": "nrepari", "fr_origin": "réparer", "category": "verbs_service", "meaning_ar": "أصلح الشيء المعطل", "example": "يقدر يريباري البيسي تاعي؟"},
        {"darja_ar": "نشونجي", "arabizi": "nchangi", "fr_origin": "changer", "category": "verbs_service", "meaning_ar": "أغير أو أستبدل", "example": "حاب نشونجي البوانتير"},
        {"darja_ar": "نفاكتيري", "arabizi": "nfacturi", "fr_origin": "facturer", "category": "verbs_commerce", "meaning_ar": "أصدر فاتورة", "example": "تقدرو تفاكتيريولي السلعة؟"},
        {"darja_ar": "نخلص / نبايي", "arabizi": "npayi", "fr_origin": "payer", "category": "verbs_commerce", "meaning_ar": "أدفع الثمن", "example": "نبايي كاش ولا بالبطاقة الذهبية؟"},
        {"darja_ar": "نبارطاجي", "arabizi": "npartagi", "fr_origin": "partager", "category": "verbs_tech", "meaning_ar": "أشارك المنشور أو الرابط", "example": "بارطاجي معايا لاباج"},
        {"darja_ar": "نكونيكتي", "arabizi": "nconnecti", "fr_origin": "connecter", "category": "verbs_tech", "meaning_ar": "أتصل بالإنترنت", "example": "ما قدرتش نكونيكتي اليوم"},
        {"darja_ar": "نشيكولي", "arabizi": "nchekoli", "fr_origin": "checker", "category": "verbs_tech", "meaning_ar": "أتحقق من الأمر", "example": "شيكيلي الكولي وين وصل"},

        # E-Commerce, Logistics & Products
        {"darja_ar": "ديسبو", "arabizi": "dispo", "fr_origin": "disponible", "category": "commerce", "meaning_ar": "متوفر في المخزون", "example": "راهي ديسبو كابا ولا مقطوعة؟"},
        {"darja_ar": "مريڤل", "arabizi": "mrigel", "fr_origin": "réglé", "category": "daily_slang", "meaning_ar": "مضبوط، جاهز، تمام", "example": "كلش راه مريڤل صحيت"},
        {"darja_ar": "كابا", "arabizi": "caba", "fr_origin": "cabas", "category": "commerce", "meaning_ar": "بضاعة مستوردة أصلية عبر الحقائب", "example": "سلعة كابا دوريجين من فرنسا"},
        {"darja_ar": "صولد", "arabizi": "solde", "fr_origin": "solde", "category": "commerce", "meaning_ar": "تخفيضات الأسعار", "example": "دايرين صولد كبير هاد السيمانة"},
        {"darja_ar": "رميز", "arabizi": "remise", "fr_origin": "remise", "category": "commerce", "meaning_ar": "خصم في الثمن", "example": "كاش رميز لولاد البلاد؟"},
        {"darja_ar": "بوانتير", "arabizi": "pointure", "fr_origin": "pointure", "category": "clothing", "meaning_ar": "مقاس الحذاء", "example": "كاين بوانتير 42 في هاد الموديل؟"},
        {"darja_ar": "طاي", "arabizi": "taille", "fr_origin": "taille", "category": "clothing", "meaning_ar": "مقاس الملابس", "example": "طاي L جاتني سوا سوا"},
        {"darja_ar": "دوريجين", "arabizi": "dorigine", "fr_origin": "d'origine", "category": "commerce", "meaning_ar": "أصلي غير مقلد", "example": "حاجة دوريجين مع الضمان"},
        {"darja_ar": "إيميتاسيون", "arabizi": "imitation", "fr_origin": "imitation", "category": "commerce", "meaning_ar": "نسخة مقلدة", "example": "هادي دوريجين ولا إيميتاسيون برومي شوا؟"},
        {"darja_ar": "كولي", "arabizi": "colis", "fr_origin": "colis", "category": "logistics", "meaning_ar": "طرد بريدي أو شحنة", "example": "الكولي وصل للبياجي"},
        {"darja_ar": "ليفريزون", "arabizi": "livraison", "fr_origin": "livraison", "category": "logistics", "meaning_ar": "خدمة التوصيل", "example": "شحال ليفريزون لوهران؟"},
        {"darja_ar": "ستوب ديسك", "arabizi": "stop desk", "fr_origin": "stop desk", "category": "logistics", "meaning_ar": "استلام الطرد من مقر وكالة الشحن", "example": "نفضل ستوب ديسك في ياليدين"},
        {"darja_ar": "دوميسيل", "arabizi": "domicile", "fr_origin": "à domicile", "category": "logistics", "meaning_ar": "توصيل إلى باب المنزل", "example": "توصيل دوميسيل لعين الدفلى"},
        {"darja_ar": "فاكتير", "arabizi": "facture", "fr_origin": "facture", "category": "commerce", "meaning_ar": "فاتورة شراء رسمية", "example": "تبعثولي الفاكتير مع الكولي؟"},
        {"darja_ar": "قارانتي", "arabizi": "garantie", "fr_origin": "garantie", "category": "commerce", "meaning_ar": "ضمان الجودة والصيانة", "example": "كاين قارانتي عام كامل"},
        {"darja_ar": "روطار", "arabizi": "retard", "fr_origin": "retard", "category": "daily_slang", "meaning_ar": "تأخير في الموعد", "example": "الليفرور دار روطار اليوم"},
        {"darja_ar": "أونبان", "arabizi": "en panne", "fr_origin": "en panne", "category": "technical", "meaning_ar": "معطل أو به خلل", "example": "التلفون راه أونبان"},
        {"darja_ar": "ديفو", "arabizi": "defaut", "fr_origin": "défaut", "category": "commerce", "meaning_ar": "عيب أو نقص صناعي", "example": "إذا فيه ديفو تقدر ترجعو"},
        {"darja_ar": "رومبورسمون", "arabizi": "remboursement", "fr_origin": "remboursement", "category": "commerce", "meaning_ar": "استرجاع الأموال المدفوعة", "example": "حاب رومبورسمون دراهمي"},
        {"darja_ar": "كليون", "arabizi": "client", "fr_origin": "client", "category": "commerce", "meaning_ar": "زبون", "example": "سيرفيس كليون ممتاز"},
        {"darja_ar": "ماغازان", "arabizi": "magasin", "fr_origin": "magasin", "category": "commerce", "meaning_ar": "محل تجاري أو متجر", "example": "وين جاي الماغازان تاعكم؟"},
        {"darja_ar": "بوتيك", "arabizi": "boutique", "fr_origin": "boutique", "category": "commerce", "meaning_ar": "دكان أو متجر ألبسة", "example": "البوتيك في البويرة"},
        {"darja_ar": "بري فيكس", "arabizi": "prix fixe", "fr_origin": "prix fixe", "category": "commerce", "meaning_ar": "سعر غير قابل للتفاوض", "example": "السومة بري فيكس خويا"},
        {"darja_ar": "أوكازيون", "arabizi": "occasion", "fr_origin": "occasion", "category": "commerce", "meaning_ar": "مستعمل أو فرصة جيدة", "example": "بيسي أوكازيون نظيف"},
        {"darja_ar": "نوف", "arabizi": "neuf", "fr_origin": "neuf", "category": "commerce", "meaning_ar": "جديد غير مستعمل بالكرتونة", "example": "سلعة نوف زيرو كليمتر"},
        {"darja_ar": "فالابل", "arabizi": "valable", "fr_origin": "valable", "category": "commerce", "meaning_ar": "صالح وساري المفعول", "example": "البرومو مازالت فالابل"},

        # Daily Expressions & Discourse Markers
        {"darja_ar": "ديجا", "arabizi": "deja", "fr_origin": "déjà", "category": "discourse", "meaning_ar": "سابقاً، بالفعل", "example": "ديجا وصيتك عليها الخطرة لي فاتت"},
        {"darja_ar": "نورمال", "arabizi": "normal", "fr_origin": "normal", "category": "discourse", "meaning_ar": "عادي، بدون مشكلة", "example": "نورمال خويا ما كاين حتى حرج"},
        {"darja_ar": "ديركت", "arabizi": "direct", "fr_origin": "direct", "category": "discourse", "meaning_ar": "مباشرة فوراً", "example": "توصلك ديركت لباب دارك"},
        {"darja_ar": "بارفي", "arabizi": "parfait", "fr_origin": "parfait", "category": "discourse", "meaning_ar": "ممتاز ومثالي", "example": "هكدا بارفي خويا صحيت"},
        {"darja_ar": "إكزاكتومون", "arabizi": "exactement", "fr_origin": "exactement", "category": "discourse", "meaning_ar": "بالضبط كما هو", "example": "إكزاكتومون هاديك هي السلعة"},
        {"darja_ar": "بيان سير", "arabizi": "bien sur", "fr_origin": "bien sûr", "category": "discourse", "meaning_ar": "بالتأكيد ودون شك", "example": "بيان سير كاين التوصيل"},
        {"darja_ar": "ميرسي", "arabizi": "merci", "fr_origin": "merci", "category": "courtesy", "meaning_ar": "شكراً جزيلاً", "example": "ميرسي بزاف ربي يعاونكم"},
        {"darja_ar": "باردون", "arabizi": "pardon", "fr_origin": "pardon", "category": "courtesy", "meaning_ar": "عذراً أو أعتذر", "example": "باردون غلطت في النميرو"},
        {"darja_ar": "سيلفوبلي", "arabizi": "svp", "fr_origin": "s'il vous plaît", "category": "courtesy", "meaning_ar": "من فضلك أو لو سمحت", "example": "السومة سيلفوبلي"},
        {"darja_ar": "بون كوراج", "arabizi": "bon courage", "fr_origin": "bon courage", "category": "courtesy", "meaning_ar": "بالتوفيق والصبر والهمة", "example": "بون كوراج في الخدمة خويا"},
        {"darja_ar": "صونطي", "arabizi": "sante", "fr_origin": "santé", "category": "courtesy", "meaning_ar": "بالصحة والعافية", "example": "بون صونطي للجميع"},
        {"darja_ar": "رونديفو", "arabizi": "rendez-vous", "fr_origin": "rendez-vous", "category": "daily_slang", "meaning_ar": "موعد متفق عليه", "example": "درنا رونديفو مع الـ 14:00"},
        {"darja_ar": "سيرفيس", "arabizi": "service", "fr_origin": "service", "category": "service", "meaning_ar": "خدمة أو مساعدة", "example": "كاش سيرفيس نقدرو نعاونوك بيه؟"},
        {"darja_ar": "كابابل", "arabizi": "capable", "fr_origin": "capable", "category": "daily_slang", "meaning_ar": "قادر أو محتمل", "example": "كابابل توصلك اليوم العشية"}
    ]
}
franco_darja_dataset["count"] = len(franco_darja_dataset["words"])

# 4. Algerian Memes & Pop-Culture Expressions Dataset
memes_dataset = {
    "version": "1.0.0",
    "description": "Algerian memes, viral series quotes (Achour 10, Dakious & Makious, Bouzid Days), football anthems, and iconic street culture phrases.",
    "count": 0,
    "memes": [
        # Iconic TV Series Quotes
        {
            "id": "meme_001",
            "phrase": "فاك يا حشيشة",
            "arabizi": "fak ya hchicha",
            "origin": "دقيوس ومقيوس (Dakious & Makious)",
            "category": "tv_comedy",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "تعبير كوميدي شهير يُقال عند الصدمة أو الاستغراب أو حدوث أمر غير متوقع.",
            "tags": ["dakious", "comedy", "viral_quote"]
        },
        {
            "id": "meme_002",
            "phrase": "ما تخلطش شعبان مع رمضان",
            "arabizi": "ma tkheletch cha3ban m3a ramdan",
            "origin": "دقيوس ومقيوس والمثل الشعبي الجزائري",
            "category": "tv_comedy",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "دعوة لعدم خلط المواضيع المنفصلة ببعضها البعض.",
            "tags": ["proverb", "dakious", "logic"]
        },
        {
            "id": "meme_003",
            "phrase": "الراس فالكاس",
            "arabizi": "rass fel kess",
            "origin": "دقيوس ومقيوس",
            "category": "tv_comedy",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "التركيز التام على شرب الشاي أو الاسترخاء والهروب من وجع الرأس.",
            "tags": ["tea", "focus", "dakious"]
        },
        {
            "id": "meme_004",
            "phrase": "هبط يدك يا بنادم",
            "arabizi": "hbet ydek ya bnadem",
            "origin": "ترند شوارع ومواقع التواصل بالجزائر",
            "category": "street_viral",
            "sentiment": "NEGATIVE",
            "intent": "CASUAL_CHAT",
            "meaning": "عبارة شهيرة انتشرت كفيديو ترند للمطالبة بالهدوء وعدم الإشارة باليد أثناء النقاش.",
            "tags": ["street_slang", "viral", "trend"]
        },
        {
            "id": "meme_005",
            "phrase": "يا راجل كبر عقلك",
            "arabizi": "ya rajel kber 3a9lek",
            "origin": "عاشور العاشر (سلطان العاشوريين)",
            "category": "tv_comedy",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "تعبير يُقال للشخص عندما يتصرف بسذاجة أو طيش لتذكيره بالحكمة والتعقل.",
            "tags": ["achour10", "wisdom", "comedy"]
        },
        {
            "id": "meme_006",
            "phrase": "شكون نتا",
            "arabizi": "chkoune nta",
            "origin": "عاشور العاشر / الثقافة الشعبية",
            "category": "tv_comedy",
            "sentiment": "NEGATIVE",
            "intent": "CASUAL_CHAT",
            "meaning": "سؤال استنكاري يعبر عن التجاهل أو التقليل من شأن الطرف المقابل بأسلوب هزلي.",
            "tags": ["achour10", "pride", "comedy"]
        },
        {
            "id": "meme_007",
            "phrase": "البرهان ولا البهتان",
            "arabizi": "el borhan wela el bohtan",
            "origin": "عاشور العاشر (شخصية الوزير قنديل)",
            "category": "tv_comedy",
            "sentiment": "NEUTRAL",
            "intent": "INQUIRY",
            "meaning": "المطالبة بالدليل القاطع وإلا اعتُبر الأمر افتراءً واختلاقاً.",
            "tags": ["achour10", "proof", "court"]
        },
        {
            "id": "meme_008",
            "phrase": "متقوليش نتا تاني",
            "arabizi": "matgoulich nta tani",
            "origin": "ترند جزائري ومسلسلات فكاهية",
            "category": "social_trend",
            "sentiment": "NEGATIVE",
            "intent": "CASUAL_CHAT",
            "meaning": "التعبير عن خيبة الأمل من تكرار نفس الطلب أو خذلان من شخص لم يكن متوقعاً منه.",
            "tags": ["disappointment", "viral", "trend"]
        },
        {
            "id": "meme_009",
            "phrase": "زوخ وطير",
            "arabizi": "zoukh w tir",
            "origin": "الأمثال الشعبية والمسلسلات الكوميدية",
            "category": "street_culture",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "السخرية من شخص يبالغ في التفاخر بممتلكاته أو إنجازاته الوهمية.",
            "tags": ["pride", "proverb", "street"]
        },
        {
            "id": "meme_010",
            "phrase": "في خاطر ولاد بلادي",
            "arabizi": "fi khater wlad bladi",
            "origin": "الإهداءات الشعبية والراي الجزائري",
            "category": "culture_folk",
            "sentiment": "POSITIVE",
            "intent": "GREETING",
            "meaning": "إهداء حار مخصص لكل أبناء وبنات الجزائر في الداخل والخارج.",
            "tags": ["patriotism", "folk", "dedication"]
        },
        {
            "id": "meme_011",
            "phrase": "وان تو ثري فيفا لالجيري",
            "arabizi": "1 2 3 viva l'algerie",
            "origin": "الهتاف التاريخي للمنتخب الجزائري والشعب",
            "category": "national_sport",
            "sentiment": "POSITIVE",
            "intent": "CELEBRATION",
            "meaning": "الشعار الرياضي والوطني الأشهر الذي يعبر عن الفخر والوحدة الجزائرية.",
            "tags": ["football", "patriotism", "anthem"]
        },
        {
            "id": "meme_012",
            "phrase": "هادي هي لالجيري",
            "arabizi": "hadi hiya l'algerie",
            "origin": "ثقافة الشارع ومواقع التواصل",
            "category": "street_culture",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "تعبير عن تقبل الواقع الجزائري بكل مفارقاته وجماله بابتسامة وهدوء.",
            "tags": ["identity", "street_philosophy"]
        },
        {
            "id": "meme_013",
            "phrase": "زوالي وفحل",
            "arabizi": "zwali w fhel",
            "origin": "الأغنية والوعي الجمعي الجزائري",
            "category": "culture_folk",
            "sentiment": "POSITIVE",
            "intent": "PRIDE",
            "meaning": "الاعتزاز بنبل الأخلاق والشرف والمروءة رغم بساطة الحال والمستوى المادي.",
            "tags": ["pride", "dignity", "values"]
        },
        {
            "id": "meme_014",
            "phrase": "خليه يريح",
            "arabizi": "khelih yriyeh",
            "origin": "ترند السوشيال ميديا وكرة القدم",
            "category": "social_trend",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "دعوة لتجاهل شخص معين أو تركه يستريح وعدم إعطائه اهتماماً أكبر من حجمه.",
            "tags": ["meme", "relax", "trend"]
        },
        {
            "id": "meme_015",
            "phrase": "طير انت وياه",
            "arabizi": "tir nta wiyaho",
            "origin": "كوميديا الشارع الجزائري",
            "category": "street_comedy",
            "sentiment": "NEGATIVE",
            "intent": "CASUAL_CHAT",
            "meaning": "صيغة هزلية لرفض كلام شخصين وطردهم من الحوار.",
            "tags": ["street_slang", "dismissal"]
        },
        {
            "id": "meme_016",
            "phrase": "ما كاين والو",
            "arabizi": "ma kayen walou",
            "origin": "الدارجة الجزائرية اليومية",
            "category": "daily_slang",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "تطمين الطرف الآخر بأنه لا يوجد أي مشكل أو خطر، أو وصف حالة الفراغ.",
            "tags": ["daily_life", "peace"]
        },
        {
            "id": "meme_017",
            "phrase": "راك فالموزمبيق",
            "arabizi": "rak fel mozambique",
            "origin": "الميمات والترندات الهزلية",
            "category": "social_trend",
            "sentiment": "NEGATIVE",
            "intent": "CASUAL_CHAT",
            "meaning": "سخرية عند وقوع أمر سريالي أو مخالف تماماً للمنطق أو المعايير.",
            "tags": ["meme", "sarcasm", "viral"]
        },
        {
            "id": "meme_018",
            "phrase": "بلاد ميكي",
            "arabizi": "bled miki",
            "origin": "الثقافة الساخرة",
            "category": "social_criticism",
            "sentiment": "NEGATIVE",
            "intent": "COMPLAINT",
            "meaning": "انتقاد الفوضى وسوء التنظيم في بعض الإدارات أو المرافق.",
            "tags": ["satire", "criticism"]
        },
        {
            "id": "meme_019",
            "phrase": "عيش تسمع",
            "arabizi": "3ich tesma3",
            "origin": "المثل الشعبي الجزائري",
            "category": "proverbs",
            "sentiment": "NEUTRAL",
            "intent": "SURPRISE",
            "meaning": "الدهشة والتعجب من غرابة الأخبار والمواقف المتجددة.",
            "tags": ["proverb", "amazement"]
        },
        {
            "id": "meme_020",
            "phrase": "عفسة شابة",
            "arabizi": "3afsa chaba",
            "origin": "الدارجة الشبابية",
            "category": "street_slang",
            "sentiment": "POSITIVE",
            "intent": "APPRECIATION",
            "meaning": "وصف فكرة ذكية، تقنية جديدة، أو منتج مميز وأنيق.",
            "tags": ["cool", "innovation", "youth"]
        },
        {
            "id": "meme_021",
            "phrase": "طايح خشين",
            "arabizi": "tayeh khchine",
            "origin": "الدارجة الشبابية",
            "category": "street_slang",
            "sentiment": "NEGATIVE",
            "intent": "CRITICISM",
            "meaning": "انتقاد شخص يتصرف بتعالي وقوة مبالغ فيها.",
            "tags": ["slang", "attitude"]
        },
        {
            "id": "meme_022",
            "phrase": "سلكها يا سليك",
            "arabizi": "salekha ya slik",
            "origin": "ثقافة الميمات اليومية",
            "category": "social_trend",
            "sentiment": "NEUTRAL",
            "intent": "HELP_INQUIRY",
            "meaning": "طلب إيجاد حل ذكي وسريع للخروج من ورطة أو موقف محرج.",
            "tags": ["rescue", "humor"]
        },
        {
            "id": "meme_023",
            "phrase": "الله غالب يا حليش",
            "arabizi": "allah ghaleb ya halliche",
            "origin": "كرة القدم الوطنية (ملحمة كأس أمم إفريقيا 2010)",
            "category": "national_sport",
            "sentiment": "NEUTRAL",
            "intent": "RESIGNATION",
            "meaning": "التسليم بالقدر بعد بذل كل المجهود والشجاعة الممكنة.",
            "tags": ["halliche", "football", "sacrifice"]
        },
        {
            "id": "meme_024",
            "phrase": "جابوها الرجالة",
            "arabizi": "djabouha rdjala",
            "origin": "الاحتفالات الوطنية والرياضية",
            "category": "national_sport",
            "sentiment": "POSITIVE",
            "intent": "CELEBRATION",
            "meaning": "الافتخار بتحقيق الفوز والانتصار بفضل كفاح الرجال الأوفياء.",
            "tags": ["victory", "men", "glory"]
        },
        {
            "id": "meme_025",
            "phrase": "دير الخير وانساه",
            "arabizi": "dir lkhir wensah",
            "origin": "حكمة جزائرية أصيلة",
            "category": "proverbs",
            "sentiment": "POSITIVE",
            "intent": "WISDOM",
            "meaning": "دعوة لعمل الخير والإحسان دون انتظار المقابل أو التباهي.",
            "tags": ["morals", "charity", "proverb"]
        },
        {
            "id": "meme_026",
            "phrase": "حاجة فور",
            "arabizi": "haja fort",
            "origin": "الدارجة المعاصرة",
            "category": "product_review",
            "sentiment": "POSITIVE",
            "intent": "PRAISE",
            "meaning": "وصف منتج أو خدمة بجودة استثنائية تفوق التوقعات.",
            "tags": ["top_quality", "slang"]
        },
        {
            "id": "meme_027",
            "phrase": "كاسكيطة وشانسون",
            "arabizi": "casquette w chanson",
            "origin": "اللوك الشعبي العاصمي",
            "category": "street_culture",
            "sentiment": "NEUTRAL",
            "intent": "CASUAL_CHAT",
            "meaning": "أسلوب الحياة الشعبي البسيط والأنيق للشباب الجزائري.",
            "tags": ["lifestyle", "culture"]
        },
        {
            "id": "meme_028",
            "phrase": "حوتة ومقلية",
            "arabizi": "houta w ma9liya",
            "origin": "المثل الساخر في الدارجة",
            "category": "proverbs",
            "sentiment": "NEGATIVE",
            "intent": "SARCASM",
            "meaning": "سخرية من شخص يطلب الشيء جاهزاً ومطبوخاً دون أي جهد.",
            "tags": ["laziness", "humor"]
        },
        {
            "id": "meme_029",
            "phrase": "طايح في بير",
            "arabizi": "tayeh fi bir",
            "origin": "الدارجة اليومية",
            "category": "daily_slang",
            "sentiment": "NEUTRAL",
            "intent": "INQUIRY",
            "meaning": "تُقال عند طول غياب الشخص أو انقطاع أخباره فجأة وكأنه سقط في بئر.",
            "tags": ["absence", "slang"]
        },
        {
            "id": "meme_030",
            "phrase": "ما طلقو والو",
            "arabizi": "ma tal9ou walou",
            "origin": "الترندات الاجتماعية",
            "category": "social_trend",
            "sentiment": "NEUTRAL",
            "intent": "SURPRISE",
            "meaning": "التعجب من قدرة الجزائريين على تحويل أي موقف جاد إلى نكتة وميم متداول.",
            "tags": ["humor", "memes"]
        }
    ]
}
memes_dataset["count"] = len(memes_dataset["memes"])

# 5. Conversational Dialogue & Greeting Rules Dataset
# Specifically supporting user's prompt: 'wach ya khoy' -> 'we cv hamdoulah w nta kho'
dialogue_rules = {
    "version": "1.0.0",
    "description": "Algerian Darja conversational intents, matching patterns, and authentic colloquial responses in both Arabizi and Arabic script.",
    "rules": [
        {
            "intent": "WELLBEING_INQUIRY",
            "patterns_arabizi": [
                "wach ya khoy", "wach ya kho", "wach rak", "wachrak", "wach rak kho",
                "kifech rak", "kirak", "kirak ghaya", "ca va kho", "cv kho",
                "labas kho", "we cv", "wach l'ahwal", "kifech ahwalek", "wach rakoum"
            ],
            "patterns_arabic": [
                "واش يا خويا", "واش راك", "واش راك خويا", "واشراك", "كيفاش راك",
                "كيراك", "كيراك غايا", "لاباس خويا", "واش الأحوال", "كيفاش الأحوال",
                "واش راكم", "لاباس عليك", "كلش مليح", "واش راك خو"
            ],
            "responses_arabizi": [
                "We cv hamdoulah w nta kho? Koulchi mlih?",
                "Labas hamdoullah rabi yahfdhek, w nta kifech rak?",
                "Hamdoullah kolchi mrigel, kash ma khasek kho?",
                "Ghaya rabi ykhellik w nta kirak labas?"
            ],
            "responses_arabic": [
                "لاباس الحمد لله خويا العزيز، وأنت واش راك؟ كلش مريڤل؟",
                "الحمد لله ربي يحفظك خونا، وأنت كاش جديد من جيهتك؟",
                "كلش مريڤل وعلى خير ربي يبارك فيك، في الخدمة خويا واش يخصك؟",
                "غايا ربي يسلمك ويحفظك، واش حوالكم نتومة؟"
            ]
        },
        {
            "intent": "ISLAMIC_GREETING",
            "patterns_arabizi": [
                "salam", "salam alaykom", "slm", "salam khoya", "assalam",
                "salamo alaykom", "salam 3likom", "slm kho"
            ],
            "patterns_arabic": [
                "سلام", "سلام عليكم", "السلام عليكم", "سلام خويا", "أهلا خويا", "السلام عليكم ورحمة الله"
            ],
            "responses_arabizi": [
                "Wa alaykom salam w rahma kho, marhba bik!",
                "Wa alaykom salam kho l3ziz, marhba bik kash ma khasek?",
                "3likom salam khouna, nharek mabrouk w koulchi mrigel!"
            ],
            "responses_arabic": [
                "وعليكم السلام ورحمة الله وبركاته، مرحباً بيك خونا نورتنا!",
                "وعليكم السلام خويا العزيز، مرحباً بيك في أي وقت كاش ما نسحقو نخدموك؟",
                "وعليكم السلام ورحمة الله، نهارك مبروك ومرحباً بيك!"
            ]
        },
        {
            "intent": "CASUAL_GREETING",
            "patterns_arabizi": [
                "saha kho", "saha khouya", "saha", "sahite", "sahiti", "sahitou"
            ],
            "patterns_arabic": [
                "صحا خويا", "صحا خونا", "صحا", "صحيت", "صحيت خويا", "صحيتو"
            ],
            "responses_arabizi": [
                "Saha lik rabi yahfdhek kho!",
                "Yselmek kho l3ziz, bla mziya!",
                "Saha kho, marhba bik f kol wa9t!"
            ],
            "responses_arabic": [
                "الله يسلمك ويحفظك خويا العزيز!",
                "يسلمك خونا الغالي، مرحباً بيك في كل وقت!",
                "صحا ليك وربي يعطيك الصحة والعافية!"
            ]
        },
        {
            "intent": "MORNING_GREETING",
            "patterns_arabizi": [
                "sbah lkhir", "sbah ennour", "bonjour", "sbah el kheir"
            ],
            "patterns_arabic": [
                "صباح الخير", "صباح النور", "صباح الفل", "صباح الورد"
            ],
            "responses_arabizi": [
                "Sbah el nour w lkhir kho! Nharek mabrouk!",
                "Sbah el khir w l3afya, marhba bik!"
            ],
            "responses_arabic": [
                "صباح الخير والسرور خويا الغالي، نهارك مبروك إن شاء الله!",
                "صباح النور والبركة، مرحباً بيك وفي الخدمة دائماً!"
            ]
        },
        {
            "intent": "EVENING_GREETING",
            "patterns_arabizi": [
                "messa lkhir", "msa lkhir", "bonsoir", "messa ennour"
            ],
            "patterns_arabic": [
                "مساء الخير", "مساء النور", "مسا الخير", "مساء الورد"
            ],
            "responses_arabizi": [
                "Messa lkhir w l3afya kho! Marhba bik!",
                "Bonsoir kho, koulchi mrigel nchallah?"
            ],
            "responses_arabic": [
                "مساء الخير والعافية خويا، مرحباً بيك ونورتنا!",
                "مساء النور والسرور، كاش ما نسحقو نخدموك ليوما؟"
            ]
        },
        {
            "intent": "RAMADAN_GREETING",
            "patterns_arabizi": [
                "saha ftourkoum", "saha ftourkom", "saha remdankoum", "ramadan kareem", "saha shourkoum"
            ],
            "patterns_arabic": [
                "صحة فطوركم", "صحة رمضانكم", "رمضان كريم", "صحة سحوركم", "صيام مقبول"
            ],
            "responses_arabizi": [
                "Saha ftourkoum w rabi yeta9abal menna w menkoum!",
                "Saha remdankoum w koul 3am w ntouma b alf khir!",
                "Saha shourkoum w rabi ybarek fikoum!"
            ],
            "responses_arabic": [
                "صحة فطوركم وربي يتقبل منا ومنكم الصيام والقيام وصالح الأعمال!",
                "صحة رمضانكم وكل عام وأنتم وأحبابكم بألف خير وسعادة!",
                "صحة سحوركم وذنب مغفور إن شاء الله!"
            ]
        },
        {
            "intent": "EID_GREETING",
            "patterns_arabizi": [
                "saha 3idek", "saha 3idkoum", "aid mubarak", "saha l3id"
            ],
            "patterns_arabic": [
                "صحة عيدك", "صحة عيدكم", "عيد مبارك", "عيدكم مبارك", "كل عام وانتم بخير"
            ],
            "responses_arabizi": [
                "Saha 3idek kho, koul 3am w ntouma bkhir w sa7a w lehna!",
                "3idkoum mabrouk w ta9abala Allahou minna wa minkoum, koul 3am bkhir!"
            ],
            "responses_arabic": [
                "صحة عيدكم وكل عام وأنتم بألف خير، ربي يتقبل منا ومنكم ولعقوبة للعام الجاي!",
                "عيدكم مبارك وسعيد، تقبل الله منا ومنكم وغفر لنا ولكم، ربي يحفظكم!"
            ]
        },
        {
            "intent": "GRATITUDE",
            "patterns_arabizi": [
                "merci", "merci bzaf", "ya3tik saha", "chokran", "chokran bzaf", "barak allah fik"
            ],
            "patterns_arabic": [
                "شكرا", "شكرا بزاف", "يعطيك الصحة", "الله يحفظك", "بارك الله فيك", "ربي يجازيك"
            ],
            "responses_arabizi": [
                "Bla mziya kho rabi yahfdhek, f lkhedma f ay wa9t!",
                "Yselmek kho w rabi yjazik, marhba bik dima!",
                "Bla jmil khouna, rabi ybarek fik!"
            ],
            "responses_arabic": [
                "بلا مزية خويا ربي يحفظك، في الخدمة دائماً ومرحباً بيك في أي وقت!",
                "الله يسلمك ويعافيك خويا العزيز، وفيك بارك الله!",
                "العفو وبلا جميل، ربي يرزقك من واسع فضله!"
            ]
        },
        {
            "intent": "FAREWELL",
            "patterns_arabizi": [
                "b9a 3la khir", "bye", "bslama", "tchao", "au revoir", "thala", "thala f rouhek"
            ],
            "patterns_arabic": [
                "بقى على خير", "بالسلامة", "في أمان الله", "تهلا في روحك", "تبقاو على خير"
            ],
            "responses_arabizi": [
                "B9a 3la khir kho, thala f rouhek w nharek mabrouk!",
                "Bslama kho, marhba bik f ay wa9t w rabi yahfdhek!"
            ],
            "responses_arabic": [
                "بالسلامة وفي أمان الله وحفظه، تهلا في روحك خويا ونهارك مبروك!",
                "تبقاو على خير ونورتونا، مرحباً بيكم دائماً!"
            ]
        },
        {
            "intent": "NEWS_INQUIRY",
            "patterns_arabizi": [
                "kash jdid", "kash akhbar", "kayen jdid", "kash ma kayen", "kash sel3a"
            ],
            "patterns_arabic": [
                "كاش جديد", "كاش أخبار", "كاين جديد", "كاش ما كاين", "كاش سلعة جديدة"
            ],
            "responses_arabizi": [
                "Koulchi mrigel w labas hamdoulah! Kayen jdid w sel3a top, kash ma rak thawas?",
                "Hamdoulah kolchi bkhir, dakhlet sel3a chaba bzaf marhba bik!"
            ],
            "responses_arabic": [
                "كلش مريڤل والحمد لله على خير! دخلتنا سلعة جديدة ممتازة كاش ما راك تحوس؟",
                "كاين الخير ربي يبارك! الجديد راهو واجد وسومات شابة بزاف، مرحباً بيك!"
            ]
        },
        {
            "intent": "COMMERCE_ORDER_HELP",
            "patterns_arabizi": [
                "kifech ncommandi", "hab nchri", "kifech nechri", "hab ncommander", "hab nedi haba"
            ],
            "patterns_arabic": [
                "كيفاش نكوموندي", "حاب نشري", "كيفاش نشري", "حاب ندي حبة", "طريقة الطلب"
            ],
            "responses_arabizi": [
                "Sahl bzaf kho: ab3atli l'adresse, lwilaya, numéro de téléphone w l'article li habou w nlivriwlek l bab dar!",
                "Marhba bik! Khallili nom, prénom, numéro w lwilaya f ميساج w nconfirmiwlek la commande f lwa9t!"
            ],
            "responses_arabic": [
                "ساهلة ماهلة خويا: ابعثلي العنوان، الولاية، رقم الهاتف والمنتج لي حابو ونوصلوهولك لباب الدار!",
                "مرحباً بيك خونا! خليلي الاسم، رقم الهاتف، والولاية ونكونفيرميولك الطلبية فوراً!"
            ]
        },
        {
            "intent": "DELIVERY_LOCATION_HELP",
            "patterns_arabizi": [
                "win rakoum", "kayen livraison", "tlivriw", "chhal livri", "tlivriw l 69 wilaya"
            ],
            "patterns_arabic": [
                "وين راكم", "كاين توصيل", "توصلو", "شحال التوصيل", "توصلو للدار", "توصيل 69 ولاية"
            ],
            "responses_arabizi": [
                "Kaynin f dzayer w ndirou livri rapide l ga3 69 wilaya l bab dar wla stop desk!",
                "Livraison dispo f ga3 69 wilaya b prix mrigel w khalass 3and l'istilam COD!"
            ],
            "responses_arabic": [
                "متواجدين في الجزائر ونوفرو التوصيل السريع لجميع 69 ولاية لباب الدار أو ستوب ديسك!",
                "التوصيل متوفر لـ 69 ولاية والدفع عند الاستلام بعد ما تفيزي سلعتك وتتأكد منها!"
            ]
        }
    ]
}

# Write files to both Python and JS packages
for target_dir in [PY_DATA, JS_DATA]:
    target_dir.mkdir(parents=True, exist_ok=True)
    
    with open(target_dir / 'wilayas.json', 'w', encoding='utf-8') as f:
        json.dump(synced_wilayas, f, ensure_ascii=False, indent=2)
        
    with open(target_dir / 'profanity.json', 'w', encoding='utf-8') as f:
        json.dump(profanity_dataset, f, ensure_ascii=False, indent=2)
        
    with open(target_dir / 'franco_darja.json', 'w', encoding='utf-8') as f:
        json.dump(franco_darja_dataset, f, ensure_ascii=False, indent=2)
        
    with open(target_dir / 'memes.json', 'w', encoding='utf-8') as f:
        json.dump(memes_dataset, f, ensure_ascii=False, indent=2)
        
    with open(target_dir / 'dialogue_rules.json', 'w', encoding='utf-8') as f:
        json.dump(dialogue_rules, f, ensure_ascii=False, indent=2)

print("All massive datasets successfully generated and synchronized across Python and TypeScript!")
