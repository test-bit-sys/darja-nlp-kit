"""
Script to build comprehensive slang.json dataset
representing Algerian colloquial slang, youth expressions,
and street vocabulary in both Arabic script and Arabizi.
"""
import json
from pathlib import Path

SLANG_DATA = {
    "expressions": [
        # ================= Youth & Street Slang =================
        {
            "term": "تمسخير",
            "arabizi": "tmeskhir",
            "meaning": "المزاح غير الجاد، الاستهزاء أو تضييع الوقت دون فائدة.",
            "type": "youth_slang",
            "polarity": "NEGATIVE"
        },
        {
            "term": "خرطي",
            "arabizi": "khorti",
            "meaning": "كلام فارغ لا صحة له، تضليل أو ادعاء باطل دون دليل.",
            "type": "youth_slang",
            "polarity": "NEGATIVE"
        },
        {
            "term": "سكاتشو",
            "arabizi": "sketchou",
            "meaning": "موقف مضحك أو غريب أشبه بالتمثيلية والمسرحية الكوميدية.",
            "type": "youth_slang",
            "polarity": "NEUTRAL"
        },
        {
            "term": "تفرعين",
            "arabizi": "tfer3in",
            "meaning": "التعالي والتكبر والغرور على الناس دون حق.",
            "type": "youth_slang",
            "polarity": "NEGATIVE"
        },
        {
            "term": "تبهديل",
            "arabizi": "tebhdil",
            "meaning": "فضيحة وإحراج كبير ومظهر غير لائق أمام الناس.",
            "type": "youth_slang",
            "polarity": "NEGATIVE"
        },
        {
            "term": "تقياش",
            "arabizi": "t9yach",
            "meaning": "التأنق المبالغ فيه ولفت الانتباه بالمظهر أو الحركات.",
            "type": "youth_slang",
            "polarity": "NEUTRAL"
        },
        {
            "term": "تبياع",
            "arabizi": "tebya3",
            "meaning": "الوشاية بالآخرين وإفشاء أسرارهم لمن يعاقبهم.",
            "type": "youth_slang",
            "polarity": "NEGATIVE"
        },
        {
            "term": "تمهبيل",
            "arabizi": "temhbil",
            "meaning": "التصرف بجنون وعفوية أو قيادة جنونية متهورة.",
            "type": "youth_slang",
            "polarity": "NEUTRAL"
        },
        {
            "term": "مريول",
            "arabizi": "meryoul",
            "meaning": "شاب منغمس في موضة الشارع وموسيقى الراي ومظاهر الفخامة السطحية.",
            "type": "youth_slang",
            "polarity": "NEUTRAL"
        },
        {
            "term": "طاير",
            "arabizi": "tayr",
            "meaning": "ذكي جداً ولماح وسريع الفهم ولا يمكن خداعه بسهولة.",
            "type": "youth_slang",
            "polarity": "POSITIVE"
        },
        {
            "term": "كودار",
            "arabizi": "koudar",
            "meaning": "شخص صلب وعنيد لا يتراجع عن موقفه أو قراره.",
            "type": "youth_slang",
            "polarity": "NEUTRAL"
        },
        {
            "term": "سيريو",
            "arabizi": "serieux",
            "meaning": "جاد وموثوق ويتعامل باحترافية وانضباط.",
            "type": "youth_slang",
            "polarity": "POSITIVE"
        },

        # ================= E-Commerce & Marketplace Slang =================
        {
            "term": "سلعة كابا",
            "arabizi": "sl3a kaba",
            "meaning": "بضاعة مستوردة شخصياً في حقائب السفر من أوروبا وأصلية 100%.",
            "type": "commerce",
            "polarity": "POSITIVE"
        },
        {
            "term": "سلعة شناوة",
            "arabizi": "sl3a chinwa",
            "meaning": "سلعة مقلدة أو صينية رديئة الصنع والتصنيع التجاري الرخيص.",
            "type": "commerce",
            "polarity": "NEGATIVE"
        },
        {
            "term": "سلعة لوز",
            "arabizi": "sl3a louz",
            "meaning": "بضاعة ممتازة ونقية كاللوز، لا عيب فيها ومطابقة للمواصفات.",
            "type": "commerce",
            "polarity": "POSITIVE"
        },
        {
            "term": "خردة",
            "arabizi": "kherda",
            "meaning": "شيء مهترئ وفاسد ولا يصلح للاستخدام إطلاقاً.",
            "type": "commerce",
            "polarity": "NEGATIVE"
        },
        {
            "term": "مفرعسة",
            "arabizi": "mfer3sa",
            "meaning": "سلعة أو علبة ممزقة، مشوهة أو معطوبة بسبب سوء الشحن.",
            "type": "commerce",
            "polarity": "NEGATIVE"
        },
        {
            "term": "ديرلي سومة",
            "arabizi": "dirli souma",
            "meaning": "قدم لي سعراً تشجيعياً مخفضاً يناسب ميزانيتي لإتمام الشراء.",
            "type": "commerce",
            "polarity": "NEUTRAL"
        },
        {
            "term": "سومة حنينة",
            "arabizi": "souma 7nina",
            "meaning": "سعر طيب ورحيم ومناسب جداً للزبون دون مغالاة.",
            "type": "commerce",
            "polarity": "POSITIVE"
        },
        {
            "term": "لافان تاع السومة",
            "arabizi": "lafin ta3 souma",
            "meaning": "السعر النهائي القطعي الذي لا يقبل أي تخفيض إضافي.",
            "type": "commerce",
            "polarity": "NEUTRAL"
        },
        {
            "term": "ساعدني",
            "arabizi": "sa3edni",
            "meaning": "طلب التخفيض والمرونة في شروط الصفقة أو مصاريف التوصيل.",
            "type": "commerce",
            "polarity": "NEUTRAL"
        },
        {
            "term": "حشيتوهالي",
            "arabizi": "7chitohali",
            "meaning": "خدعتموني وبعتم لي سلعة لا تطابق ما وعدتم به (علامة تصعيد وشكوى قصوى).",
            "type": "commerce",
            "polarity": "NEGATIVE"
        },

        # ================= Emotional & Psychological States =================
        {
            "term": "زعاف",
            "arabizi": "z3af",
            "meaning": "غضب شديد واستياء وانفعال نفسي من موقف سلبي.",
            "type": "emotions",
            "polarity": "NEGATIVE"
        },
        {
            "term": "فشوش",
            "arabizi": "fchouch",
            "meaning": "دلع مفرط ورغبة في تلبية كل المطالب دون جهد.",
            "type": "emotions",
            "polarity": "NEUTRAL"
        },
        {
            "term": "قوسطو",
            "arabizi": "gousto",
            "meaning": "مزاج رائق وممتع ونفسية مقبلة على الحياة والتواصل.",
            "type": "emotions",
            "polarity": "POSITIVE"
        },
        {
            "term": "حشمان",
            "arabizi": "7echman",
            "meaning": "شديد الخجل والحياء والأدب في التعامل مع الآخرين.",
            "type": "emotions",
            "polarity": "POSITIVE"
        },
        {
            "term": "مبلع",
            "arabizi": "mballa3",
            "meaning": "مغلق النفسية ومكتئب أو المحل مغلق تماماً ولا يستقبل أحداً.",
            "type": "emotions",
            "polarity": "NEGATIVE"
        },
        {
            "term": "مروبل",
            "arabizi": "mroubel",
            "meaning": "مضطرب ومشوش التفكير أو المكان يعاني من فوضى عارمة.",
            "type": "emotions",
            "polarity": "NEGATIVE"
        },
        {
            "term": "فرحان فرحة لوز",
            "arabizi": "far7an far7a louz",
            "meaning": "في قمة السعادة والابتهاج والرضا التام عن الخدمة والمنتج.",
            "type": "emotions",
            "polarity": "POSITIVE"
        },
        {
            "term": "مريڤل",
            "arabizi": "mreguel",
            "meaning": "منضبط، مرتب، مضبوط ومجهز بدقة واحترافية.",
            "type": "qualities",
            "polarity": "POSITIVE"
        },
        {
            "term": "حطة",
            "arabizi": "7atta",
            "meaning": "غاية في الأناقة والجمال والفخامة والشياكة.",
            "type": "qualities",
            "polarity": "POSITIVE"
        },
        {
            "term": "هبال",
            "arabizi": "hbal",
            "meaning": "شيء رائع وخارق للعادة يثير الإعجاب الشديد لدرجة الذهول.",
            "type": "qualities",
            "polarity": "POSITIVE"
        },
        {
            "term": "فور بزاف",
            "arabizi": "fort bzaf",
            "meaning": "قوي جداً وممتاز ويفوق التوقعات.",
            "type": "qualities",
            "polarity": "POSITIVE"
        }
    ]
}

def main():
    root = Path(__file__).resolve().parent.parent
    data_dir = root / "data"
    out_file = data_dir / "slang.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(SLANG_DATA, f, ensure_ascii=False, indent=2)

    total = len(SLANG_DATA["expressions"])
    print(f"Generated {total} slang expressions in {out_file.relative_to(root)}")

if __name__ == "__main__":
    main()
