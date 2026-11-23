"""
Enrich linguistic datasets (lexicon.json, stopwords.json, arabizi_rules.json)
with comprehensive authentic Algerian Darja expressions from e-commerce,
customer feedback, and regional dialects.
"""
import json
from pathlib import Path


def enrich_lexicon(root: Path) -> None:
    path = root / 'data' / 'lexicon.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_positives = {
        # Authentic Algerian praise & satisfaction expressions
        "سلعة روعة": 0.95,
        "ما شاء الله": 0.95,
        "الله يبارك": 0.95,
        "يعطيكم الصحة": 0.95,
        "قمة في الروعة": 0.95,
        "طوب دي طوب": 0.95,
        "سلعة لوكس": 0.9,
        "سلعة شابة": 0.85,
        "سلعة شابة بزاف": 0.95,
        "خدمة نقية": 0.9,
        "خدمة في المستوى": 0.9,
        "ما عندي ما نقول": 0.9,
        "تستاهلو خمس نجوم": 0.95,
        "حطة": 0.85,
        "باهية بزاف": 0.85,
        "تبارك الله": 0.9,
        "ناس ملاح": 0.85,
        "أمانة وثقة": 0.95,
        "سيرفيس شباب": 0.85,
        "سلعة أصلية": 0.9,
        "سلعة دوريجين": 0.9,
        "كيما فوطو": 0.85,
        "كيما التصويرة": 0.85,
        "ربي يوفقكم": 0.85,
        "ربي يجازيكم": 0.85,
        "خدمة سريعة": 0.85,
        "توصيل سريع": 0.85,
        "معاملة راقية": 0.9,
        "مشكورين": 0.8,
        "عجبني بزاف": 0.9,
        "عجبتني بزاف": 0.9,
        # Arabizi & French loan expressions
        "top du top": 0.95,
        "la classe": 0.9,
        "chaba bzf": 0.95,
        "chaba bezaf": 0.95,
        "hayla bzf": 0.95,
        "hayla bezaf": 0.95,
        "lah ybarek": 0.95,
        "lahibarek": 0.95,
        "machaallah": 0.95,
        "tbarkellah": 0.95,
        "service impecable": 0.95,
        "service tayara": 0.9,
        "mrigla": 0.85,
        "mrigel": 0.85,
        "kolchi mrigel": 0.9,
        "dorigine": 0.9,
        "originale": 0.9,
        "produit hayel": 0.9,
        "livraison rapide": 0.85,
        "chapeau": 0.85,
        "merci bcp": 0.8,
        "merci bezaf": 0.85,
    }

    new_negatives = {
        # Authentic Algerian complaints & negative expressions
        "سلعة شينوة": -0.85,
        "سلعة فالصو": -0.9,
        "مخدوعة": -0.85,
        "مغشوشة": -0.9,
        "تبهديلة": -0.9,
        "كارثة": -0.9,
        "حرام عليكم": -0.95,
        "ما تصلحش": -0.85,
        "ما يصلحش": -0.85,
        "غير ما تشريوش": -0.95,
        "تضييع دراهم": -0.9,
        "سقاطة": -0.85,
        "بخصتو بينا": -0.9,
        "ما نزيدش نشري": -0.9,
        "سلعة ميتة": -0.85,
        "سلعة مفاتشة": -0.85,
        "خدمة مقودة": -0.9,
        "ما يخدمش": -0.8,
        "ما تخدمش": -0.8,
        "سلعة عيانة بزاف": -0.95,
        "روطار كبير": -0.8,
        "حقارة": -0.9,
        "سرقة عيني عينك": -0.95,
        "كذابين": -0.9,
        "تخرعيط": -0.85,
        "تمنشير": -0.8,
        "فشلتوني": -0.85,
        "ندمت لي شريت": -0.95,
        "ندمت": -0.75,
        "ماشي دوريجين": -0.85,
        "ماشي أصلية": -0.85,
        "ماشي كيما التصويرة": -0.85,
        # Arabizi & French loan negative expressions
        "khorda": -0.85,
        "falso": -0.85,
        "chinwa": -0.8,
        "karita": -0.9,
        "tbahdila": -0.9,
        "7ram 3likom": -0.95,
        "ma tesla7ch": -0.85,
        "ma yesla7ch": -0.85,
        "tedyi3 draham": -0.9,
        "be5esto bina": -0.9,
        "service 0": -0.9,
        "zerro": -0.8,
        "arnaqueurs": -0.95,
        "la pire": -0.9,
        "retard kbir": -0.8,
        "habaltiha": -0.8,
        "nedmet": -0.75,
        "ma fihach": -0.7,
        "3ayana bzf": -0.9,
    }

    new_negators = [
        "ماشي", "ما كانش", "ماكاش", "ماكاينش", "ما هوش", "ماهيش",
        "machi", "makach", "makaynch", "mahouch", "mahich"
    ]

    new_intensifiers = {
        "بزاف": 1.5,
        "ياسر": 1.5,
        "قوي": 1.4,
        "طايشة": 1.3,
        "كراف": 1.5,
        "فوق اللازم": 1.5,
        "grave": 1.5,
        "tro": 1.4,
        "trop": 1.4,
        "bzzf": 1.5,
        "yasser": 1.5,
    }

    for k, v in new_positives.items():
        data['positive'][k] = v

    for k, v in new_negatives.items():
        data['negative'][k] = v

    for n in new_negators:
        if n not in data['negators']:
            data['negators'].append(n)

    for k, v in new_intensifiers.items():
        data['intensifiers'][k] = v

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] lexicon.json: {len(data['positive'])} positive, {len(data['negative'])} negative, {len(data['negators'])} negators, {len(data['intensifiers'])} intensifiers")


def enrich_stopwords(root: Path) -> None:
    path = root / 'data' / 'stopwords.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    additions = {
        "demonstratives": [
            "هاداك", "هاديك", "هادوك", "هادو", "هاذو", "هاذوك", "هاذي", "هادا",
            "hadak", "hadik", "hadouk", "hadou", "hadi", "hada"
        ],
        "question_words": [
            "وقتاش", "وينتا", "وقتاه", "فاش", "علاش", "علاه", "واشنهي", "واشنو", "شكون",
            "we9tach", "wektach", "wenta", "we9tah", "3lech", "3lah", "wachnou", "chkoune"
        ],
        "conjunctions": [
            "باشما", "كاشما", "باش", "كيما", "على خاطر", "باسكو",
            "bachma", "kachma", "bach", "kima", "parce que", "pask"
        ],
        "temporal": [
            "ضرك", "دروك", "دوك", "دك", "البارح", "غدوة", "اليوم", "دركا", "دروكا",
            "dork", "dorka", "drouk", "drouka", "lbarah", "ghedwa", "lyoum"
        ],
        "prepositions": [
            "من جيهة", "حتى لـ", "مور", "مورا",
            "men jihet", "mor", "mora"
        ],
    }

    for cat, words in additions.items():
        if cat not in data:
            data[cat] = []
        for w in words:
            if w not in data[cat]:
                data[cat].append(w)

    total = sum(len(v) for v in data.values())
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] stopwords.json: {total} stopwords across {len(data)} categories")


def enrich_arabizi_rules(root: Path) -> None:
    path = root / 'data' / 'arabizi_rules.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_overrides = {
        "nchlh": "ان شاء الله",
        "inchallah": "ان شاء الله",
        "inchaalah": "ان شاء الله",
        "stpl": "الله يعيشك",
        "svp": "من فضلك",
        "stp": "من فضلك",
        "mrc": "شكرا",
        "dsl": "سمحلي",
        "bshtk": "بصحتك",
        "bsha": "بصحتك",
        "yatik": "يعطيك",
        "sahbi": "صاحبي",
        "khoya": "خويا",
        "khti": "اختي",
        "chouf": "شوف",
        "chofi": "شوفي",
        "asma3": "اسمع",
        "drk": "درك",
        "dorka": "دروك",
        "dok": "دوك",
        "wela": "ولا",
        "bghit": "بغيت",
        "hbit": "حبيت",
        "kheli": "خلي",
        "khalih": "خليه",
        "3labali": "على بالي",
        "ma3labalich": "ما على باليش",
        "ma3ndich": "ما عنديش",
        "mafhmtch": "ما فهمتش",
        "fehmni": "فهمني",
        "fhamt": "فهمت",
        "mrigla": "مريقلة",
        "mrigel": "مريقل",
    }

    new_whitelist = [
        "livraison", "livreur", "bureau", "domicile", "facture", "garantie",
        "original", "produit", "commande", "client", "adresse", "couleur",
        "taille", "pointure", "modele", "marque", "qualite", "prix",
        "promo", "solde", "remise", "colis", "reclamation", "retour",
        "echange", "disponible", "rupture", "stock", "messagerie",
        "telephone", "numero", "confirmation", "validation", "expedition",
        "recu", "recuperer", "boutique", "magasin", "service", "support",
        "vendeur", "bouton", "ecran", "batterie", "chargeur", "accessoire",
        "ordinateur", "casque", "montre", "sac", "chaussure", "veste",
        "pantalon", "chemise", "noir", "blanc", "rouge", "bleu", "vert"
    ]

    for k, v in new_overrides.items():
        data['overrides'][k] = v

    for w in new_whitelist:
        if w not in data['french_whitelist']:
            data['french_whitelist'].append(w)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] arabizi_rules.json: {len(data['overrides'])} overrides, {len(data['french_whitelist'])} whitelist entries")


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    enrich_lexicon(root)
    enrich_stopwords(root)
    enrich_arabizi_rules(root)


if __name__ == '__main__':
    main()
