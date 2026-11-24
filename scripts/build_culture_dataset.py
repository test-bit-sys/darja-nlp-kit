"""
Script to build comprehensive, verified culture.json dataset
encompassing Algerian Proverbs, Internet Memes & Trends,
Landmarks & Markets, and Traditional Cuisine & Sweets.
"""
import json
from pathlib import Path

CULTURE_DATA = {
    # ================= 1. PROVERBS & POPULAR SAYINGS (الأمثال والحكم الشعبية) =================
    "proverbs": [
        {
            "id": "prv_001",
            "text": "الحجرة في بلاصتها ثقيلة",
            "arabizi": "el 7ajra f blast-ha th9ila",
            "meaning": "الإنسان له وزنه وقيمته وهيبته حين يبقى في بيئته ومكانه الأصلي ومع أهله.",
            "category": "dignity",
            "region": "GENERAL"
        },
        {
            "id": "prv_002",
            "text": "طاح الحك وصاب غطاه",
            "arabizi": "tah l7ok w sab ghtah",
            "meaning": "يُضرب للتوافق التام بين شخصين في الطباع أو في المصالح، خاصة في الزواج أو الشراكة.",
            "category": "compatibility",
            "region": "GENERAL"
        },
        {
            "id": "prv_003",
            "text": "العروسة تشكرها أمها وخالتها",
            "arabizi": "el 3roussa techkorha omha w khaltha",
            "meaning": "يُقال بسخرية لمن يمدح نفسه أو يمدحه أقرب الناس إليه بدافع العاطفة دون موضوعية.",
            "category": "humor",
            "region": "GENERAL"
        },
        {
            "id": "prv_004",
            "text": "مول التاج ويحتاج",
            "arabizi": "moul et-taj w ya7taj",
            "meaning": "مهما بلغ الإنسان من الغنى أو السلطة والمكانة، فإنه يظل بحاجة إلى مساعدة الآخرين.",
            "category": "humility",
            "region": "GENERAL"
        },
        {
            "id": "prv_005",
            "text": "اللسان ما فيه عظم بصح يكسر العظام",
            "arabizi": "el lssan ma fih 3dhem bsah ykesser el 3dham",
            "meaning": "الكلمة الجارحة أشد وقعاً من الأذى الجسدي، لذا يجب الحذر وحفظ اللسان.",
            "category": "wisdom",
            "region": "GENERAL"
        },
        {
            "id": "prv_006",
            "text": "اللي فات مات وخلى الذكريات",
            "arabizi": "li fat mat w khalla ed-dikrayat",
            "meaning": "دعوة للمضي قدماً وعدم البكاء على الماضي والتصالح مع ما حصل.",
            "category": "optimism",
            "region": "GENERAL"
        },
        {
            "id": "prv_007",
            "text": "جاء يكحلها عماها",
            "arabizi": "ja yka7alha 3maha",
            "meaning": "يُضرب لمن أراد إصلاح أمر فزاده فساداً وسوءاً نتيجة قلة الخبرة أو التسرع.",
            "category": "warning",
            "region": "GENERAL"
        },
        {
            "id": "prv_008",
            "text": "ما يحس بالجمرة غير اللي كواتو",
            "arabizi": "ma y7ess bel jamra ghir li kwatou",
            "meaning": "لا يدرك عمق الألم وحرقة المشكلة إلا الشخص الذي يعيشها ويعاني منها شخصياً.",
            "category": "empathy",
            "region": "GENERAL"
        },
        {
            "id": "prv_009",
            "text": "خالط تصفى",
            "arabizi": "khalet tesfa",
            "meaning": "التنوع والتجربة والاحتكاك بالناس يكشف معادنهم الحقيقية ويوضح الأمور في النهاية.",
            "category": "experience",
            "region": "GENERAL"
        },
        {
            "id": "prv_010",
            "text": "كل خنفوس عند أمه غزال",
            "arabizi": "koll khenfouss 3and ommou ghzal",
            "meaning": "حب الأم لأبنائها أعمى، فترى فيهم الجمال والكمال مهما كانت عيوبهم في نظر الآخرين.",
            "category": "humor",
            "region": "GENERAL"
        },
        {
            "id": "prv_011",
            "text": "الصنعة في اليد أمان من الفقر",
            "arabizi": "es-san3a fel yed amane men el fa9r",
            "meaning": "الحرفة والمهارة اليدوية والعمل الحر تشكل سداً منيعاً يحمي صاحبها من العوز وضيق الحال.",
            "category": "work",
            "region": "GENERAL"
        },
        {
            "id": "prv_012",
            "text": "الجديد حبو والقديم لا تفرط فيه",
            "arabizi": "el jdid 7abbou w el 9dim la tfarrat fih",
            "meaning": "وازن بين قبول التطور والأشياء الجديدة وبين الحفاظ على الأصول والعلاقات القديمة الصادقة.",
            "category": "wisdom",
            "region": "GENERAL"
        },
        {
            "id": "prv_013",
            "text": "خبز الدار ياكلو البراني",
            "arabizi": "khobz ed-dar yaklou el barrani",
            "meaning": "يُقال حين يستفيد الغريب من خيرات البيت أو الوطن ويُحرم منها أصحاب الحق وأهل الدار.",
            "category": "critique",
            "region": "GENERAL"
        },
        {
            "id": "prv_014",
            "text": "مول النية يربح",
            "arabizi": "moul en-niya yerba7",
            "meaning": "صاحب النية الطيبة والسريرة النقية سينتصر ويوفقه الله مهما كاد له المخادعون.",
            "category": "faith",
            "region": "GENERAL"
        },
        {
            "id": "prv_015",
            "text": "خبي قرشك الأبيض ليومك الأسود",
            "arabizi": "khabbi 9erchek el byed l youmek el k7el",
            "meaning": "نصيحة بالادخار والتدبير المالي وعدم التبذير تحسباً للأزمات والظروف الطارئة.",
            "category": "finance",
            "region": "GENERAL"
        },
        {
            "id": "prv_016",
            "text": "اللي دارها بيديه يفكها بسنيه",
            "arabizi": "li darha b yeddih yfokha b sennih",
            "meaning": "من يتسبب في ورطة أو خطأ بقراره، عليه أن يتحمل المسؤولية كاملة ويجد الحل بنفسه.",
            "category": "responsibility",
            "region": "GENERAL"
        },
        {
            "id": "prv_017",
            "text": "الحديث قياس فيه الذهب وفيه النحاس",
            "arabizi": "el 7dith 9yas fih ed-dhahab w fih en-n7ass",
            "meaning": "الكلام له ميزان وقيمة؛ فمنه الثمين كالجواهر ومنه الرخيص الذي لا فائدة منه.",
            "category": "speech",
            "region": "GENERAL"
        },
        {
            "id": "prv_018",
            "text": "سعدك يا فاعل الخير",
            "arabizi": "sa3dek ya fa3el el khir",
            "meaning": "دعاء واستبشار بالخير والبركة لكل من يقدم العون للناس ويصلح بين البشر.",
            "category": "charity",
            "region": "GENERAL"
        },
        {
            "id": "prv_019",
            "text": "كي سيدي كي جوادو",
            "arabizi": "ki sidi ki jwadou",
            "meaning": "يُضرب للتشابه التام في الصفات السلبية أو الإيجابية بين الرئيس ومرؤوسيه.",
            "category": "critique",
            "region": "GENERAL"
        },
        {
            "id": "prv_020",
            "text": "الفم المسدود ما تدخلو ذبانة",
            "arabizi": "el femm el masdoud ma todkhlou debana",
            "meaning": "الصمت حكمة وحفظ اللسان يقي الإنسان من المشاكل وسوء الفهم ونقل الكلام.",
            "category": "silence",
            "region": "GENERAL"
        },
        {
            "id": "prv_021",
            "text": "يا شاري دالة ويا بايع دالة",
            "arabizi": "ya chari dalla w ya baye3 dalla",
            "meaning": "التجارة ربح وخسارة، والدنيا تدور يوماً لك ويوماً عليك، فلا تظلم ولا تتكبر.",
            "category": "commerce",
            "region": "GENERAL"
        },
        {
            "id": "prv_022",
            "text": "كول ما يعجبك والبس ما يعجب الناس",
            "arabizi": "koul ma ya3jbek w elbes ma ya3jeb en-nass",
            "meaning": "طعامك شأن خاص بك، أما مظهرك الخارجي وهندامك فيخضع للعرف والمظهر الاجتماعي المحترم.",
            "category": "society",
            "region": "GENERAL"
        },
        {
            "id": "prv_023",
            "text": "يا سعد من زار وخفف",
            "arabizi": "ya sa3d men zar w khaffaf",
            "meaning": "أفضل الزيارات هي الزيارات القصيرة اللطيفة التي لا تثقل على أهل البيت.",
            "category": "etiquette",
            "region": "GENERAL"
        },
        {
            "id": "prv_024",
            "text": "المكتوب ما منو هروب",
            "arabizi": "el mektoub ma mennou hroub",
            "meaning": "إيمان بالقضاء والقدر بأن ما كتبه الله للإنسان سيصيبه لا محالة.",
            "category": "faith",
            "region": "GENERAL"
        },
        {
            "id": "prv_025",
            "text": "اللي ما عندو سيدو عندو ربي",
            "arabizi": "li ma 3andou sidou 3andou rabbi",
            "meaning": "من انقطعت به السبل ولا يملك نفوذاً أو واسطة، فإن الله كافيه وناصره.",
            "category": "faith",
            "region": "GENERAL"
        }
    ],

    # ================= 2. MEMES, VIRAL TRENDS & POPULAR STREET PHRASES =================
    "memes_and_trends": [
        {
            "id": "meme_001",
            "phrase": "راك فاهم",
            "arabizi": "rak fahem",
            "meaning": "عبارة للتأكيد والاتفاق السريع، تعني: 'لقد استوعبت الفكرة تماماً' وتُستخدم ختاماً لأغلب الجمل الحوارية.",
            "tone": "conversational",
            "context": "شائعة جداً في الشارع ومنصات التواصل لتأكيد الفهم المشترك."
        },
        {
            "id": "meme_002",
            "phrase": "نلعبوا ولا نحرموا",
            "arabizi": "nel3bou wla n7armou",
            "meaning": "تعبير شهير عن العناد والتمسك بالموقف: 'إما أن نلعب بالقواعد التي تناسبني أو أفسد اللعبة على الجميع'.",
            "tone": "humorous_defiance",
            "context": "تُستخدم في المواقف الرياضية والسياسية ومناقشات البيع والشراء."
        },
        {
            "id": "meme_003",
            "phrase": "عش عيشة لبلاد",
            "arabizi": "3ich 3ichet leblad",
            "meaning": "دعوة للواقعية والتعايش مع الظروف المحلية الاقتصادية والاجتماعية دون تصنع أو ترفع.",
            "tone": "pragmatic",
            "context": "نصيحة ساخرة أو جدية للتأقلم مع واقع السوق والحياة اليومية."
        },
        {
            "id": "meme_004",
            "phrase": "هادي قاع ماكانش منها",
            "arabizi": "hadi ga3 makanch menha",
            "meaning": "نفي قاطع ومطلق: هذا الأمر غير حقيقي ومستحيل وخالٍ تماماً من الصحة.",
            "tone": "skeptical",
            "context": "رد فوري على الشائعات أو الادعاءات غير المنطقية والأسعار المبالغ فيها."
        },
        {
            "id": "meme_005",
            "phrase": "هبلتونا يا خويا",
            "arabizi": "hbaltouna ya khoya",
            "meaning": "تعبير عن نفاد الصبر أو الذهول من كثرة الشائعات أو الطلبات الغريبة.",
            "tone": "exasperated",
            "context": "تُستخدم في التعليقات الساخرة وفي خدمة العملاء عند مواقف الاستغراب."
        },
        {
            "id": "meme_006",
            "phrase": "تيكي تاكا",
            "arabizi": "tiki taka",
            "meaning": "تنسيق سلس وسريع ودقيق للأمور، مستعارة من كرة القدم لتعني إنجاز العمل دون تعقيد.",
            "tone": "enthusiastic",
            "context": "تُقال عند تسليم طلبيات سريعة أو إتمام معاملة تجارية في وقت قياسي."
        },
        {
            "id": "meme_007",
            "phrase": "سلعة لوز",
            "arabizi": "sl3a louz",
            "meaning": "وصف شعبي تجاري فائق الجودة؛ السلعة نقية وممتازة وأصلية مثل حبات اللوز الصافية.",
            "tone": "commercial_praise",
            "context": "شعار التجار الجزائريين في واد كنيس وفيسبوك لمدح المنتجات الممتازة."
        },
        {
            "id": "meme_008",
            "phrase": "كليتو لبلاد يا السراقين",
            "arabizi": "klitou leblad ya serra9ine",
            "meaning": "تريند وميم شعبي متداول عند الغضب من الغلاء أو الاحتيال أو الرداءة في الخدمة.",
            "tone": "protest_satire",
            "context": "يظهر في شكاوى الزبائن الغاضبين أو كتعليق ساخر على الغلاء."
        },
        {
            "id": "meme_009",
            "phrase": "الفايدة والحاصل",
            "arabizi": "el fayda w el 7assel",
            "meaning": "المحصلة النهائية وخلاصة الحديث وزبدة الموضوع دون إطالة.",
            "tone": "decisive",
            "context": "تُستخدم للوصول إلى النقطة الجوهرية في الاتفاقات التجارية."
        },
        {
            "id": "meme_010",
            "phrase": "صدمة كبيرة",
            "arabizi": "sadma kbira",
            "meaning": "ميم فيروسي يعبر عن المفاجأة والذهول غير المتوقع من موقف أو نتيجة أو سعر.",
            "tone": "viral_humor",
            "context": "تريند استُعمل في آلاف مقاطع الفيديو الساخرة والمقارنات."
        },
        {
            "id": "meme_011",
            "phrase": "كودار",
            "arabizi": "koudar",
            "meaning": "شخص صلب وعنيد وثابت على موقفه لا يتزحزح بسهولة، كالحجر أو الصخرة.",
            "tone": "character_trait",
            "context": "وصف شعبي للشخص الصلب أو التاجر الذي لا ينزل في السعر بسهولة."
        },
        {
            "id": "meme_012",
            "phrase": "دزاير يا العالية",
            "arabizi": "dzayer ya l3alia",
            "meaning": "نداء وافتخار وطني عميق بالجزائر وشعبها في المناسبات الرياضية والوطنية الكبرى.",
            "tone": "patriotic",
            "context": "في الاحتفالات وإنجازات الشباب الجزائري والتضامن الوطني."
        },
        {
            "id": "meme_013",
            "phrase": "يا راجل كولشي مريڤل",
            "arabizi": "ya rajel koulchi mreguel",
            "meaning": "عبارة طمأنة شعبية مريحة تعني: 'لا تقلق على الإطلاق، كل الأمور تحت السيطرة ومجهزة'.",
            "tone": "reassuring",
            "context": "تُستخدم يومياً في التجارة لإراحة الزبون بشأن طلبيته وتوصيلها."
        },
        {
            "id": "meme_014",
            "phrase": "خلطها تصفى",
            "arabizi": "khalatha tesfa",
            "meaning": "تعبير حركي يعني خوض التحديات والمغامرة دون تردد، لأن الأمور ستستقر وتتضح بالعمل.",
            "tone": "adventurous",
            "context": "تُقال عند بدء مشروع جديد أو اتخاذ قرار جريء."
        },
        {
            "id": "meme_015",
            "phrase": "زوخي يا نوارة",
            "arabizi": "zoukhi ya nouara",
            "meaning": "تعبير ساخر يوجه لمن يتفاخر ويتباهى بنجاحه أو بمظهره أمام الآخرين.",
            "tone": "teasing",
            "context": "ممازحة بين الأصدقاء عند التباهي بسيارة أو هاتف جديد."
        }
    ],

    # ================= 3. LANDMARKS, MARKETS & HISTORIC PLACES (الأماكن والأسواق والمعالم) =================
    "landmarks": [
        {
            "id": "lmk_001",
            "name": "مقام الشهيد (نصب رياض الفتح)",
            "city": "الجزائر العاصمة",
            "wilaya_code": 16,
            "category": "monument",
            "description": "المعلم التذكاري التاريخي الأبرز بالجزائر، يخلد تضحيات شهداء الثورة التحريرية ويطل على خليج العاصمة."
        },
        {
            "id": "lmk_002",
            "name": "حي القصبة العتيقة",
            "city": "الجزائر العاصمة",
            "wilaya_code": 16,
            "category": "heritage",
            "description": "المدينة التاريخية المحصنة المصنفة تراثاً عالمياً لليونسكو بأزقتها الضيقة وسلالمها وأبوابها الخشبية الأصيلة."
        },
        {
            "id": "lmk_003",
            "name": "ساحة الشهداء وباب الواد",
            "city": "الجزائر العاصمة",
            "wilaya_code": 16,
            "category": "quarter",
            "description": "قلب الجزائر النابض بالحركة الشعبية والتاريخ الوطني، ومحطة التقاء تجارة التجزئة والمقاهي العريقة."
        },
        {
            "id": "lmk_004",
            "name": "سيدي الهواري وحصن سانتا كروز",
            "city": "وهران",
            "wilaya_code": 31,
            "category": "heritage",
            "description": "الحي العتيق لوهران الباهية وحصن سانتا كروز الشامخ فوق جبل مرجاجو المشرف على خليج وهران والمرسى الكبير."
        },
        {
            "id": "lmk_005",
            "name": "جسور قسنطينة المعلقة (سيدي راشد وصالح باي)",
            "city": "قسنطينة (سيرتا)",
            "wilaya_code": 25,
            "category": "monument",
            "description": "أشهر الجسور المعلقة في إفريقيا والعالم العربي فوق وادي الرمال، تمنح قسنطينة لقبها الخالد 'مدينة الجسور المعلقة'."
        },
        {
            "id": "lmk_006",
            "name": "عين الفوارة وشارع 8 ماي",
            "city": "سطيف",
            "wilaya_code": 19,
            "category": "landmark",
            "description": "الرمز التاريخي والروحي لمدينة سطيف العالي، ونافورتها الشهيرة التي تتوسط مركز النشاط والمدينة."
        },
        {
            "id": "lmk_007",
            "name": "كنيسة القديس أوغسطين وتلة بونة",
            "city": "عنابة",
            "wilaya_code": 23,
            "category": "heritage",
            "description": "المعلم التاريخي الشهير في لالا بونة (عنابة)، والمطل على خليج هيبون وشواطئ سرايدي الخلابة."
        },
        {
            "id": "lmk_008",
            "name": "جبال جرجرة وتيكجدة",
            "city": "البويرة / تيزي وزو",
            "wilaya_code": 10,
            "category": "nature",
            "description": "القمم الجبلية الشامخة بغابات الأرز والثلج ومحميات المحيط الحيوي للرياضات الجبلية والسياحة البيئية."
        },
        {
            "id": "lmk_009",
            "name": "واحة وقصر تاغيت العتيق",
            "city": "بني عباس / بشار",
            "wilaya_code": 52,
            "category": "desert_wonder",
            "description": "عروس الصحراء الغربية بكثبانها الرملية الذهبية الشاهقة والنقوش الصخرية التي تعود لآلاف السنين."
        },
        {
            "id": "lmk_010",
            "name": "جبال الهقار والأتاكور",
            "city": "تمنراست",
            "wilaya_code": 11,
            "category": "desert_wonder",
            "description": "موطن قمة تاهات أتاكور أعلى قمة في الجزائر ومحطة أروع غروب وشروق شمس على وجه الأرض في أسكرام."
        },
        {
            "id": "lmk_011",
            "name": "طاسيلي ناجر والكهوف الصخرية",
            "city": "جانت / إليزي",
            "wilaya_code": 56,
            "category": "unesco_park",
            "description": "أكبر متحف طبيعي مفتوح للنقوش الصخرية التي توثق الحضارات القديمة والصحراء الخضراء عبر العصور."
        },
        {
            "id": "lmk_012",
            "name": "قصور وادي ميزاب الخمسة",
            "city": "غرداية",
            "wilaya_code": 47,
            "category": "heritage",
            "description": "الهندسة المعمارية الفريدة لقصور ميزاب المصنفة عالمياً بنظام توزيع المياه والتكافل الاجتماعي التاريخي."
        },
        {
            "id": "lmk_013",
            "name": "سوق دبي بالجملة بالعلمة",
            "city": "العلمة (سطيف)",
            "wilaya_code": 19,
            "category": "market",
            "description": "أكبر قطب تجاري لبيع الأجهزة الكهرومنزلية والإلكترونيات والألبسة بالجملة في الجزائر وشمال إفريقيا."
        },
        {
            "id": "lmk_014",
            "name": "سوق بلفور للإلكترونيات والهواتف",
            "city": "الحراش (الجزائر العاصمة)",
            "wilaya_code": 16,
            "category": "market",
            "description": "البورصة الوطنية الأولى لتجارة الهواتف الذكية ومستلزمات الحواسيب والصيانة التقنية في الجزائر."
        },
        {
            "id": "lmk_015",
            "name": "سوق بودربالة بالبليدة",
            "city": "البليدة",
            "wilaya_code": 9,
            "category": "market",
            "description": "السوق الشعبي العريق في مدينة الورود لتجارة الأقمشة والملابس والمستلزمات المنزلية."
        },
        {
            "id": "lmk_016",
            "name": "سوق الرحبة للبهارات والتوابل",
            "city": "قسنطينة",
            "wilaya_code": 25,
            "category": "market",
            "description": "أقدم سوق للأعشاب والبهارات التقليدية ورأس الحانوت والورد المقطر في الشرق الجزائري."
        },
        {
            "id": "lmk_017",
            "name": "سوق كاسطور للألبسة والأحذية",
            "city": "وهران",
            "wilaya_code": 31,
            "category": "market",
            "description": "أشهر أسواق التجزئة والحركية الشبابية للموضة وسلع الكابا في الباهية وهران."
        }
    ],

    # ================= 4. GASTRONOMY, DISHES & SWEETS (المطبخ والأكلات والحلويات الجزائرية) =================
    "gastronomy": [
        {
            "id": "food_001",
            "name": "الكسكسي الجزائري (الطعام)",
            "arabizi": "couscous / ta3am",
            "category": "main_dish",
            "origin": "PAN_ALGERIAN",
            "description": "الطبق الوطني الأول بالسميد المفتول باليد والمرقة الحمراء أو البيضاء، يُقدم مع لحم الخروف أو الدجاج والخضار الموسمية ووجبة الجمعة والأفراح."
        },
        {
            "id": "food_002",
            "name": "الرشتة العاصمية",
            "arabizi": "rechta algéroise",
            "category": "main_dish",
            "origin": "CENTER",
            "description": "رقائق عجين حريري مطبوخة على البخار مع مرقة بيضاء بالقرفة واللفت والحمص ولحم الدجاج، سيدة المناسبات العاصمية."
        },
        {
            "id": "food_003",
            "name": "الشخشوخة البسكرية",
            "arabizi": "chakhchoukha biskria",
            "category": "main_dish",
            "origin": "SOUTH_EAST",
            "description": "رقائق خبز الفطير المقطع المغموس في مرقة حمراء حارة جداً ومبهرة برأس الحانوت والفلفل الحار واللحم."
        },
        {
            "id": "food_004",
            "name": "الكرانتيكا / الكاران (الحامي)",
            "arabizi": "karantika / carane",
            "category": "street_food",
            "origin": "WEST_ORAN",
            "description": "أشهر أكلة شعبية في الشارع الجزائري، مخبوزة بطحين الحمص والبيض والكمون، تؤكل ساخنة في خبز الباغيت مع الهريسة والبارد."
        },
        {
            "id": "food_005",
            "name": "الدوبارة البسكرية",
            "arabizi": "doubara biskria",
            "category": "street_food",
            "origin": "SOUTH_BISKRA",
            "description": "حمص أو فول مغلى ومتبل بخلطة سحرية من الطماطم الطازجة، الثوم، الفلفل الأخضر الحار، وزيت الزيتون والكمون."
        },
        {
            "id": "food_006",
            "name": "المحاجب الحارين",
            "arabizi": "mhadjeb 7arrine",
            "category": "street_food",
            "origin": "PAN_ALGERIAN",
            "description": "فطائر سميد مورقة ومقرمشة محشوة بتكتوكة البصل والطماطم والحرور الحار، معشوقة الجماهير في كل الفصول."
        },
        {
            "id": "food_007",
            "name": "البوراك الجزائري",
            "arabizi": "bourek dziri",
            "category": "appetizer",
            "origin": "PAN_ALGERIAN",
            "description": "أوراق الديول المقرمشة المحشوة باللحم المفروم والبصل والمعدنوس والجبن والبطاطا، نجم مائدة الإفطار في رمضان."
        },
        {
            "id": "food_008",
            "name": "شوربة فريك",
            "arabizi": "chorba frik",
            "category": "soup",
            "origin": "PAN_ALGERIAN",
            "description": "الحساء الرمضاني الأصيل المحضر بالفريك الأخضر المشوي والمرقة الحمراء المعطرة بالكزبرة والنعناع واللحم."
        },
        {
            "id": "food_009",
            "name": "طاجين الزيتون",
            "arabizi": "tajine ezzitoun",
            "category": "main_dish",
            "origin": "PAN_ALGERIAN",
            "description": "طبق تقليدي أنيق من حبات الزيتون الأخضر منزوع الملوحة المطهو بمرقة مرطبة مع الجزر والدجاج أو كرات اللحم."
        },
        {
            "id": "food_010",
            "name": "طاجين الحلو (لحم لحلو)",
            "arabizi": "tajine la7lou",
            "category": "festive_dish",
            "origin": "PAN_ALGERIAN",
            "description": "طبق احتفالي فاخر يجمع بين البرقوق والمشمش المجفف والزبيب واللوز وماء الزهر، يُقدم فأل خير في الأعراس وبداية رمضان."
        },
        {
            "id": "food_011",
            "name": "قلب اللوز (الشامية)",
            "arabizi": "9elb el louz / chamia",
            "category": "traditional_sweet",
            "origin": "CENTER_WEST",
            "description": "سيد الحلويات الرمضانية بالسميد الخشن والمحشو باللوز والمشرب بالشاربات المعطرة بماء الزهر المقطر."
        },
        {
            "id": "food_012",
            "name": "مقروط العسل (مقروط الكوشة ومقروط المقلة)",
            "arabizi": "maqrout el 3ssal",
            "category": "traditional_sweet",
            "origin": "PAN_ALGERIAN",
            "description": "الحلوى الملكية الجزائرية بالسميد المرمّل المحشو بالغرس (عجينة التمر) أو اللوز والمعسل بعسل النحل الطبيعي."
        },
        {
            "id": "food_013",
            "name": "تشاراك المسكر وتشاراك العريان",
            "arabizi": "tcharek msekar",
            "category": "traditional_sweet",
            "origin": "CENTER_ALGIERS",
            "description": "هلاليات العيد الفاخرة المحشوة بعقدة اللوز والمغطاة بطبقة ناعمة من السكر الصقيل تذوب في الفم."
        },
        {
            "id": "food_014",
            "name": "الطمينة الجزائرية",
            "arabizi": "tamina dziria",
            "category": "festive_sweet",
            "origin": "PAN_ALGERIAN",
            "description": "حلوى البشارة بالمولود الجديد واحتفالات المولد النبوي بالسميد المحمص الدافئ والزبدة والعسل والقرفة واللوز."
        },
        {
            "id": "food_015",
            "name": "المطبقة الصحراوية (خبز الشحم)",
            "arabizi": "metbegua sahraouia",
            "category": "street_food",
            "origin": "SOUTH_ELOUED",
            "description": "فطائر صحراوية محشوة بخلطة غنية من البصل، الشحم المفروم، التوابل الصحراوية، والأعشاب البرية العطرية."
        }
    ]
}

def main():
    root = Path(__file__).resolve().parent.parent
    data_dir = root / "data"
    out_file = data_dir / "culture.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(CULTURE_DATA, f, ensure_ascii=False, indent=2)

    total_proverbs = len(CULTURE_DATA["proverbs"])
    total_memes = len(CULTURE_DATA["memes_and_trends"])
    total_landmarks = len(CULTURE_DATA["landmarks"])
    total_food = len(CULTURE_DATA["gastronomy"])
    total_all = total_proverbs + total_memes + total_landmarks + total_food

    print(f"Generated {total_all} cultural records in {out_file.relative_to(root)}:")
    print(f"  - Proverbs: {total_proverbs}")
    print(f"  - Memes & Trends: {total_memes}")
    print(f"  - Landmarks & Markets: {total_landmarks}")
    print(f"  - Gastronomy & Sweets: {total_food}")

if __name__ == "__main__":
    main()
