"""Master Builder v2:
1. Train compact zero-dependency sentiment model (data/sentiment_model.json) on 55k+ real Algerian texts
   while keeping strictly isolated held-out test samples for honest benchmarking.
2. Enrich core JSON linguistic & cultural datasets from DziriEval, DziriAlign, ADArabic-50K, DziriBERT.
3. Build conversational retrieval knowledge base (data/dialogue_kb.json) from DziriAlign, DziriEval & clean Telegram chats.
4. Build held-out real benchmark dataset (data/eval_benchmark.json) for CLI `darja-nlp eval`.
5. Build massive curated Fine-Tuning + DPO corpora (9,000+ samples) in Alpaca, ShareGPT, OpenAI JSONL, and DPO JSONL.
6. Sync all runtime JSON datasets across /data, packages/js/data, and packages/python/darja_nlp/data.
"""

import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FINETUNE_DIR = DATA_DIR / "fine_tuning"
SCRATCH = ROOT / "scratch_corpus"
FINETUNE_DIR.mkdir(parents=True, exist_ok=True)

RE_URL = re.compile(r"https?://\S+|@\w+")
RE_TASH = re.compile(r"[\u064B-\u065F\u0670\u0640]")
RE_ALEF = re.compile(r"[أإآ]")
RE_ELONG = re.compile(r"(.)\1{2,}")
RE_TOK = re.compile(r"[a-zA-Z0-9\u0621-\u064A\u0671-\u06D3]+|[👍👎❤️😍🔥💔😡😭🤣😂👏🌹🇩🇿😢😠🤬💯✅❌👌🥹]+")


def extract_sentiment_features(text: str) -> list[str]:
    t = RE_URL.sub(" ", str(text).lower())
    t = RE_TASH.sub("", t)
    t = RE_ALEF.sub("ا", t).replace("ة", "ه").replace("ى", "ي")
    t = RE_ELONG.sub(r"\1\1", t)
    toks = RE_TOK.findall(t)
    feats = list(toks)
    for i in range(len(toks) - 1):
        feats.append(f"{toks[i]}_{toks[i + 1]}")
    for w in toks:
        if len(w) >= 5 and w.isalpha():
            feats.append(f"p3:{w[:3]}")
            feats.append(f"s3:{w[-3:]}")
    return feats


def load_jsonl(path: Path) -> list[dict]:
    items = []
    if path.exists():
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    pass
    return items


def build_sentiment_model_and_benchmark():
    print("\n=== [1/6] TRAINING COMPACT ZERO-DEP SENTIMENT MODEL & BENCHMARK ===")
    ad_df = pd.read_csv(SCRATCH / "ad_arabic_50k.csv").dropna().sample(frac=1.0, random_state=42).reset_index(drop=True)
    # Strict held-out split: 2000 balanced/shuffled ADArabic test, rest train
    ad_test = ad_df.iloc[:2000]
    ad_train = ad_df.iloc[2000:]

    dz_train = pd.read_csv(SCRATCH / "dziribert_train_sent.csv").dropna(subset=["text", "label"])
    dz_test = pd.read_csv(SCRATCH / "dziribert_test_sent.csv").dropna(subset=["text", "label"])

    sep_train = pd.read_csv(SCRATCH / "sentiment_train.csv").dropna()
    sep_dev = pd.read_csv(SCRATCH / "sentiment_dev.csv").dropna()
    sep_test = pd.read_csv(SCRATCH / "sentiment_test.csv").dropna()

    train_pairs = (
        [(str(t), int(l), 1.0) for t, l in zip(ad_train["text"], ad_train["label"])]
        + [(str(t), int(l), 2.5) for t, l in zip(dz_train["text"], dz_train["label"])]
        + [(str(t), 0 if int(l) == 0 else 2, 3.0) for t, l in zip(sep_train["text"], sep_train["label"])]
        + [(str(t), 0 if int(l) == 0 else 2, 3.0) for t, l in zip(sep_dev["text"], sep_dev["label"])]
    )

    vocab_counts = {0: Counter(), 1: Counter(), 2: Counter()}
    doc_counts = Counter()
    global_df = Counter()

    for txt, lbl, wt in train_pairs:
        if lbl not in (0, 1, 2):
            continue
        doc_counts[lbl] += wt
        feats = extract_sentiment_features(txt)
        for f in feats:
            vocab_counts[lbl][f] += wt
        for f in set(feats):
            global_df[f] += 1

    N = sum(doc_counts.values())
    scored = []
    for f, df_c in global_df.items():
        if df_c < 5 or len(f) <= 1:
            continue
        tot = vocab_counts[0][f] + vocab_counts[1][f] + vocab_counts[2][f]
        chi = sum(
            ((vocab_counts[c][f] - tot * (doc_counts[c] / N)) ** 2)
            / (tot * (doc_counts[c] / N) + 1e-6)
            for c in (0, 1, 2)
        )
        scored.append((chi, f))

    scored.sort(reverse=True)
    K = 8000
    vocab = [f for _, f in scored[:K]]
    alpha = 1.0
    t_toks = {c: sum(vocab_counts[c][f] for f in vocab) for c in (0, 1, 2)}
    priors = [round(math.log(doc_counts[c] / N), 4) for c in (0, 1, 2)]
    weights = {}
    for f in vocab:
        weights[f] = [round(math.log((vocab_counts[c][f] + alpha) / (t_toks[c] + alpha * K)), 4) for c in (0, 1, 2)]

    def eval_split(texts, labels):
        ok = 0
        tot = 0
        for txt, lbl in zip(texts, labels):
            s = list(priors)
            for f in extract_sentiment_features(txt):
                w = weights.get(f)
                if w is not None:
                    s[0] += w[0]
                    s[1] += w[1]
                    s[2] += w[2]
            pred = 0 if (s[0] >= s[1] and s[0] >= s[2]) else (1 if s[1] >= s[2] else 2)
            if pred == int(lbl):
                ok += 1
            tot += 1
        return ok, tot, (ok / tot if tot else 0.0)

    ad_ok, ad_tot, ad_acc = eval_split(ad_test["text"], ad_test["label"])
    dz_ok, dz_tot, dz_acc = eval_split(dz_test["text"], dz_test["label"])
    sp_ok, sp_tot, sp_acc = eval_split(sep_test["text"], [0 if int(x) == 0 else 2 for x in sep_test["label"]])

    print(f"  Held-out ADArabic-2K      : {ad_ok}/{ad_tot} ({ad_acc:.2%})")
    print(f"  Held-out DziriBERT-2.3K   : {dz_ok}/{dz_tot} ({dz_acc:.2%})")
    print(f"  Held-out Algerian_sent-92 : {sp_ok}/{sp_tot} ({sp_acc:.2%})")

    model_obj = {
        "version": "2.0.0",
        "algorithm": "multinomial_nb_chi2",
        "labels": ["NEGATIVE", "NEUTRAL", "POSITIVE"],
        "vocab_size": len(weights),
        "training_samples": {
            "ad_arabic_train": len(ad_train),
            "dziribert_train": len(dz_train),
            "algerian_sentiment_train_dev": len(sep_train) + len(sep_dev),
            "total_raw_documents": len(ad_train) + len(dz_train) + len(sep_train) + len(sep_dev),
        },
        "heldout_eval": {
            "ad_arabic_2k_acc": round(ad_acc, 4),
            "dziribert_test_acc": round(dz_acc, 4),
            "algerian_sentiment_test_acc": round(sp_acc, 4),
        },
        "priors": priors,
        "weights": weights,
    }
    out_model = DATA_DIR / "sentiment_model.json"
    out_model.write_text(json.dumps(model_obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  Saved sentiment_model.json ({out_model.stat().st_size / 1024:.1f} KB)")

    # Save clean compact held-out evaluation benchmark (600 samples across sources)
    bench_items = []
    lbl_name = {0: "NEGATIVE", 1: "NEUTRAL", 2: "POSITIVE"}
    for cls in (0, 1, 2):
        sub = ad_test[ad_test["label"] == cls].head(120)
        for txt in sub["text"]:
            bench_items.append({"source": "ADArabic-50K", "text": str(txt), "label": lbl_name[cls]})
    for txt, lbl in zip(dz_test["text"].head(150), dz_test["label"].head(150)):
        bench_items.append({"source": "DziriBERT-Twifil", "text": str(txt), "label": lbl_name[int(lbl)]})
    for txt, lbl in zip(sep_test["text"].head(90), sep_test["label"].head(90)):
        mapped = "NEGATIVE" if int(lbl) == 0 else "POSITIVE"
        bench_items.append({"source": "Algerian_sentiment", "text": str(txt), "label": mapped})

    bench_path = DATA_DIR / "eval_benchmark.json"
    bench_path.write_text(json.dumps({"version": "1.0.0", "count": len(bench_items), "sentiment": bench_items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Saved eval_benchmark.json ({len(bench_items)} held-out items)")


def enrich_core_datasets():
    print("\n=== [2/6] ENRICHING CORE DATASETS FROM REAL CORPORA ===")

    # A. Enrich lexicon.json with verified pure positive/negative words mined from ADArabic-50K
    lex_path = DATA_DIR / "lexicon.json"
    lexicon = json.load(open(lex_path, encoding="utf-8"))

    verified_pos = {
        "رائع": 0.9, "رائعة": 0.9, "اروع": 0.95, "القمة": 0.9, "بالتوفيق": 0.85,
        "يوفقك": 0.85, "يوفقكم": 0.85, "يحفضك": 0.85, "جزاك": 0.85, "يجازيك": 0.85,
        "يعافيك": 0.8, "ويعافيك": 0.8, "حفظك": 0.85, "التألق": 0.85, "النجاح": 0.85,
        "ماشاءالله": 0.95, "جزيلا": 0.75, "courage": 0.75, "bonne": 0.75, "belle": 0.85,
        "nchlh": 0.65, "ya3tik": 0.8, "bsahtek": 0.85, "mrehba": 0.8, "hetta": 0.9,
        "n9iya": 0.8, "melli7": 0.85, "sa7a": 0.75,
    }
    verified_neg = {
        "رخيس": -0.9, "مرخس": -0.9, "الرخس": -0.9, "كذاب": -0.9, "الكذاب": -0.9,
        "كذب": -0.85, "تكذب": -0.85, "يكذب": -0.85, "تفو": -0.95, "شيات": -0.85,
        "الخرطي": -0.9, "خرطي": -0.85, "تخرط": -0.85, "منافق": -0.9, "الزبل": -0.9,
        "تافهة": -0.85, "جايح": -0.85, "خبيث": -0.9, "سراق": -0.95, "سراقين": -0.95,
        "فاشل": -0.85, "فاشلين": -0.85, "عيب": -0.7, "تبهديلة": -0.9, "معفون": -0.85,
        "معفونة": -0.85, "كهر": -0.8, "غالي": -0.65, "غالية": -0.65, "nar": -0.65,
    }
    for k, v in verified_pos.items():
        lexicon["positive"].setdefault(k, v)
    for k, v in verified_neg.items():
        lexicon["negative"].setdefault(k, v)
    lex_path.write_text(json.dumps(lexicon, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  lexicon.json -> {len(lexicon['positive'])} pos, {len(lexicon['negative'])} neg")

    # B. Enrich arabizi_rules.json safely (overrides + french_whitelist from DziriAlign/ADArabic)
    ar_path = DATA_DIR / "arabizi_rules.json"
    ar_rules = json.load(open(ar_path, encoding="utf-8"))
    new_overrides = {
        "wlh": "والله", "wlah": "والله", "bsahtek": "بصحتك", "bsa7tek": "بصحتك",
        "ma3lich": "معليش", "ma3liche": "معليش", "khouya": "خويا", "khoya": "خويا",
        "mrehba": "مرحبا", "marhba": "مرحبا", "bezzaf": "بزاف", "bzaf": "بزاف",
        "chwiya": "شوية", "chwaya": "شوية", "melyoun": "مليون", "mlyon": "مليون",
        "melyon": "مليون", "mlayen": "ملاين", "sabat": "صباط", "t9acher": "تقاشر",
        "hetta": "حطة", "n9iya": "نقية", "mellekher": "ماللخر", "doro": "دورو",
        "y9ar3ej": "يقرعج", "thbliii": "تهبلي", "tehbali": "تهبلي", "3aychek": "عيشك",
        "ya3tik": "يعطيك", "sa7a": "صحة", "chhal": "شحال", "ch7al": "شحال",
    }
    for k, v in new_overrides.items():
        ar_rules["overrides"].setdefault(k, v)
    new_fr = ["cadeau", "casse", "coiffeur", "souris", "plomberie", "kilo", "morkso", "gamer", "origine", "policy"]
    for w in new_fr:
        if w not in ar_rules["french_whitelist"]:
            ar_rules["french_whitelist"].append(w)
    ar_path.write_text(json.dumps(ar_rules, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  arabizi_rules.json -> {len(ar_rules['overrides'])} overrides, {len(ar_rules['french_whitelist'])} french_whitelist")

    # C. Enrich franco_darja.json with verified DziriEval code-switching verbs
    fr_path = DATA_DIR / "franco_darja.json"
    franco = json.load(open(fr_path, encoding="utf-8"))
    existing_fr = {w.get("arabizi", "").lower() for w in franco.get("words", [])}
    new_franco_items = [
        {"darja_ar": "نفليكسي", "arabizi": "nflexy", "fr_origin": "flexy", "category": "verbs_telecom", "meaning_ar": "أرسل رصيد هاتف", "example": "راني نفليكسي مية الف فالتليفون"},
        {"darja_ar": "نبوانتي", "arabizi": "nbwanti", "fr_origin": "pointer", "category": "verbs_work", "meaning_ar": "أسجل حضوري في العمل", "example": "لازم نروح نبوانتي على الثمانية"},
        {"darja_ar": "نريغلي", "arabizi": "nregli", "fr_origin": "régler", "category": "verbs_service", "meaning_ar": "أحل الإشكال أو أسوي الحساب", "example": "ارواح نريغليوها درك"},
        {"darja_ar": "نديباني", "arabizi": "ndepanni", "fr_origin": "dépanner", "category": "verbs_service", "meaning_ar": "أساعد مؤقتاً أو أفك ضيقة", "example": "ديبانيتو بـ 100 ألف باش يسلك أمورو"},
        {"darja_ar": "نفاليدي", "arabizi": "nvalidi", "fr_origin": "valider", "category": "verbs_commerce", "meaning_ar": "أؤكد وأعتمد الطلب", "example": "ابعثلي النميرو ونفاليديلك الكوموند"},
        {"darja_ar": "نروتورني", "arabizi": "nretourni", "fr_origin": "retourner", "category": "verbs_commerce", "meaning_ar": "أعيد السلعة أو أرجع", "example": "إذا ما جاتكش الطاي نروتورنيها عادي"},
        {"darja_ar": "نسيي", "arabizi": "nsiyi", "fr_origin": "essayer", "category": "verbs_commerce", "meaning_ar": "أجرب أو أقيس", "example": "نقدر نسيي السبردينة قبل ما نخلص؟"},
        {"darja_ar": "نكومبيلي", "arabizi": "ncompili", "fr_origin": "compiler", "category": "verbs_tech", "meaning_ar": "أجمع الكود أو أنسق الملفات", "example": "راني نكومبيلي فالمشروع"},
    ]
    for item in new_franco_items:
        if item["arabizi"].lower() not in existing_fr:
            franco["words"].append(item)
            existing_fr.add(item["arabizi"].lower())
    franco["count"] = len(franco["words"])
    fr_path.write_text(json.dumps(franco, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  franco_darja.json -> {franco['count']} hybrid terms")

    # D. Enrich dialects.json with DziriEval regional markers
    dia_path = DATA_DIR / "dialects.json"
    dia = json.load(open(dia_path, encoding="utf-8"))
    regional_additions = {
        "WEST": ["ڨارع", "ڨارعلي", "الشطابة", "الشرجم", "خيزو", "ڨورع", "نستناك", "9are3", "cherjem"],
        "EAST": ["السنارية", "المصلحة", "ماعلاباليش", "واشبيها", "بركاني", "هايا", "senarya", "moslaha"],
        "CENTER": ["الزرودية", "قوسطو", "شغول", "نتاع", "دك", "هاك", "zroudiya", "bessah"],
        "SOUTH": ["أرجى", "أرجاني", "بصح زين", "قواكم الله", "مرحبتين", "كاش علوم", "arja"],
    }
    for reg, additions in regional_additions.items():
        if reg in dia["regions"]:
            cur = dia["regions"][reg]["markers"]
            for m in additions:
                if m not in cur:
                    cur.append(m)
    dia_path.write_text(json.dumps(dia, ensure_ascii=False, indent=2), encoding="utf-8")
    print("  dialects.json enriched across all 4 regions.")

    # E. Enrich culture.json & slang.json with curated DziriEval items
    cult_path = DATA_DIR / "culture.json"
    cult = json.load(open(cult_path, encoding="utf-8"))
    existing_prov = {p["text"] for p in cult.get("proverbs", [])}
    new_proverbs = [
        {"text": "العود اللي تحقرو يعميك", "arabizi": "el 3oud li ta7gro ya3mik", "meaning": "لا تستهزئ بالشيء أو الشخص الضعيف فقد يغلبك", "category": "wisdom", "region": "NATIONAL"},
        {"text": "اللي يخلط روحو للنخالة ينقبو الدجاج", "arabizi": "li ykhelet rou7o l nokhala yna9bo djaj", "meaning": "من يضع نفسه في مواقف مشبوهة يتحمل نتائجها", "category": "wisdom", "region": "NATIONAL"},
        {"text": "جا يعاونو في قبر باباه هربلو بالفاس", "arabizi": "ja y3awno f 9ber babah hreblo b lfass", "meaning": "طلبت عوناً من شخص فزادك ورطة", "category": "humor", "region": "NATIONAL"},
        {"text": "الخيل مربوطة والحمير تبوط", "arabizi": "el khil marbouta w lhmir tbout", "meaning": "أصحاب الكفاءة محاصرون وغير الأكفاء يتصدرون المشهد", "category": "satire", "region": "NATIONAL"},
    ]
    for np in new_proverbs:
        if np["text"] not in existing_prov:
            cult["proverbs"].append(np)
            existing_prov.add(np["text"])
    cult_path.write_text(json.dumps(cult, ensure_ascii=False, indent=2), encoding="utf-8")

    slang_path = DATA_DIR / "slang.json"
    slang = json.load(open(slang_path, encoding="utf-8"))
    existing_slang = {s["term"] for s in slang.get("expressions", [])}
    new_slang = [
        {"term": "الحرڤة", "arabizi": "lharga / 7arga", "meaning": "الهجرة غير الشرعية عبر البحر", "type": "youth_slang", "polarity": "NEUTRAL"},
        {"term": "دير الميز", "arabizi": "dir lmiz", "meaning": "قيم الوضع وقدّر الموقف بذكاء", "type": "street_wisdom", "polarity": "POSITIVE"},
        {"term": "تحلب", "arabizi": "ta7leb", "meaning": "تفطن وتعلم القوالب ولم يعد مغفلاً", "type": "youth_slang", "polarity": "NEUTRAL"},
        {"term": "يقرعج", "arabizi": "y9ar3ej", "meaning": "يتطفل ويتجسس لمعرفة أخبار الناس", "type": "youth_slang", "polarity": "NEGATIVE"},
    ]
    for ns in new_slang:
        if ns["term"] not in existing_slang:
            slang["expressions"].append(ns)
            existing_slang.add(ns["term"])
    slang_path.write_text(json.dumps(slang, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  culture.json ({len(cult['proverbs'])} proverbs) & slang.json ({len(slang['expressions'])} expressions) updated.")


def build_dialogue_kb():
    print("\n=== [3/6] BUILDING RETRIEVAL DIALOGUE KB (DziriAlign + DziriEval + Clean Chat) ===")
    kb_entries = []

    # 1. Clean high-grade DziriAlign bargaining & daily dialogues (400 curated items)
    align_items = load_jsonl(SCRATCH / "DziriAlign.jsonl")
    for idx, item in enumerate(align_items[:400]):
        prompt = re.sub(r"\s+", " ", item.get("prompt", "")).strip()
        chosen = re.sub(r"\s+", " ", item.get("chosen", "")).strip()
        if 8 <= len(prompt) <= 220 and 10 <= len(chosen) <= 320:
            has_ar = bool(re.search(r"[\u0600-\u06FF]", prompt))
            kb_entries.append({
                "id": f"align_{idx}",
                "source": "DziriAlign",
                "script": "arabic" if has_ar else "arabizi",
                "prompt": prompt,
                "reply": chosen,
                "intent": "COMMERCE_BARGAIN" if any(k in prompt.lower() for k in ["chhal", "شحال", "سومة", "غالي", "ghali", "prix", "khal"]) else "CONVERSATION",
            })

    # 2. Clean DziriEval cultural & linguistic QA entries (200 curated items)
    ev_items = load_jsonl(SCRATCH / "dzirieval.jsonl")
    selected_domains = {
        "Gastronomie Traditionnelle (المطبخ الجزائري)",
        "Proverbes et Sagesses",
        "Arabizi Standard & Chiffres",
        "Code-Switching (Mélange Darja-Français)",
        "Argot et Néologismes de la Jeunesse",
        "Toponymie et Surnoms des Villes",
    }
    ev_count = 0
    for idx, item in enumerate(ev_items):
        if item.get("domain") in selected_domains and ev_count < 200:
            q = re.sub(r"\s+", " ", item.get("question", "")).strip()
            ans = item.get("choices", {}).get(item.get("answer", ""), "")
            exp = re.sub(r"\s+", " ", item.get("explanation", "")).strip()
            reply = f"{ans}. {exp}" if exp else ans
            if 10 <= len(q) <= 220 and reply:
                kb_entries.append({
                    "id": f"eval_{idx}",
                    "source": "DziriEval",
                    "script": "arabic",
                    "prompt": q,
                    "reply": reply,
                    "intent": "CULTURAL_QA",
                })
                ev_count += 1

    kb_path = DATA_DIR / "dialogue_kb.json"
    kb_path.write_text(json.dumps({"version": "1.0.0", "count": len(kb_entries), "entries": kb_entries}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"  Saved dialogue_kb.json ({len(kb_entries)} real retrieval entries, {kb_path.stat().st_size / 1024:.1f} KB)")


def build_finetuning_v2():
    print("\n=== [4/6] GENERATING MASSIVE CURATED FINE-TUNING & DPO CORPORA ===")
    alpaca = []
    sharegpt = []
    openai_rows = []
    dpo_rows = []

    def add_sample(instruction: str, user_input: str, assistant_output: str, source: str):
        alpaca.append({"instruction": instruction, "input": user_input, "output": assistant_output, "source": source})
        user_msg = f"{instruction}\n{user_input}" if user_input else instruction
        sharegpt.append({"conversations": [{"from": "human", "value": user_msg}, {"from": "gpt", "value": assistant_output}], "source": source})
        openai_rows.append({
            "messages": [
                {"role": "system", "content": "You are Darja-NLP, an authentic Algerian AI assistant fluent in Algerian Arabic, Arabizi, and French code-switching."},
                {"role": "user", "content": user_msg},
                {"role": "assistant", "content": assistant_output},
            ]
        })

    # 1. DziriAlign (1,000 high-grade human-evaluated pairs + DPO)
    align_items = load_jsonl(SCRATCH / "DziriAlign.jsonl")
    for item in align_items:
        p = re.sub(r"\s+", " ", item.get("prompt", "")).strip()
        c = re.sub(r"\s+", " ", item.get("chosen", "")).strip()
        r = re.sub(r"\s+", " ", item.get("rejected", "")).strip()
        if p and c:
            add_sample("أجب بالدارجة الجزائرية الأصيلة بأسلوب بشري طبيعي ولطيف ومناسب للسياق الجزائري:", p, c, "DziriAlign")
            if r:
                dpo_rows.append({"prompt": p, "chosen": c, "rejected": r, "source": "DziriAlign"})

    # 2. DziriEval (1,000 Algerian culture, language, history, proverbs QA pairs)
    ev_items = load_jsonl(SCRATCH / "dzirieval.jsonl")
    for item in ev_items:
        q = re.sub(r"\s+", " ", item.get("question", "")).strip()
        ans = item.get("choices", {}).get(item.get("answer", ""), "")
        exp = re.sub(r"\s+", " ", item.get("explanation", "")).strip()
        out = f"{ans}\nالتوضيح: {exp}" if exp else ans
        if q and out:
            add_sample("أجب على السؤال التالي حول الثقافة والتاريخ واللهجة الجزائرية بالدارجة:", q, out, "DziriEval")

    # 3. Real Telegram Chats from asce3/algerian-chat-messages (2,400 clean exchanges)
    chat_items = load_jsonl(SCRATCH / "chat_messages_sample.jsonl")
    chat_count = 0
    for item in chat_items:
        txt = re.sub(r"\s+", " ", item.get("text", "")).strip()
        reply = re.sub(r"\s+", " ", item.get("replytext", "") or "").strip()
        if txt and reply and "http" not in txt and "http" not in reply and 5 <= len(txt) <= 180 and 5 <= len(reply) <= 180:
            if not any(b in txt or b in reply for b in ["t.me", "قناة", "ملصقات", "اشتراك", "ممنوع"]):
                add_sample("تفاعل في محادثة جزائرية عفوية واقعية بالرد المناسب للرسالة التالية:", reply, txt, "asce3/algerian-chat")
                chat_count += 1
                if chat_count >= 2400:
                    break

    # 4. Balanced 3-class Sentiment (ADArabic-50K + DziriBERT -> 2,400 real comments, 800/class)
    ad_df = pd.read_csv(SCRATCH / "ad_arabic_50k.csv").dropna()
    ad_df = ad_df[ad_df["text"].astype(str).str.len().between(15, 220)]
    label_desc = {
        0: "سلبي (NEGATIVE) — النص يعبر عن استياء أو نقد أو غضب.",
        1: "محايد (NEUTRAL) — النص استفسار أو معلومة عامة بدون انحياز عاطفي واضح.",
        2: "إيجابي (POSITIVE) — النص يعبر عن رضا، تشجيع، أو مدح بالدارجة الجزائرية.",
    }
    for cls in (0, 1, 2):
        sub = ad_df[ad_df["label"] == cls].head(800)
        for txt in sub["text"]:
            clean_t = RE_URL.sub("", str(txt)).strip()
            if len(clean_t) >= 10:
                add_sample("حلل المشاعر في هذا النص الجزائري بدقة (إيجابي / محايد / سلبي):", clean_t, f"التصنيف: {label_desc[cls]}", "ADArabic-50K")

    # 5. Parallel Algerian-English Translation pairs (1,600 pairs bidirectional)
    trans_items = load_jsonl(SCRATCH / "translation_50k_sample.jsonl")
    t_count = 0
    for item in trans_items:
        ar = item.get("Arabic", "").strip()
        en = item.get("English", "").strip()
        if 8 <= len(ar) <= 220 and 8 <= len(en) <= 220:
            add_sample("ترجم الجملة التالية من الدارجة الجزائرية إلى الإنجليزية:", ar, en, "algerian-translation-50k")
            add_sample("ترجم الجملة الإنجليزية التالية إلى الدارجة الجزائرية المتداولة:", en, ar, "algerian-translation-50k")
            t_count += 1
            if t_count >= 800:
                break

    # 6. 69 Wilayas Logistics + Franco-Darja (now using correct "words" key!) + Memes
    wilayas = json.load(open(DATA_DIR / "wilayas.json", encoding="utf-8"))
    for w in wilayas:
        code = w["code"]
        name_ar = w["name_ar"]
        name_fr = w["name_fr"]
        communes = w.get("communes_sample", [])
        com = communes[0] if communes else name_ar
        add_sample(
            "أنت مساعد متجر إلكتروني جزائري. أجب الزبون بخصوص الشحن لولايته:",
            f"سلام خويا، توصلو لبلدية {com} بولاية {name_ar} ({code})؟",
            f"وعليكم السلام خويا! نعم التوصيل متوفر لجميع بلديات ولاية {name_ar} ({code}) بما فيها {com} في ظرف 24-48 ساعة لباب الدار أو ستوب ديسك.",
            "algeria-geo-69",
        )
        add_sample(
            "أجب على الزبون بالعربيزي حول التوصيل:",
            f"salam kayen livraison l {name_fr} ({code})?",
            f"Wa alaykom salam kho! Oui livraison dispo l {name_fr} ({code}) f 24-48h l bab dar wla stop desk, w khalass COD 3and l'istilam.",
            "algeria-geo-69",
        )

    franco = json.load(open(DATA_DIR / "franco_darja.json", encoding="utf-8"))
    for fw in franco.get("words", []):
        add_sample(
            "اشرح معنى وأصل هذا المصطلح الهجين (الفرونكو-عرب) في الدارجة الجزائرية:",
            f"واش معناها '{fw.get('darja_ar')}' ({fw.get('arabizi')})؟",
            f"المصطلح '{fw.get('darja_ar')}' ({fw.get('arabizi')}) مشتق من الفرنسية '{fw.get('fr_origin')}' ويعني: {fw.get('meaning_ar')}. مثال: {fw.get('example')}",
            "franco_darja",
        )

    memes = json.load(open(DATA_DIR / "memes.json", encoding="utf-8"))
    for m in memes.get("memes", []):
        add_sample(
            "اشرح هذا الميم أو التريند الجزائري الشهير وسياقه الثقافي:",
            f"واش قصة عبارة '{m.get('phrase')}'؟",
            f"عبارة '{m.get('phrase')}' تريند جزائري من مصدر ({m.get('origin')}). المعنى: {m.get('meaning')}",
            "algerian-memes",
        )

    with open(FINETUNE_DIR / "algerian_corpus_alpaca.json", "w", encoding="utf-8") as f:
        json.dump(alpaca, f, ensure_ascii=False, indent=2)
    with open(FINETUNE_DIR / "algerian_corpus_sharegpt.json", "w", encoding="utf-8") as f:
        json.dump(sharegpt, f, ensure_ascii=False, indent=2)
    with open(FINETUNE_DIR / "algerian_corpus_openai.jsonl", "w", encoding="utf-8") as f:
        for row in openai_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with open(FINETUNE_DIR / "algerian_dpo_align.jsonl", "w", encoding="utf-8") as f:
        for row in dpo_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"  Generated {len(alpaca):,} SFT instruction samples + {len(dpo_rows):,} DPO preference pairs!")


def update_and_run_sync():
    print("\n=== [5/6] UPDATING sync_data.py REGISTRY ===")
    sync_path = ROOT / "scripts" / "sync_data.py"
    sync_src = sync_path.read_text(encoding="utf-8")
    for fname in ["sentiment_model.json", "dialogue_kb.json", "eval_benchmark.json"]:
        if fname not in sync_src:
            sync_src = sync_src.replace(
                "'memes.json'",
                "'memes.json',\n        '" + fname + "'",
                1,
            )
    sync_path.write_text(sync_src, encoding="utf-8")
    print("  Updated scripts/sync_data.py to sync all models and knowledge bases.")


if __name__ == "__main__":
    build_sentiment_model_and_benchmark()
    enrich_core_datasets()
    build_dialogue_kb()
    build_finetuning_v2()
    update_and_run_sync()
    print("\n[6/6] Running python scripts/sync_data.py now...")
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_data.py")], check=True)
    print("\nALL DATA & TRAINED ARTIFACTS BUILT AND SYNCED SUCCESSFULLY!")
