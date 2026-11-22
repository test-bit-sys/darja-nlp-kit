"""Interactive demo for darja-nlp-kit."""
import sys
from pathlib import Path

# Ensure local package is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "packages" / "python"))

from darja_nlp import (
    normalize,
    arabizi_to_arabic,
    tokenize,
    remove_stopwords,
    analyze_sentiment,
    extract_entities,
    detect_dialect,
)


def run_sample(text: str) -> None:
    print("\n" + "=" * 65)
    print(f"النص الأصلي (Original): {text}")
    print("-" * 65)

    # 1. Normalization
    norm = normalize(text)
    print(f"1. التطبيع (Normalized)       : {norm}")

    # 2. Arabizi to Arabic
    arabic = arabizi_to_arabic(text)
    print(f"2. تحويل الأرابيزي (Arabic)    : {arabic}")

    # 3. Tokenize & Negation
    tokens_res = tokenize(text)
    print(f"3. التقطيع (Tokens)            : {tokens_res.tokens}")
    if tokens_res.negations:
        neg_roots = [f"{n.original} -> جذر: {n.root}" for n in tokens_res.negations]
        print(f"   حالات النفي (ما..ش)         : {', '.join(neg_roots)}")

    # 4. Stopwords removal
    no_stopwords = remove_stopwords(text)
    print(f"4. بدون كلمات شائعة            : {no_stopwords}")

    # 5. Sentiment analysis
    sentiment = analyze_sentiment(text)
    sentiment_color = {
        "POSITIVE": "[إيجابي +]",
        "NEGATIVE": "[سلبي -]",
        "MIXED": "[مختلط ~]",
        "NEUTRAL": "[محايد o]",
    }.get(sentiment.label, sentiment.label)

    print(f"5. تحليل المشاعر (Sentiment)   : {sentiment_color} (Score: {sentiment.score})")
    if sentiment.positive_tokens:
        print(f"   الكلمات الإيجابية          : {sentiment.positive_tokens}")
    if sentiment.negative_tokens:
        print(f"   الكلمات السلبية            : {sentiment.negative_tokens}")

    # 6. Algerian Entities (69 Wilayas, Payments, Prices)
    entities = extract_entities(text)
    if entities.wilayas:
        w_strs = [f"{w.name_ar} / {w.name_fr} ({w.code_str})" for w in entities.wilayas]
        print(f"6. الولايات (Wilayas - 69)     : {', '.join(w_strs)}")
    if entities.payments:
        p_strs = [p.label for p in entities.payments]
        print(f"   طرق الدفع (Payments)        : {', '.join(p_strs)}")
    if entities.prices:
        pr_strs = [f"{p.raw} -> {p.amount} DZD" for p in entities.prices]
        print(f"   الأسعار (Prices)            : {', '.join(pr_strs)}")

    # 7. Regional Dialect Identification
    dialect = detect_dialect(text)
    print(f"7. اللهجة الجهوية (Dialect)    : [{dialect.region}] (الثقة: {int(dialect.confidence * 100)}%)")
    if dialect.detected_markers:
        print(f"   المؤشرات اللغوية المرصودة   : {dialect.detected_markers}")


def main() -> None:
    print("=" * 65)
    print("      DZ Open Suite - darja-nlp-kit Interactive Demo")
    print("=" * 65)

    samples = [
        "السلعة هاااااايلة بزاااااف و الخدمة فور، يعطيك الصحة! توصيل لبوسعادة",
        "produit mli7 bzaf livraison l wahran rotar chwiya, prix 4500 DA w khlass b baridimob",
        "سلعة عيانة و السيرفيس ماشي شباب قاع، ارناك كبيرة ما ننصحكمش",
        "شوالا راك باغي خوية غايا درك؟ كاين توصيل للسانية ولاية 31",
        "واشنهي هادا قداش يدير ياسر باهي سيرتا نخلصك كاش عند الاستلام بـ زوج ملاين",
    ]

    print("\n--- تشغيل عينات تجريبية من تعليقات التجارة الإلكترونية والولايات الـ 69 ---")
    for s in samples:
        run_sample(s)

    print("\n" + "=" * 65)
    print("الآن دورك! اكتب أي جملة بالدارجة أو الأرابيزي لتجربتها (أو اضغط Enter للخروج):")
    print("=" * 65)

    while True:
        try:
            user_input = input("\nأدخل نصاً (Input) > ").strip()
            if not user_input:
                print("إلى اللقاء! / Besslama!")
                break
            run_sample(user_input)
        except (KeyboardInterrupt, EOFError):
            print("\nإلى اللقاء!")
            break


if __name__ == "__main__":
    main()
