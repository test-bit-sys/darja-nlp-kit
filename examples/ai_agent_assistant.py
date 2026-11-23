"""
ai_agent_assistant.py - Algerian E-Commerce Customer Support AI Agent Example.

Demonstrates how to use `darja-nlp-kit` as a smart middleware / context provider
for an LLM (like GPT-4o, Gemini, Claude, or local LLMs).
"""

import sys
import os
import json

# Ensure darja_nlp package is discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../packages/python")))

from darja_nlp import (
    build_agent_context,
    format_agent_system_prompt,
    get_openai_tool_definitions,
)


def simulate_ai_agent_flow(customer_message: str):
    """Simulate the complete AI Agent customer flow."""
    print("=" * 75)
    print(f"📩 رسالة الزبون: \"{customer_message}\"")
    print("-" * 75)

    # 1. Run darja-nlp-kit agent context builder
    context = build_agent_context(customer_message, store_name="Bazar El Djazair")

    print("🔍 [1. ما اكتشفته المكتبة (Grounded NLP Intelligence)]:")
    if context["raw_message"] != context["arabic_transliterated"]:
        print(f"  • فك شفرة العربيزي : {context['arabic_transliterated']}")
    print(f"  • اللهجة الجهوية    : {context['dialect']['region']} (الثقة: {int(context['dialect']['confidence']*100)}%)")
    print(f"  • مؤشرات اللهجة    : {context['dialect']['detected_markers']}")
    print(f"  • المزاج والشعور   : {context['sentiment']['label']} (الدرجة: {context['sentiment']['score']})")
    print(f"  • النبرة الموجهة    : {context['sentiment']['tone']}")
    
    facts = context["grounded_facts"]
    print(f"  • الولايات المؤكدة : {facts['wilayas'] if facts['wilayas'] else 'لا توجد'}")
    print(f"  • المبالغ بالدينار  : {facts['prices_dzd'] if facts['prices_dzd'] else 'لا توجد'}")
    print(f"  • وسائل الدفع      : {facts['payments'] if facts['payments'] else 'لا توجد'}")
    print(f"  • شركات التوصيل    : {facts['delivery_companies'] if facts['delivery_companies'] else 'لا توجد'}")
    print(f"  • نمط الاستلام     : {facts['delivery_mode'] if facts['delivery_mode'] else 'لا يوجد'}")
    print(f"  • أرقام الهاتف     : {facts['phones'] if facts['phones'] else 'لا توجد'}")

    # 2. Build System Prompt for the LLM
    prompt = format_agent_system_prompt(context)
    
    print("\n🧠 [2. الـ Prompt المحقون للذكاء الاصطناعي (LLM Augmented Prompt)]:")
    first_lines = "\n".join(["    " + line for line in prompt.strip().split("\n")[:8]])
    print(f"{first_lines}\n    [... بقية سياق الحقائق المستخرجة وقواعد الرد ...]")

    # 3. Realistic human response matching the dialect and customer mood
    sample_responses = {
        "WEST": "وعليكم السلام خويا لعزيز! مرحبا بيك، السلعة راها كاينة وتوصيل لـ {wilaya} كاين بـ {carrier}. والسعر {price}. تقدر تفيرسي في BaridiMob ولا تخلص كاش كي توصلك السلعة غايا!",
        "EAST": "أهلاً وسهلاً بيك خويا ربي يحفظك! سلعة لوز وضرك نوجدوهالك للـ {wilaya}، الحساب راهو {price}. نبعثوها مع {carrier} وتقدر تخلص كي يوصلهالك الليفرور، عيشك!",
        "CENTER": "سلام خويا، مرحبا بيك عندنا! ما كاش مشكل خلاص، السلعة متوفرة ونوصلوها لـ {wilaya} مع {carrier}، والحساب {price}. الدفع تحب بريدي موب ولا كاش كي تلحقك؟",
        "NEGATIVE": "سلام عليكم خويا، حقك علينا ونعتذروا منك بزاف بزاف! ما تقلقش روحك كامل، المشكل نحلوهولك درك. قولي برك واش صرا بالضبط ونبدلولك السلعة ولا نرجعولك دراهمك في الحين."
    }

    print("\n🤖 [3. رد الذكاء الاصطناعي البشري الواقعي (Human-like AI Response)]:")
    if context["sentiment"]["label"] == "NEGATIVE":
        response = sample_responses["NEGATIVE"]
    else:
        wilaya_str = facts["wilayas"][0] if facts["wilayas"] else "عندك"
        price_str = facts["prices_dzd"][0] if facts["prices_dzd"] else "مضبوط"
        carrier_str = facts["delivery_companies"][0] if facts["delivery_companies"] else "شركة التوصيل"
        template = sample_responses.get(context["dialect"]["region"], sample_responses["CENTER"])
        response = template.format(wilaya=wilaya_str, price=price_str, carrier=carrier_str)

    print(f"  👉 \"{response}\"")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    print("\n🇩🇿 [darja-nlp-kit] محاكي وكيل الذكاء الاصطناعي للرد البشري على الزبائن\n")

    # Example 1: Customer from Constantine ordering with Arabizi, carrier, and phone
    simulate_ai_agent_flow(
        "salam khoya 3jebni l produit w rani hab nchrih b 2 mlayen l Constantine b yalidine stop desk. num ta3i: 0661234567"
    )

    # Example 2: Western customer with local slang, Wilaya 60 (Barika), and price in dinars
    simulate_ai_agent_flow(
        "sahbi rani baghi had lmontaj l barika w esq nkhles cash wla edahabia? w bchhal livraizon ltema?"
    )

    # Example 3: Angry customer complaining about a defective parcel
    simulate_ai_agent_flow(
        "khedma 3ayana w sil3a khorda wlah ma thechmou 7chitohali w l colis ja mfetchech!"
    )
