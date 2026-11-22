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
)


def run_sample(text: str) -> None:
    print("\n" + "=" * 60)
    print(f"النص الأصلي (Original): {text}")
    print("-" * 60)

    # 1. Normalization
    norm = normalize(text)
    print(f"1. التطبيع (Normalized)     : {norm}")

    # 2. Arabizi to Arabic
    arabic = arabizi_to_arabic(text)
    print(f"2. تحويل الأرابيزي (Arabic)  : {arabic}")

    # 3. Tokenize & Negation
    tokens_res = tokenize(text)
    print(f"3. التقطيع (Tokens)          : {tokens_res.tokens}")
    if tokens_res.negations:
        neg_roots = [f"{n.original} -> جذر: {n.root}" for n in tokens_res.negations]
        print(f"   حالات النفي الدائري (ما..ش): {', '.join(neg_roots)}")

    # 4. Stopwords removal
    no_stopwords = remove_stopwords(text)
    print(f"4. بدون كلمات شائعة          : {no_stopwords}")

    # 5. Sentiment analysis
    sentiment = analyze_sentiment(text)
    sentiment_color = {
        "POSITIVE": "[إيجابي +]",
        "NEGATIVE": "[سلبي -]",
        "MIXED": "[مختلط ~]",
        "NEUTRAL": "[محايد o]",
    }.get(sentiment.label, sentiment.label)

    print(f"5. تحليل المشاعر (Sentiment) : {sentiment_color} (Score: {sentiment.score})")
    if sentiment.positive_tokens:
        print(f"   الكلمات الإيجابية        : {sentiment.positive_tokens}")
    if sentiment.negative_tokens:
        print(f"   الكلمات السلبية          : {sentiment.negative_tokens}")
    if sentiment.negated:
        print(f"   تم رصد نفي معكوس        : نعم (Negation detected)")


def main() -> None:
    print("=" * 60)
    print("      DZ Open Suite - darja-nlp-kit Interactive Demo")
    print("=" * 60)

    samples = [
        "السلعة هاااااايلة بزاااااف و الخدمة فور، يعطيك الصحة!",
        "produit mli7 bzaf walakin livraison rotar chwiya, prix 4500 DA",
        "سلعة عيانة و السيرفيس ماشي شباب قاع، ارناك كبيرة ما ننصحكمش",
        "2ana 9rib نوصل، wesh rak khoya?",
        "مافهمتش علاش هاد التيليفون ماشي مليح، ما عجبنيش",
    ]

    print("\n--- تشغيل عينات تجريبية من تعليقات التجارة الإلكترونية الجزائرية ---")
    for s in samples:
        run_sample(s)

    print("\n" + "=" * 60)
    print("الآن دورك! اكتب أي جملة بالدارجة أو الأرابيزي لتجربتها (أو اضغط Enter للخروج):")
    print("=" * 60)

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
