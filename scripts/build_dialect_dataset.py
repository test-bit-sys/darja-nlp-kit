"""
Script to build comprehensive, verified dialogues.json dataset
representing authentic multi-dialect Algerian e-commerce interactions.
"""
import json
from pathlib import Path

DIALOGUES = [
    # ================= WEST (الوهراني، التلمساني، المستغانمي، العباسي) =================
    {
        "id": "west_001",
        "region": "WEST",
        "domain": "footwear",
        "intent": "PRICE_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "salam khoya kirak ghaya, chwala souma ta3 had sberdina noir pointure 43?",
        "merchant_response": "الله يسلمك خويا العزيز، غايا ربي يحفظك. هاديك السبردينة سومتها 5,800 دج والسلعة كابا أصلية، وبوانتير 43 راهي واجدة درك في النوار.",
        "entities": {"category": "سبردينة", "color": "نوار", "size": "43", "price_dzd": 5800},
        "notes": "Authentic Oranais phrasing (kirak ghaya, chwala, sberdina, drk)."
    },
    {
        "id": "west_002",
        "region": "WEST",
        "domain": "electronics",
        "intent": "ORDER",
        "sentiment": "POSITIVE",
        "customer_message": "خويا باغي نكوموندي زوج حبات كيت بلوتوث لوهران درك، شحال يحسبهملي؟",
        "merchant_response": "مرحبا بيك خويا في وهران الباهية! زوج حبات نحسبهملك 4,400 دج مع توصيل مجاني للمكتب ياليدين. صايي ابعثلي اسمك ورقم الهاتف ونفاليديهملك درك.",
        "entities": {"wilaya": "وهران (31)", "quantity": 2, "unit": "حبات", "price_dzd": 4400},
        "notes": "Western vocab: باغي، درك، صايي، وهران الباهية."
    },
    {
        "id": "west_003",
        "region": "WEST",
        "domain": "clothing",
        "intent": "AVAILABILITY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "شاكاين لي كولور فهاد تريكو أوفرسايز؟ باغي كولور بلون ونوار طاي L",
        "merchant_response": "أهلا خويا الغالي، كاينين في زوج: البلون والنوار في الطاي L راهي متوفرة درك قطن 100%. إلا راك باغي نريڤلوهملك في طلبيتك.",
        "entities": {"colors": ["بلون", "نوار"], "size": "L", "item": "تريكو"},
        "notes": "Western marker: شاكاين، باغي، درك."
    },
    {
        "id": "west_004",
        "region": "WEST",
        "domain": "general",
        "intent": "BARGAINING",
        "sentiment": "NEUTRAL",
        "customer_message": "خويا ديرلي سومة مليحة راني باغي ندي 3 حبات، ساعدني شوي ربي يحفظك طليت عليك",
        "merchant_response": "على الراس وبلا مزية خويا! على خاطر راك داي 3 حبات نديرلك لافان ونحسبهملك بـ 7,500 دج في بلاصة 9,000 دج، وتوصيل ياليدين عليا.",
        "entities": {"quantity": 3, "discount_offered": True, "price_dzd": 7500},
        "notes": "Western warmth: بلا مزية، طليت عليك، باغي، لافان."
    },
    {
        "id": "west_005",
        "region": "WEST",
        "domain": "dispute",
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "customer_message": "chwala hadi sl3a kaba wla chinwa? hrez tbi3li haja mfer3sa khoya rani nchouf la semelle mafihach ga3 finition!",
        "merchant_response": "حقك علينا خويا العزيز وحرز تتقلق، سلعتنا كابا مضمونة وادا لقيت فيها أدنى مشكل رانا هنا نرجعولك دراهمك ولا نبدلوهالك درك وبلا مزية. ابعثلي تصويرة ورقم الطلب.",
        "entities": {"complaint_type": "defect", "urgency": "HIGH"},
        "notes": "Western complaint: chwala, hrez, mfer3sa, ga3, بلا مزية."
    },
    {
        "id": "west_006",
        "region": "WEST",
        "domain": "clothing",
        "intent": "DELIVERY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "خويا صايي راني عاقل هاديك لفيستا، كاين لافريزون لتلمسان سطوب ديسك وشحال تدي وقت؟",
        "merchant_response": "مرحبا بالناس الزينين في تلمسان! واه خويا كاين توصيل سطوب ديسك ياليدين بـ 350 دج برك، توصلك في 24 إلى 48 ساعة درك نبعثوهالك.",
        "entities": {"wilaya": "تلمسان (13)", "delivery_mode": "STOP_DESK", "carrier": "Yalidine", "delivery_dzd": 350},
        "notes": "Western markers: صايي، راني عاقل، واه، درك."
    },
    {
        "id": "west_007",
        "region": "WEST",
        "domain": "logistics",
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "customer_message": "راني نستنى فكوليتي عند ياليدين وهران حي مطلع الفجر من يومين وماعيطوليش، شوفلي شا كاين درك",
        "merchant_response": "ما تقلقش روحك خويا درك نتاصل بمسؤول ياليدين وهران ونعطيك رقم التتبع حالا. حقك محفوظ وخويا ما يروحش غضبان إطلاقاً.",
        "entities": {"wilaya": "وهران (31)", "carrier": "Yalidine", "urgency": "HIGH"},
        "notes": "Western escalation: شا كاين، درك، ما تقلقش روحك."
    },
    {
        "id": "west_008",
        "region": "WEST",
        "domain": "tech",
        "intent": "AVAILABILITY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "salam alikom, baghi nchouf ila mazal kayen charjeur type c 65w d origine w chhal lafin?",
        "merchant_response": "وعليكم السلام خويا الغالي، واه مازال متوفر أصلي 100% مع ضمان 6 أشهر. السومة للخر نحسبهالك بـ 2,800 دج. صايي ادا باغي احجز حبتك.",
        "entities": {"item": "شاحن", "price_dzd": 2800, "specs": "65W Type-C"},
        "notes": "Western Arabizi: baghi, chhal lafin, wah, sayi."
    },
    {
        "id": "west_009",
        "region": "WEST",
        "domain": "cosmetics",
        "intent": "ORDER",
        "sentiment": "POSITIVE",
        "customer_message": "كيراك خويا غايا، اديني قرعة ريحة سوفاج لمستغانم، هاك نومرو 0771234567 والاسم عبد القادر",
        "merchant_response": "الله يحفظك أخ عبد القادر ومرحب بيك وبكل ناس مستغانم الحبيبة! طلبيتك تسجلت، العطر أصلي ويوصلك بعد غدوا ان شاء الله وبلا مزية.",
        "entities": {"customer_name": "عبد القادر", "phone": "0771234567", "operator": "Djezzy", "wilaya": "مستغانم (27)"},
        "notes": "Western order confirmation: كيراك غايا، بلا مزية."
    },
    {
        "id": "west_010",
        "region": "WEST",
        "domain": "footwear",
        "intent": "ORDER",
        "sentiment": "NEUTRAL",
        "customer_message": "chakayn jdid f les baskets? baghi haja mliha l sidi bel abbes pointure 42",
        "merchant_response": "مرحبا بيك وبناس بلعباس! كاين موديلات جدد سلعة كابا هبال، درك نبعثلك الكتالوج في التيليغرام ولا الواتساب تختار لي يعجبك خويا.",
        "entities": {"wilaya": "سيدي بلعباس (22)", "size": "42"},
        "notes": "chakayn, baghi, sidi bel abbes."
    },
    {
        "id": "west_011",
        "region": "WEST",
        "domain": "general",
        "intent": "GREETING",
        "sentiment": "POSITIVE",
        "customer_message": "شراكم يا ناس الكرم، كيراكم مع السلعة الجديدة؟ طليت نسلم برك",
        "merchant_response": "يسلمك ويحفظك خويا العزيز، غايا الحمد لله ربي يعزك وطليت عليك البركة والخير! رانا ديما في الخدمة وكاش ما تسحق راك في دارك.",
        "entities": {},
        "notes": "شراكم، كيراكم، طليت نسلم، غايا."
    },
    {
        "id": "west_012",
        "region": "WEST",
        "domain": "automotive",
        "intent": "PRICE_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "chwala souma ta3 vidange castrol 5w40 w ida 3andkom filtre a huile l clio 4 f oran?",
        "merchant_response": "مرحبا خويا، بيدون كاسترول 5w40 دوريجين يدير 6,200 دج والفيلتر 900 دج، وعندنا التوصيل في وهران حتى لباب دارك درك.",
        "entities": {"wilaya": "وهران (31)", "price_dzd": 6200},
        "notes": "chwala, oran, drk."
    },

    # ================= EAST (القسنطيني، السطايفي، العنابي، الباتني) =================
    {
        "id": "east_001",
        "region": "EAST",
        "domain": "clothing",
        "intent": "PRICE_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "عيشك خويا قداش السومة تاع هاد لفيستا الكحلة؟ وكاش مساعدة على هاد السعر؟",
        "merchant_response": "يعيشك خويا العزيز ومرحبا بيك! السومة تاع لفيستا راهي 7,200 دج والسلعة باهية خلاص كابا تركية. وادا شريت نساعدك على عيني ونديرلك 6,800 دج.",
        "entities": {"category": "فيستا", "color": "كحلة", "price_dzd": 6800},
        "notes": "Eastern markers: عيشك، قداش، باهية خلاص، على عيني."
    },
    {
        "id": "east_002",
        "region": "EAST",
        "domain": "logistics",
        "intent": "DELIVERY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "salam 3aychek khoya, 9dach livrison l constantine bureau yalidine w 9dach te93od?",
        "merchant_response": "وعليكم السلام ويعيشك خويا، مرحبا بناس سيرتا العريقة! التوصيل لمكتب ياليدين قسنطينة يدير 300 دج برك، وتوصلك في 24 ساعة بإذن الله.",
        "entities": {"wilaya": "قسنطينة (25)", "alias": "سيرتا", "carrier": "Yalidine", "delivery_dzd": 300},
        "notes": "Eastern Arabizi: 3aychek, 9dach, constantine, سيرتا."
    },
    {
        "id": "east_003",
        "region": "EAST",
        "domain": "footwear",
        "intent": "AVAILABILITY_INQUIRY",
        "sentiment": "POSITIVE",
        "customer_message": "خويا باهي السلعة باينة حطة، كاين بوانتير 42 في الكحلة؟ راني باغي نشري ضرك لسطيف",
        "merchant_response": "الله يبارك فيك خويا ويعيشك! بوانتير 42 في النوار كاين واجد، نهارين ويكون في سطيف العالي. ابعثلي العنوان ورقم الهاتف ونسجلوهالك على عيني.",
        "entities": {"wilaya": "سطيف (19)", "size": "42", "color": "كحلة / نوار"},
        "notes": "Eastern markers: باهي، عيشك، ضرك، على عيني، سطيف العالي."
    },
    {
        "id": "east_004",
        "region": "EAST",
        "domain": "dispute",
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "customer_message": "واشنهي هاد السلعة مكسرة وصلاتني؟ راني نرجعها ضروك ولا نعيط لحماية المستهلك ونبهدلكم!",
        "merchant_response": "حقك على عيني وراسي خويا وما يكون غير خاطرك طيب! متأسفين ياسر على هاد الخطأ، السلعة نبدلوهالك ضرك بوحدة جديدة ومصاريف الإرجاع كاملة علينا. ربي يهديك ويهدينا وما تقلقش خلاص.",
        "entities": {"escalation": True, "urgency": "CRITICAL", "reason": "LEGAL_THREAT"},
        "notes": "Eastern escalation: واشنهي، ضروك، على عيني وراسي، ياسر، خلاص."
    },
    {
        "id": "east_005",
        "region": "EAST",
        "domain": "customer_service",
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "customer_message": "وشبيك خويا عيطتلكم ياسر وما رديتوش، راني نستنى فلكولي في عنابة من الصباح وما جاني حتى ميساج!",
        "merchant_response": "يعيشك خويا ونعتذروا منك ياسر على التأخير بسبب ضغط المكالمات. كوليك في عنابة راهو مع ليفرور ويوصلك قبل العصر، درك نبعثلو ينبهك.",
        "entities": {"wilaya": "عنابة (23)", "urgency": "HIGH"},
        "notes": "Eastern dialect: وشبيك، عيشك، ياسر، درك."
    },
    {
        "id": "east_006",
        "region": "EAST",
        "domain": "general",
        "intent": "BARGAINING",
        "sentiment": "NEUTRAL",
        "customer_message": "عيشك خويا ديرلي فيها سومة باهية راني زبون قديم وداي 4 حبات، قداش تحسبهملي ماللخر؟",
        "merchant_response": "على عيني وراسي زبوننا الوفي! على خاطر راك داي 4 حبات نقصلك 500 دج في الحبة، وتوصيل عنابة باطل. هكدا مليح ويعيشك؟",
        "entities": {"quantity": 4, "discount": True},
        "notes": "عيشك، باهية، قداش، على عيني وراسي."
    },
    {
        "id": "east_007",
        "region": "EAST",
        "domain": "traditional",
        "intent": "AVAILABILITY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "يعيشك أختي كاين قندورة عنابية مطروزة طاي 44 فالغوج كاشمير؟ و قداش تقعد للباتنة؟",
        "merchant_response": "أهلا وسهلا بيك أختي العزيزة، كاين قندورة عنابية حرة مطروزة يد في الطاي 44. التوصيل لباتنة يومين برك وتكون عندك عند ياليدين.",
        "entities": {"wilaya": "باتنة (5)", "item": "قندورة عنابية", "size": "44", "color": "غوج كاشمير"},
        "notes": "Eastern culture: يعيشك، قندورة، قداش، باتنة."
    },
    {
        "id": "east_008",
        "region": "EAST",
        "domain": "logistics",
        "intent": "ORDER",
        "sentiment": "POSITIVE",
        "customer_message": "salam khoya bahi bzf, 3andkom livrison l skikda a domicile wla stop desk? hawli num 0660445566",
        "merchant_response": "وعليكم السلام ويعيشك خويا، كاين لزوج في سكيكدة: للدار بـ 550 دج وللمكتب بـ 300 دج. درك نتصلوا بيك في موبيليس ونأكدوا كل التفاصيل.",
        "entities": {"wilaya": "سكيكدة (21)", "phone": "0660445566", "operator": "Mobilis"},
        "notes": "bahi bzf, 3aychek, skikda, stop desk."
    },
    {
        "id": "east_009",
        "region": "EAST",
        "domain": "food",
        "intent": "PRICE_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "قداش يدير كيلو قهوة مخلطة أصلية كولومبي؟ وهل كاين توصيل لقالمة ضرك؟",
        "merchant_response": "مرحبا بخويا وبأهل قالمة الكرام! الكيلو يدير 2,200 دج تحميص طازج، ونبعثوهالك ضرك وتوصلك بعد غدوا الصباح بإذن الله.",
        "entities": {"wilaya": "قالمة (24)", "price_dzd": 2200, "item": "قهوة"},
        "notes": "قداش، قالمة، ضرك."
    },
    {
        "id": "east_010",
        "region": "EAST",
        "domain": "general",
        "intent": "GREETING",
        "sentiment": "POSITIVE",
        "customer_message": "صباح الورد خويا باهي واش حالك واش راك مع هاد البرد في قسنطينة؟",
        "merchant_response": "صباح النور والسرور خويا الغالي ويعيشك! رانا لاباس ربي يدوم فضلك وسيرتا ديما باردة بصح قلوب ناسها دافية. واش كاش ما نعاونوك اليوم؟",
        "entities": {"wilaya": "قسنطينة (25)"},
        "notes": "باهي واش حالك، يعيشك، سيرتا."
    },

    # ================= CENTER (العاصمي، البليدي، البومرداسي، التيبازي) =================
    {
        "id": "center_001",
        "region": "CENTER",
        "domain": "footwear",
        "intent": "AVAILABILITY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "واش خويا لعزيز واش راك، كولشي مريڤل؟ حبيت نسقسي على هاد السبردينة كاين بوانتير 41 فلكحل؟",
        "merchant_response": "واش خويا الغالي، الحمد لله كولشي مريڤل ربي يحفظك! السبردينة 41 في النوار راهي متوفرة حطة ما شاء الله، ادا باغي نخبيوهالك ونبعثوهالك لباب الدار في البهجة.",
        "entities": {"size": "41", "color": "كحل / نوار", "item": "سبردينة"},
        "notes": "Center dialect: واش خويا، مريڤل، حطة، البهجة."
    },
    {
        "id": "center_002",
        "region": "CENTER",
        "domain": "clothing",
        "intent": "PRICE_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "salam khoya wachnou souma ta3 had sac a dos w kach remise ida ddit zouj habat?",
        "merchant_response": "وعليكم السلام خويا العزيز! الساك يدير 3,500 دج، وادا ديت زوج نحسبهملك بـ 6,000 دج برك مع توصيل مجاني في الجزائر العاصمة.",
        "entities": {"price_dzd": 6000, "quantity": 2, "wilaya": "الجزائر (16)"},
        "notes": "wachnou, zouj habat, khoya l3aziz, remise."
    },
    {
        "id": "center_003",
        "region": "CENTER",
        "domain": "feedback",
        "intent": "GREETING",
        "sentiment": "POSITIVE",
        "customer_message": "سلعة هبال ما شاء الله حطة بزاف وصلتني اليوم للبليدة في وقتها، يعطيكم الصحة يا ليكيب!",
        "merchant_response": "الله يسترك خويا العزيز وشهادة نعتزوا بيها بزاف! ربي يفرحك وتلبسها بالصحة والهنا وكاش ما تسحق رانا هنا ديما لولاد لبلاد.",
        "entities": {"wilaya": "البليدة (9)", "sentiment_score": 0.95},
        "notes": "سلعة هبال، حطة، الله يسترك، كاش ما تسحق."
    },
    {
        "id": "center_004",
        "region": "CENTER",
        "domain": "order",
        "intent": "ORDER",
        "sentiment": "NEUTRAL",
        "customer_message": "خويا كاش ما تسحق باش تفاليدي لكوموند؟ هاوليك لادريس باب الواد الجزائر ونميرو 0661223344 حبة كحلة",
        "merchant_response": "صحيت خويا كولشي مريڤل وسجلنا كل المعلومات! غدوا الصباح تكون عندك في باب الواد مع ليفرور ويديرلك ابيل قبل ما يوصل.",
        "entities": {"wilaya": "الجزائر (16)", "commune": "باب الواد", "phone": "0661223344", "operator": "Mobilis"},
        "notes": "مريڤل، باب الواد، كاش ما تسحق، صحيت."
    },
    {
        "id": "center_005",
        "region": "CENTER",
        "domain": "logistics",
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "customer_message": "واش هاد الروطار يا خويا؟ لافريزون كانت مبرمجة لبارح لتيبازة وما شفت والو وراني مزروب بزاف!",
        "merchant_response": "حقك علينا خويا وما تتقلقش، صرا ضغط خفيف في التوزيع البارح بصح دروك كوليك راهو مع ليفرور تاع تيبازة ويكون عندك قبل 2 تاع العشية أكيد.",
        "entities": {"wilaya": "تيبازة (42)", "urgency": "HIGH"},
        "notes": "واش هاد الروطار، دروك، تيبازة."
    },
    {
        "id": "center_006",
        "region": "CENTER",
        "domain": "electronics",
        "intent": "PRICE_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "شحال يدير هاد ليكوتور ابل برو و كاش لافان فيه خويا لعزيز راني شاري دروك؟",
        "merchant_response": "خويا العزيز نحسبهولك بـ 4,900 دج سلعة برومي شوا مع كابل وضمان، ونديرلك معاه بوشيت سيليكون كادو من عندنا.",
        "entities": {"price_dzd": 4900, "item": "écouteurs"},
        "notes": "لافان، خويا لعزيز، شاري دروك."
    },
    {
        "id": "center_007",
        "region": "CENTER",
        "domain": "payment",
        "intent": "ORDER",
        "sentiment": "NEUTRAL",
        "customer_message": "خويا دروك نبعثلك ببريدي موب 4500 دج، ابعثلي ريب تاعك نفاليدي وراني في بومرداس",
        "merchant_response": "مريڤل خويا هاوليك الريب تاعنا في بريدي موب (RIP: 00799999...)، غير تبعث الروصي نخرجو الكولي لبومرداس مع ياليدين.",
        "entities": {"payment": "BARIDIMOB", "price_dzd": 4500, "wilaya": "بومرداس (35)"},
        "notes": "بريدي موب، مريڤل، بومرداس."
    },
    {
        "id": "center_008",
        "region": "CENTER",
        "domain": "delivery",
        "intent": "DELIVERY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "salam khoya kayen livraison express f dar f alger centre lyoum apres midi?",
        "merchant_response": "وعليكم السلام خويا! واه كاين إكسبريس للدار في العاصمة كاملة بـ 400 دج، نهارك اليوم يكون عندك قبل 18:00.",
        "entities": {"wilaya": "الجزائر (16)", "commune": "الجزائر الوسطى", "delivery_mode": "DOMICILE", "delivery_dzd": 400},
        "notes": "express, alger centre, lyoum."
    },

    # ================= SOUTH (الصحراوي، البسكري، الورقلي، الغرداوي، الوادي) =================
    {
        "id": "south_001",
        "region": "SOUTH",
        "domain": "footwear",
        "intent": "DELIVERY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "مرحب بيك خويا وعلى الراس والعين، واش حال هاد السلعة توصل لبسكرة وبشحال سومة التوصيل؟",
        "merchant_response": "أهلا وسهلا بناس بسكرة النخلة والخير! التوصيل لبسكرة يدير 400 دج للمكتب و650 دج لباب داركم، ويوصلكم في ظرف 48 ساعة على الراس والعين.",
        "entities": {"wilaya": "بسكرة (7)", "delivery_dzd": 400},
        "notes": "Southern dialect: مرحب بيك، على الراس والعين، واش حال."
    },
    {
        "id": "south_002",
        "region": "SOUTH",
        "domain": "electronics",
        "intent": "ORDER",
        "sentiment": "POSITIVE",
        "customer_message": "salam alikom khoya, wah baghi nchri had lproduit l ouargla bureau yalidine w hawli num 0670112233",
        "merchant_response": "وعليكم السلام ورحمة الله خويا العزيز! على الراس والعين مرحب بيك وبكل أهل ورقلة الكرام. طلبيتك راهي مسجلة وبإذن الله توصلك سالمة غانمة.",
        "entities": {"wilaya": "ورقلة (30)", "phone": "0670112233", "operator": "Mobilis"},
        "notes": "Southern markers: wah, ouargla, على الراس والعين."
    },
    {
        "id": "south_003",
        "region": "SOUTH",
        "domain": "feedback",
        "intent": "GREETING",
        "sentiment": "POSITIVE",
        "customer_message": "بارك الله فيك خويا سلعة زينة بزاف ما شاء الله وربي يباركلك في رزقك وتجارتك على المصداقية",
        "merchant_response": "وفيك بارك الله وجازاك الله كل خير خويا الغالي! شهادتك تاج فوق راسنا، وربي يحفظ أهل الجنوب الكرماء اللي نفتخروا بخدمتهم ديما.",
        "entities": {"sentiment_score": 0.98},
        "notes": "بارك الله فيك، سلعة زينة، ربي يباركلك."
    },
    {
        "id": "south_004",
        "region": "SOUTH",
        "domain": "general",
        "intent": "BARGAINING",
        "sentiment": "NEUTRAL",
        "customer_message": "خويا لاه السومة زايدة ياسر للصحراء؟ ديرلنا سومة زينة ربي يجازيك كل خير رانا شاريين",
        "merchant_response": "على عينينا خويا وما يكون غير خاطرك طيب! مصاريف الشحن حنا نتحملو نصها ونديرولك سومة زينة تعجبك بزاف، ربي يبارك فيك وفي رزقك.",
        "entities": {"discount": True},
        "notes": "لاه، سومة زينة، ربي يجازيك."
    },
    {
        "id": "south_005",
        "region": "SOUTH",
        "domain": "traditional",
        "intent": "PRICE_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "مرحب بيك خويا، كاين عباية رجالي قماش صيفي وبشحال السومة دينار لغرداية؟",
        "merchant_response": "مرحب بيك خويا العزيز وعلى الراس والعين! كاين عبايات قماش صيفي رفيع يديرو 4,800 دج والتوصيل لغرداية متوفر مع ياليدين.",
        "entities": {"wilaya": "غرداية (47)", "price_dzd": 4800, "item": "عباية"},
        "notes": "مرحب بيك، غرداية، على الراس والعين."
    },
    {
        "id": "south_006",
        "region": "SOUTH",
        "domain": "dispute",
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "customer_message": "خويا لاه هاد الروطار؟ راني نستنى في الوادي أسبوع كامل والكولي ما وصلش، شوفلنا حل ربي يحفظك!",
        "merchant_response": "حقك علينا خويا العزيز ولاه نرضاو بتعطيلك أبدا! فتحنا شكوى عاجلة لمدير مركز الوادي ودرك نتبعولك الشحنة حتى توصل ليدك سالمة ومعوضين ان شاء الله.",
        "entities": {"wilaya": "الوادي (39)", "urgency": "HIGH"},
        "notes": "لاه، الوادي، ربي يحفظك."
    },
    {
        "id": "south_007",
        "region": "SOUTH",
        "domain": "appliances",
        "intent": "AVAILABILITY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "salam khoya wah kayen climatiseur tropicalisé l adrar w chhal la livraison?",
        "merchant_response": "وعليكم السلام خويا الغالي! واه متوفر كليماتيزور تروبيكال يتحمل حرارة أدرار العالية، التوصيل يدير 1,200 دج ويوصل في كوليتريكس مؤمن 100%.",
        "entities": {"wilaya": "أدرار (1)", "item": "climatiseur"},
        "notes": "wah, adrar, tropicalisé."
    },

    # ================= GENERAL_DARJA & E-COMMERCE LIFE CYCLES =================
    {
        "id": "gen_001",
        "region": "GENERAL_DARJA",
        "domain": "order",
        "intent": "ORDER",
        "sentiment": "NEUTRAL",
        "customer_message": "سلام خويا حاب نكوموندي هاد السبردينة كحلة طاي 42 توصيل للمكتب في تيزي وزو رقمي 0550112233",
        "merchant_response": "وعليكم السلام خويا مرحبا بيك! سجلنا طلبيتك: سبردينة كحلة مقاس 42 إلى مكتب ياليدين تيزي وزو. السعر الإجمالي 5,500 دج مع التوصيل.",
        "entities": {"wilaya": "تيزي وزو (15)", "size": "42", "color": "كحلة", "phone": "0550112233", "operator": "Ooredoo", "price_dzd": 5500},
        "notes": "General Darja standard order flow."
    },
    {
        "id": "gen_002",
        "region": "GENERAL_DARJA",
        "domain": "payment",
        "intent": "ORDER",
        "sentiment": "NEUTRAL",
        "customer_message": "خويا نقدر نخلص كاش كي توصلني السلعة عند الباب ولا لازم نسبق بالسي سي بي؟",
        "merchant_response": "أكيد خويا! عندنا الدفع عند الاستلام يد بيد (Paiement à la livraison)، حتى تشوف سلعتك وتفحصها باش تخلص الليفرور، وادا حبيت بالبريدي موب متوفر أيضا.",
        "entities": {"payment": "CASH_ON_DELIVERY"},
        "notes": "Paiement à la livraison reassurance."
    },
    {
        "id": "gen_003",
        "region": "GENERAL_DARJA",
        "domain": "logistics",
        "intent": "DELIVERY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "شحال يدير التوصيل لعين الدفلى لدار وشكون هي الشركة لي توصللكم؟",
        "merchant_response": "التوصيل لعين الدفلى يدير 600 دج لباب الدار و350 دج للمكتب، ونتعاملو مع شركة ياليدين إكسبريس وزد آر إكسبريس لتوصيل سريع ومضمون.",
        "entities": {"wilaya": "عين الدفلى (44)", "delivery_dzd": 600, "carriers": ["Yalidine", "ZR Express"]},
        "notes": "Clear dual delivery pricing & company mention."
    },
    {
        "id": "gen_004",
        "region": "GENERAL_DARJA",
        "domain": "dispute",
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "customer_message": "سلعتكم خردة ومفرعسة ومافيهاش قاع واش في التصويرة! راني نعيط لمديرية التجارة ونفضحكم!",
        "merchant_response": "نعتذر منك كل الاعتذار خويا، إرضاؤك أولويتنا وما نسمحوش بأي ضرر ليك. عندنا ضمان استبدال واسترجاع فوري خلال 48 ساعة، ابعثلي صورة الفاتورة ودراهمك يرجعولك كاملين درك.",
        "entities": {"escalation": True, "urgency": "CRITICAL", "reason": "LEGAL_THREAT"},
        "notes": "De-escalation protocol on angry customer."
    },
    {
        "id": "gen_005",
        "region": "GENERAL_DARJA",
        "domain": "general",
        "intent": "PRICE_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "شحال تحسبلي زوج حبات شارجور أصليين؟ كاين تخفيض؟",
        "merchant_response": "الحبة تدير 1,800 دج، وادا ديت زوج نحسبهملك بـ 3,200 دج في بلاصة 3,600 دج مع ضمان عام كامل.",
        "entities": {"quantity": 2, "price_dzd": 3200},
        "notes": "Colloquial quantity & bundle discount."
    },
    {
        "id": "gen_006",
        "region": "GENERAL_DARJA",
        "domain": "clothing",
        "intent": "AVAILABILITY_INQUIRY",
        "sentiment": "NEUTRAL",
        "customer_message": "كاين طاي 3XL فهاد لفيستا الكحلة؟ ورقم الهاتف لي نتاصل بيكم بيه واشنو هو؟",
        "merchant_response": "نعم خويا المقاس الكبير 3XL متوفر حالياً في اللون الأسود، ورقم خدمة العملاء تاعنا هو 021234567 ولا عبر الواتساب على 0550123456.",
        "entities": {"size": "3XL", "color": "كحلة / أسود", "phone": "021234567"},
        "notes": "Plus size clothing availability."
    },
    {
        "id": "gen_007",
        "region": "GENERAL_DARJA",
        "domain": "exchange",
        "intent": "COMPLAINT",
        "sentiment": "NEGATIVE",
        "customer_message": "خويا جاتني السبردينة ضيقة شوية بوانتير 41 نقدر نبدلها بـ 42؟",
        "merchant_response": "أكيد خويا وبكل سرور! الاستبدال مجاني، نبعثولك بوانتير 42 مع الليفرور ويعطيك الجديدة ويرجع القديمة بدون أي تعب.",
        "entities": {"old_size": "41", "new_size": "42"},
        "notes": "Smooth exchange handling."
    },
    {
        "id": "gen_008",
        "region": "GENERAL_DARJA",
        "domain": "general",
        "intent": "GREETING",
        "sentiment": "POSITIVE",
        "customer_message": "سلام عليكم واش راكم لباس؟ كاش سلعة جديدة دخلت هاد السمانة؟",
        "merchant_response": "وعليكم السلام خويا مرحبا بيك! الحمد لله ربي يحفظك، دخلت كوليكسيون جديدة كابا هبال في الألبسة والأحذية، ادخل للصفحة شوف أو نبعثلك الكاتالوج.",
        "entities": {},
        "notes": "Friendly general engagement."
    }
]

# Add more multi-regional dialogues programmatically to reach a solid 60-80 high-value dialogue instances
ADDITIONAL_DATA = [
    # WEST dialogues
    ("west_013", "WEST", "general", "ORDER", "NEUTRAL", "salam baghi ncommande had lmontre l tlemcen centre num ta3i 0770334455", "مرحبا بيك خويا وبناس تلمسان! المنقالة تسجلت ونبعثوهالك درك وتوصلك في 48 ساعة ان شاء الله وبلا مزية.", {"wilaya": "تلمسان (13)", "phone": "0770334455"}),
    ("west_014", "WEST", "clothing", "PRICE_INQUIRY", "NEUTRAL", "chwala souma ta3 had serwal jean noir taille 40?", "السروال راه يدير 3,200 دج وسلعة تركية ممتازة درك واجدة في النوار طاي 40.", {"item": "سروال جين", "color": "نوار", "size": "40", "price_dzd": 3200}),
    ("west_015", "WEST", "perfume", "BARGAINING", "NEUTRAL", "sa3adni chwiya f souma rani baghi nedi 2 flacons parfum l oran", "على الراس خويا! نحسبلك الزوج بـ 7,000 دج مع توصيل مجاني في وهران وبلا مزية.", {"quantity": 2, "wilaya": "وهران (31)", "price_dzd": 7000}),
    ("west_016", "WEST", "complaint", "COMPLAINT", "NEGATIVE", "chwala had retard ya khoya sl3a ta3i rahi f bureau yalidine sidi bel abbes w ma bghawch ymdouhali!", "حرز تقلق روحك خويا، درك نتصل بمدير مكتب بلعباس ونخليه يعيطلك درك وتسلم كوليك فورا.", {"wilaya": "سيدي بلعباس (22)", "urgency": "HIGH"}),
    ("west_017", "WEST", "shoes", "AVAILABILITY_INQUIRY", "NEUTRAL", "kayen pointure 44 f had claquette f mascara?", "واه متوفرة في معسكر خويا العزيز وفيها كولور كحلة ومارون حطة.", {"wilaya": "معسكر (29)", "size": "44"}),
    
    # EAST dialogues
    ("east_011", "EAST", "tech", "ORDER", "POSITIVE", "3aychek khoya b3atli charjeur anker l batna haw num 0555998877", "يعيشك خويا ومرحب بيك وبكل ناس الشاوية الكرام! طلبيتك تسجلت والشاحن الأصلي في طريقه لباتنة.", {"wilaya": "باتنة (5)", "phone": "0555998877"}),
    ("east_012", "EAST", "clothing", "PRICE_INQUIRY", "NEUTRAL", "قداش السومة تاع هاد الكاسكيطة الأصلية؟ وكاين توصيل لسطيف؟", "السومة 1,900 دج والتوصيل لسطيف العالي يدير 350 دج ويوصلك في 24 ساعة على عيني.", {"wilaya": "سطيف (19)", "price_dzd": 1900}),
    ("east_013", "EAST", "dispute", "COMPLAINT", "NEGATIVE", "واشنهي هاد الروطار يا خويا؟ كوليتي في قسنطينة راهي عندها 5 أيام!", "متأسفين ياسر خويا العزيز على هاد التأخير، درك نديروا ريكلاماسيون مستعجلة ونوصلوهالك لباب دارك باطل.", {"wilaya": "قسنطينة (25)", "urgency": "HIGH"}),
    ("east_014", "EAST", "bargaining", "BARGAINING", "NEUTRAL", "عيشك خويا ديرلي لافان في هاد الزوج قنادر راني ديما نشري من عندكم", "على عيني وراسي! على خاطر راك زبوننا الدائم نقصلك 1,000 دج وتوصيل مجاني لجيجل.", {"discount": True}),
    ("east_015", "EAST", "shoes", "AVAILABILITY_INQUIRY", "NEUTRAL", "باهي خلاص، كاين بوانتير 45 في هاد الصباط لعنابة؟", "نعم خويا بوانتير 45 متوفرة جلد طبيعي 100% ونبعثوهالك لعنابة الباهية على عيني.", {"wilaya": "عنابة (23)", "size": "45"}),

    # CENTER dialogues
    ("center_009", "CENTER", "food", "PRICE_INQUIRY", "NEUTRAL", "واش خويا شحال تحسبلي هاد الباك تاع العسل الحر وتوصيل للرويبة؟", "مرحبا خويا العزيز! الباك يدير 4,500 دج والتوصيل للرويبة كاين اليوم بـ 300 دج برك كولشي مريڤل.", {"wilaya": "الجزائر (16)", "commune": "الرويبة", "price_dzd": 4500}),
    ("center_010", "CENTER", "clothing", "ORDER", "POSITIVE", "salam khoya rani f blida, b3atli zouj tricot blanc taille L hawli 0661998877", "مريڤل خويا لعزيز! زوج تريكوات بيوضا طاي L مسجلين للبليدة ويوصلوك غدوا ان شاء الله، صحيت.", {"wilaya": "البليدة (9)", "color": "أبيض", "quantity": 2, "phone": "0661998877"}),
    ("center_011", "CENTER", "complaint", "COMPLAINT", "NEGATIVE", "خويا وصلني كولور غالط! طلبت كحل بعثتولي غري، بدلوهالي دروك!", "حقك علينا خويا وما يكون خاطرك غير طيب! دروك نخرجو ليفرور يبدلهالك في تيبازة باللون الكحل بدون أي تكلفة إضافية.", {"wilaya": "تيبازة (42)", "urgency": "HIGH"}),
    ("center_012", "CENTER", "logistics", "DELIVERY_INQUIRY", "NEUTRAL", "واش خويا كاين ليفرور يوصل لباب الدار في بوزريعة؟", "أكيد خويا العزيز، التوصيل حتى لباب دارك في بوزريعة وفي كامل بلديات العاصمة متوفر ديما.", {"wilaya": "الجزائر (16)", "commune": "بوزريعة"}),

    # SOUTH dialogues
    ("south_008", "SOUTH", "food", "ORDER", "POSITIVE", "مرحب بيك خويا، ابعثلي كرتونة تمر دقلة نور لبشار ورقمي 0670887766", "على الراس والعين خويا الغالي ومرحب بيك وبأهل بشار الكرام! التمر حر ويوصلكم في أفضل تغليف بإذن الله.", {"wilaya": "بشار (8)", "phone": "0670887766"}),
    ("south_009", "SOUTH", "general", "PRICE_INQUIRY", "NEUTRAL", "لاه السلعة هادي كم سعرها واصلة لغرداية بالدينار ربي يباركلك؟", "وفيك يبارك الله خويا! السلعة تدير 3,800 دج مع التوصيل لمكتب ياليدين غرداية مرحب بيك في كل وقت.", {"wilaya": "غرداية (47)", "price_dzd": 3800}),
    ("south_010", "SOUTH", "appliances", "DELIVERY_INQUIRY", "NEUTRAL", "salam khoya wah kayen livrison l el oued bureau yalidine w chhal te93od?", "وعليكم السلام ورحمة الله خويا العزيز! واه كاين توصيل للوادي وتوصل في 48 إلى 72 ساعة على الراس والعين.", {"wilaya": "الوادي (39)"}),
    ("south_011", "SOUTH", "clothing", "BARGAINING", "NEUTRAL", "ساعدنا في السومة خويا رانا في أدرار وبعد علينا الشحن", "على الراس والعين خويا، خفضنالك في سعر السلعة ونتحملوا جزء من مصاريف التوصيل كرامة لأهلنا في الجنوب.", {"wilaya": "أدرار (1)", "discount": True}),
    
    # SOUTH expanded
    ("south_012", "SOUTH", "clothing", "ORDER", "POSITIVE", "مرحب بيك خويا، ابعثلي دراعة صحراوية لتمنراست ورقمي 0661332211", "على الراس والعين مرحب بيك وبأهل الأهقار الكرام في تمنراست! طلبيتك مسجلة وتوصلك سالمة مع كوليتريكس.", {"wilaya": "تمنراست (11)", "phone": "0661332211"}),
    ("south_013", "SOUTH", "electronics", "DELIVERY_INQUIRY", "NEUTRAL", "salam alikom kayen livraison l touggourt stop desk yalidine?", "وعليكم السلام خويا العزيز! واه كاين مكتب ياليدين في تقرت مفتوح 6 أيام في السيمانة مرحب بيك.", {"wilaya": "تقرت (55)"}),
    ("south_014", "SOUTH", "hardware", "PRICE_INQUIRY", "NEUTRAL", "كم سعر مضخة مياه شمسية لغرداية ربي يباركلك في حلالك؟", "وفيك يبارك الله خويا! المضخة دوريجين تدير 18,500 دج وضمان عامين مع التوصيل لغرداية على الراس والعين.", {"wilaya": "غرداية (47)", "price_dzd": 18500}),
    ("south_015", "SOUTH", "general", "GREETING", "POSITIVE", "السلام عليكم ورحمة الله، واش حالكم يا أهل الخير؟ ربي يدوم فضلك وسلعتكم ديما توب", "وعليكم السلام ورحمة الله وبركاته! ربي يحفظكم ويبارك فيكم يا أهل الكرم والشهامة، نتشرفو بخدمتكم ديما.", {}),
    ("south_016", "SOUTH", "order", "ORDER", "NEUTRAL", "واه خويا اديني حبة لسوق تيميمون هاهو نميرو 0671445566", "على الراس والعين يا غالي! تسجلت الطلبية لتيميمون الواحة الحمراء ويوصلك اتصال من الليفرور قبل التسليم.", {"wilaya": "تيميمون (49)", "phone": "0671445566"}),
    ("south_017", "SOUTH", "dispute", "COMPLAINT", "NEGATIVE", "يا خويا لاه هكدا؟ سلعتكم وصلت ناقصة كابل شارج لبشار، شوفلنا حل ضرك!", "حقك على راسنا وعينينا خويا ونعتذروا أشد الاعتذار! الكابل الأصلي نخرجوهولك درك إكسبريس ومصاريف الشحن كاملة علينا.", {"wilaya": "بشار (8)", "urgency": "HIGH"}),

    # WEST expanded
    ("west_018", "WEST", "shoes", "ORDER", "POSITIVE", "salam khoya kirak ghaya, b3atli sberdina 42 l 3in tmouchent haw num 0770889900", "الله يسلمك ويحفظك خويا! السبردينة في النوار 42 مسجلة لعين تموشنت وتوصلك بعد غدوا وبلا مزية.", {"wilaya": "عين تموشنت (46)", "size": "42", "phone": "0770889900"}),
    ("west_019", "WEST", "clothing", "PRICE_INQUIRY", "NEUTRAL", "chwala souma ta3 had vesta f ghlizan w kach remise?", "في غليزان السومة 4,500 دج والسلعة كابا شابة بزاف، ونديرلك تخفيض 300 دج في التوصيل وبلا مزية خويا.", {"wilaya": "غليزان (48)", "price_dzd": 4500}),
    ("west_020", "WEST", "general", "BARGAINING", "NEUTRAL", "خويا راني شاري 5 حبات كيت بلوتوث لسعيدة، ديرلي سومة قوسطو نخدمو كيفكيف", "مرحبا بيك وبناس سعيدة! نحسبلك الحبة بـ 1,600 دج في بلاصة 2,000 دج وتوصيل مجاني صايي متفاهمين؟", {"wilaya": "سعيدة (20)", "quantity": 5, "price_dzd": 8000}),
    ("west_021", "WEST", "electronics", "AVAILABILITY_INQUIRY", "NEUTRAL", "kayen ecran protection l iphone 15 pro max f tiyaret?", "واه متوفرة أصلية مضادة للصدمات درك في تيارت خويا العزيز وبلا مزية.", {"wilaya": "تيارت (14)"}),

    # EAST expanded
    ("east_016", "EAST", "traditional", "ORDER", "POSITIVE", "عيشك أختي بعثيلي قندورة قطيفة كحلة لجيجل رقمي 0552778899", "يعيشك أختي العزيزة ومرحبا بناس جيجل الكورنيش والجمال! القندورة مسجلة وتوصلك للدار مع ياليدين على عيني.", {"wilaya": "جيجل (18)", "phone": "0552778899"}),
    ("east_017", "EAST", "hardware", "PRICE_INQUIRY", "NEUTRAL", "قداش السومة تاع بوسط صودير أنفرتر واصل لميلة؟", "السومة 16,500 دج نوعية إيطالية ممتازة مع كابل وماسك وتوصيل لميلة يدير 400 دج برك على عيني.", {"wilaya": "ميلة (43)", "price_dzd": 16500}),
    ("east_018", "EAST", "perfume", "BARGAINING", "NEUTRAL", "عيشك خويا ديرلي سومة باهية فزوج قراعي بارفان راني من أم البواقي", "على عيني وراسي خويا! نحسبلك الزوج بـ 6,200 دج وتوصيل أم البواقي مجاني يعيشك.", {"wilaya": "أم البواقي (4)", "price_dzd": 6200}),
    ("east_019", "EAST", "dispute", "COMPLAINT", "NEGATIVE", "وشبيك يا خويا باه نخلص سلعة فاسدة؟ راني نرجعها لسطيف ضروك وما ندفع والو!", "على عيني وراسي خويا وحقك مضمون 100%! ما تدفع حتى دورو والسلعة نرجعوها ونديرو فحص فوري ونبدلوهالك على حسابنا.", {"wilaya": "سطيف (19)", "urgency": "CRITICAL"}),
    ("east_020", "EAST", "shoes", "DELIVERY_INQUIRY", "NEUTRAL", "salam 3aychek kayen livrison l souk ahras stop desk w 9dach teb9a?", "وعليكم السلام ويعيشك خويا! كاين توصيل لسوق أهراس في 48 ساعة لمكتب ياليدين بـ 350 دج.", {"wilaya": "سوق أهراس (41)"}),

    # CENTER expanded
    ("center_013", "CENTER", "clothing", "ORDER", "POSITIVE", "واش خويا لعزيز بعثلي هاد الفيستا كحلة طاي XL لبومرداس نميرو 0662113344", "مريڤل خويا لعزيز! طلبيتك تسجلت وغدوا الصباح تكون عندك في بومرداس مع ليفرور صحيت.", {"wilaya": "بومرداس (35)", "color": "كحلة", "size": "XL", "phone": "0662113344"}),
    ("center_014", "CENTER", "tech", "PRICE_INQUIRY", "NEUTRAL", "شحال يدير باور بانك 20000 ميلي امبير وتوصيل للمدية؟", "يدير 3,800 دج أصلي مع شحن سريع 22.5W والتوصيل للمدية 400 دج كولشي مريڤل.", {"wilaya": "المدية (26)", "price_dzd": 3800}),
    ("center_015", "CENTER", "logistics", "DELIVERY_INQUIRY", "NEUTRAL", "kayen livraison a domicile f tipaza chenoua lyoum?", "أكيد خويا! التوصيل حتى لباب الدار في شنوة وتيبازة متوفر اليوم بـ 450 دج.", {"wilaya": "تيبازة (42)", "commune": "شنوة"}),
    ("center_016", "CENTER", "bargaining", "BARGAINING", "NEUTRAL", "خويا لعزيز ديرلي لافان في هاد الزوج ساعات راني ندي من عندكم ديما في الحراش", "على الراس خويا وليد الحراش! نحسبلك الزوج بـ 8,000 دج في بلاصة 9,400 دج وتوصيل مجاني كاش ما تسحق.", {"wilaya": "الجزائر (16)", "commune": "الحراش", "price_dzd": 8000}),
    ("center_017", "CENTER", "complaint", "COMPLAINT", "NEGATIVE", "خويا سلعتكم جات مفرعسة فالكرطونة تاعها! نبهدلكم في باجات الفيسبوك ادا ما حليتوش المشكل!", "حقك علينا خويا العزيز وما تتقلقش خلاص! رانا متأسفين بزاف ودرك نبعثولك وحدة جديدة مغلفة بإحكام ونديرو تعويض يرضيك 100%.", {"urgency": "HIGH", "reason": "PUBLIC_REPUTATION"}),

    # GENERAL_DARJA expanded
    ("gen_009", "GENERAL_DARJA", "order", "ORDER", "POSITIVE", "سلام خويا حاب نكوموندي 3 حبات شارجور أصليين للدار البيضاء 0550334455", "وعليكم السلام خويا مرحبا بيك! تم تسجيل طلبية 3 شواحن أصلية للدار البيضاء بالجزائر، السعر الإجمالي 4,800 دج مع توصيل مجاني.", {"wilaya": "الجزائر (16)", "commune": "الدار البيضاء", "quantity": 3, "phone": "0550334455"}),
    ("gen_010", "GENERAL_DARJA", "payment", "ORDER", "NEUTRAL", "خويا راني فيسيتلك 7500 دج فبريدي موب هاك الكود تاع الفيرمون", "الله يحفظك خويا وصلنا التأكيد وخرجنا الكولي تاعك مع شركة الشحن مباشرة، شكرا على ثقتك.", {"payment": "BARIDIMOB", "price_dzd": 7500}),
    ("gen_011", "GENERAL_DARJA", "logistics", "DELIVERY_INQUIRY", "NEUTRAL", "شحال وقت يدي التوصيل لبرج بوعريريج وهل كاين سطوب ديسك؟", "التوصيل لبرج بوعريريج يدي 24 إلى 48 ساعة وكاين مكتب ياليدين في وسط المدينة بـ 300 دج برك.", {"wilaya": "برج بوعريريج (34)"}),
    ("gen_012", "GENERAL_DARJA", "exchange", "COMPLAINT", "NEUTRAL", "سلام عليكم حبيت نبدل لاطاي تاع تريكو جاني عريض نقدر نبدلو؟", "وعليكم السلام خويا، أكيد الاستبدال متوفر ومجاني، نبعثولك المقاس الأصغر مع الليفرور غدوا.", {"item": "تريكو"}),
    ("gen_013", "GENERAL_DARJA", "wholesale", "PRICE_INQUIRY", "NEUTRAL", "خويا شحال تحسبلي كرطونة فيها 24 حبة سعر الجملة؟", "سعر الجملة للكرطونة (24 حبة) نحسبهولك بـ 28,000 دج أي 1,166 دج للحبة مع فاتورة وتوصيل مجاني لأي ولاية.", {"quantity": 24, "price_dzd": 28000}),
    ("gen_014", "GENERAL_DARJA", "dispute", "COMPLAINT", "NEGATIVE", "يا خويا وين راهي لاغارونتي لي هدرتو عليها؟ الكيت حبس بعد 3 أيام!", "مرحبا خويا، الضمان تاعنا حقيقي لمدة سنة كاملة، ابعثنا الكيت نبدلوهولك بواحد جديد ومغلف بدون أي نقاش وحقك محفوظ.", {"urgency": "HIGH"}),
    ("gen_015", "GENERAL_DARJA", "greeting", "GREETING", "POSITIVE", "جمعة مباركة ليكم يا أحسن متجر وربي يفتح عليكم أبواب الرزق", "جمعة مباركة وطيبة عليك وعلى عائلتك الكريمة خويا الغالي، ربي يتقبل منا ومنكم صالح الأعمال.", {}),
    
    # 10 Additional dialogues covering new Wilayas & realistic scenarios to reach 100
    ("south_018", "SOUTH", "clothing", "ORDER", "POSITIVE", "سلام خوتي ادولي قندورة وعباية للمنيعة هاهو نومرو 0663445566", "على الراس والعين خوتنا في ولاية المنيعة! طلبيتك مسجلة وتوصلك للمكتب مع ياليدين.", {"wilaya": "المنيعة (58)", "phone": "0663445566"}),
    ("south_019", "SOUTH", "general", "DELIVERY_INQUIRY", "NEUTRAL", "كاين لافريزون لبرج عمر إدريس بولاية إليزي؟", "نعم خويا نوصلوا لبرج عمر إدريس وإليزي عبر الخطوط الصحراوية في 3 إلى 5 أيام على عينينا.", {"wilaya": "إليزي (33)"}),
    ("south_020", "SOUTH", "electronics", "PRICE_INQUIRY", "NEUTRAL", "شحال يدير راديو شمس مع لومب لعين قزام ربي يسترك؟", "يدير 3,400 دج جودة عالية ويتحمل الظروف الصحراوية والتوصيل لعين قزام متوفر على الراس والعين.", {"wilaya": "عين قزام (54)", "price_dzd": 3400}),
    ("west_022", "WEST", "shoes", "PRICE_INQUIRY", "NEUTRAL", "chwala souma ta3 had sberdina l bayadh?", "السومة تدير 4,900 دج ونوصلوهالك للبيض في 48 ساعة وبلا مزية خويا العزيز.", {"wilaya": "البيض (32)", "price_dzd": 4900}),
    ("west_023", "WEST", "general", "ORDER", "POSITIVE", "صايي خويا شريت، راني في عين الصفراء بالنعامة هاك 0771998877", "الله يسلمك خويا! مسجل لعين الصفراء ولاية النعامة وتوصلك سلعة كابا نقية وبلا مزية.", {"wilaya": "النعامة (45)", "phone": "0771998877"}),
    ("east_021", "EAST", "tech", "AVAILABILITY_INQUIRY", "NEUTRAL", "عيشك خويا كاين شارجور ايفون اصلي 20w لخنشلة؟", "أهلا بناس خنشلة الأحرار! كاين واجد أصلي ونبعثوهولك ضرك ويوصلك في 24 ساعة على عيني.", {"wilaya": "خنشلة (40)"}),
    ("east_022", "EAST", "clothing", "ORDER", "POSITIVE", "قداش السومة تاع هاد الساك لتبسة؟ راني شاري هاك نومرو 0553112233", "السومة 3,800 دج والتوصيل لتبسة يدير 350 دج ومسجلة خويا لعزيز يعيشك.", {"wilaya": "تبسة (12)", "phone": "0553112233", "price_dzd": 3800}),
    ("center_018", "CENTER", "food", "ORDER", "POSITIVE", "واش خويا ابعثلي زوج باطات قهوة دزاير لعفروون البليدة 0661009988", "مريڤل خويا وليد العفرون! مسجل وتوصلك القهوة سخونة ومحمصة جديدة غدوا الصباح صحيت.", {"wilaya": "البليدة (9)", "commune": "العفرون", "phone": "0661009988"}),
    ("center_019", "CENTER", "order", "ORDER", "NEUTRAL", "خويا راني في الجلفة كاين توصيل للدار؟ نميرو 0664556677", "مرحبا بيك وبناس الجلفة! واه كاين توصيل للدار بـ 500 دج والكولي يخرج اليوم كولشي مريڤل.", {"wilaya": "الجلفة (17)", "phone": "0664556677"}),
    ("gen_016", "GENERAL_DARJA", "logistics", "DELIVERY_INQUIRY", "NEUTRAL", "سلام كاين توصيل للبير العاتر ولا لسطوب ديسك برك؟", "وعليكم السلام خويا، كاين توصيل للدار في بئر العاتر وكاين مكتب تبسة، واش يساعدك أكثر حنا هنا.", {"wilaya": "تبسة (12)", "commune": "بئر العاتر"}),

    # ================= CULTURAL, GASTRONOMY, PROVERBS & MEMES DIALOGUES =================
    ("cult_001", "CENTER", "culture_food", "ORDER", "POSITIVE", "واش خويا لعزيز ابعثلي 3 بلاطوات رشتة عاصمية بالدجاج ولفت للقبة 0661224466", "مريڤل خويا وليد القبة! الرشتة حرة سخونة واللفت والدجاج متبل بالقرفة كما يحب الخاطر، توصلك قبل الظهر صحيت.", {"wilaya": "الجزائر (16)", "commune": "القبة", "dish": "رشتة عاصمية", "phone": "0661224466"}),
    ("cult_002", "WEST", "culture_food", "ORDER", "POSITIVE", "سيدي خويا باغي 4 كاسكروطات كاران حامي مع الهريسة والكمون وبارد لوهران بلا مزية", "على الراس خويا! كاران حامي يغلي من الكوشة مع رشة كمون وكازوز حمود بوعلام، وهران الباهية في الخدمة درك وبلا مزية.", {"wilaya": "وهران (31)", "dish": "كرانتيكا / كاران"}),
    ("cult_003", "SOUTH", "culture_food", "ORDER", "POSITIVE", "مرحب بيك خويا، كاش 2 قصاع شخشوخة بسكرية حارة باللحم لبسكرة هاهو 0670119988", "على الراس والعين يا أهل الجود! شخشوخة بسكرية حرة بالراس والفلفل الحار توصلك دافية تفتح النفس وربي يباركلك.", {"wilaya": "بسكرة (7)", "dish": "شخشوخة بسكرية", "phone": "0670119988"}),
    ("cult_004", "EAST", "culture_food", "ORDER", "POSITIVE", "عيشك خويا كاين دوبارة بسكرية حارة مخلطة فول وحمص بسيرتا قسنطينة؟", "يعيشك خويا العزيز! كاين دوبارة حارة تفور بزيت الزيتون والحرور ورأس الحانوت القسنطيني على عيني وراسي.", {"wilaya": "قسنطينة (25)", "dish": "دوبارة"}),
    ("cult_005", "CENTER", "culture_sweets", "ORDER", "POSITIVE", "واش خويا كاش سنيوة قلب اللوز شامية معسلة باللوز لرمضان للبليدة؟", "مريڤل يا الغالي! سنيوة قلب اللوز عاصمي حقيقي محشي باللوز ومشرب بالشاربات وماء الزهر المقطر واجدة للبليدة.", {"wilaya": "البليدة (9)", "sweet": "قلب اللوز"}),
    ("cult_006", "EAST", "culture_sweets", "ORDER", "POSITIVE", "قداش السومة تاع كيلو مقروط العسل بالغرس واصل لسطيف العالي؟", "السومة 1,800 دج للكيلو، مقروط مرمل حر يذوب في الفم معسل بالعسل الصافي وتوصيل سطيف في 24 ساعة على عيني.", {"wilaya": "سطيف (19)", "sweet": "مقروط العسل", "price_dzd": 1800}),
    ("cult_007", "WEST", "proverb_wisdom", "GREETING", "POSITIVE", "كيراك خويا غايا، الحجرة في بلاصتها ثقيلة وسلعتكم ديما في بلاصتها ربي يحفظكم", "الله يسلمك ويحفظك خويا العزيز، كلام من ذهب وربي يثقل ميزان حسناتك! رانا ديما هنا لخدمتكم وبلا مزية.", {}),
    ("cult_008", "CENTER", "proverb_dispute", "COMPLAINT", "NEGATIVE", "يا خويا جاء يكحلها عماها ليفرور تاعكم حط الكولي عند الجيران بلا ما يعيطلي!", "حقك علينا خويا العزيز ونعتذروا أشد الاعتذار! هاد الخطأ غير مقبول تماماً، درك نتاصلوا بالسائق ونرجعولك الكولي ليدك مع تعويض يرضيك.", {"urgency": "HIGH"}),
    ("cult_009", "EAST", "proverb_complaint", "COMPLAINT", "NEGATIVE", "ما يحس بالجمرة غير لي كواتو، راني نستنى فلكولي في عنابة أسبوع وسلعتي فاسدة!", "يعيشك خويا وحاسين بيك وبحرقة حقك! السلعة نرجعوها ضروك على حسابنا ودراهمك يرجعولك كاملين أو بديل مجاني فورا.", {"wilaya": "عنابة (23)", "urgency": "CRITICAL"}),
    ("cult_010", "WEST", "meme_slang", "BARGAINING", "NEUTRAL", "راك فاهم خويا، ديرلي سومة حنينة راني باغي ندي 3 حبات لمستغانم", "على الراس وبلا مزية خويا العزيز! راك فاهم وحنا نفهموك، السومة نديروهالك لوز 6,500 دج في بلاصة 8,000 دج وتوصيل مستغانم باطل.", {"wilaya": "مستغانم (27)", "quantity": 3, "price_dzd": 6500}),
    ("cult_011", "CENTER", "meme_slang", "BARGAINING", "NEUTRAL", "نلعبوا ولا نحرموا خويا لعزيز! نحيلي 500 دج تاع التوصيل ولا نأنيلي لكوموند دروك", "هههه على الراس خويا وما تحرم والو! ما يكون غير خاطرك طيب، التوصيل باطل من عندنا وربي يدوم المحبة والسلعة توصلك مريڤلة.", {"discount": True}),
    ("cult_012", "EAST", "meme_slang", "COMPLAINT", "NEGATIVE", "واشنهي هادي قاع مكانش منها! كيفاش نحسبولي 800 دج لافريزون لقالمة؟", "حقك خويا العزيز ويعيشك، صرا خطأ في السيستام برك! التوصيل لقالمة 350 دج للمكتب وما نزيدو عليك حتى دورو زايد على عيني.", {"wilaya": "قالمة (24)"}),
    ("cult_013", "CENTER", "meme_slang", "GREETING", "POSITIVE", "تيكي تاكا يا ليكيب! الكولي لحقني لباب الدار في باب الواد في 24 ساعة يعطيكم الصحة", "الله يسترك خويا العزيز ويحفظك! خدمة سريعة ونقية كيما يحبو ولاد البهجة، بصحتك وتلبسها بالصحة والعافية.", {"wilaya": "الجزائر (16)", "commune": "باب الواد"}),
    ("cult_014", "SOUTH", "proverb_faith", "GREETING", "POSITIVE", "السلام عليكم، مول النية يربح ونيتكم باينة صافية في هاد المتجر ربي يبارك في تجارتكم", "وعليكم السلام ورحمة الله وبركاته خويا الغالي! وفيك يبارك الله يا أهل الصدق والأصالة، شهادة نعتزو بيها فوق راسنا.", {}),
    ("cult_015", "WEST", "market_places", "ORDER", "POSITIVE", "salam khoya baghi nji nchri 3andkom f souk castor wla 3andkom livraison l santa cruz f oran?", "مرحبا بيك في وهران الباهية! المحل تاعنا قريب من كاستور وعندنا توصيل حتى لسانتا كروز والمرجاجو درك وبلا مزية.", {"wilaya": "وهران (31)", "landmark": "كاستور / سانتا كروز"}),
    ("cult_016", "EAST", "market_places", "PRICE_INQUIRY", "NEUTRAL", "قداش السومة بالجملة كيما سوق دبي بالعلمة ادا ديت كرطونة كيت بلوتوث؟", "أهلا خويا! نحسبولك بسعر الجملة تماماً كيما سوق دبي بالعلمة 950 دج للحبة مع فاتورة وضمان وتوصيل للشرق كامل.", {"wilaya": "سطيف (19)", "market": "سوق دبي بالعلمة", "price_dzd": 950}),
    ("cult_017", "CENTER", "market_places", "AVAILABILITY_INQUIRY", "NEUTRAL", "واش خويا كاين هاد البياس تاشي تاع ايفون كيما يبيعوها في سوق بلفور بالحراش؟", "أكيد خويا العزيز! السلعة دوريجين برومي شوا كيما بلفور الحراش مع ضمان التجربة والاستبدال كولشي مريڤل.", {"wilaya": "الجزائر (16)", "market": "سوق بلفور الحراش"}),
    ("cult_018", "SOUTH", "market_places", "DELIVERY_INQUIRY", "NEUTRAL", "مرحب بيك خويا، كاين شحن لقصر تاغيت ببني عباس؟ وبشحال السومة؟", "على الراس والعين خويا العزيز! كاين توصيل لتاغيت وبني عباس مع كوليتريكس وتوصل في 3 أيام سالمة غانمة بإذن الله.", {"wilaya": "بني عباس (52)", "landmark": "قصر تاغيت"}),
    ("cult_019", "EAST", "market_places", "ORDER", "POSITIVE", "عيشك خويا ابعثلي رأس الحانوت حقيقي كيما سوق الرحبة بقسنطينة رقمي 0550443322", "يعيشك خويا ومرحبا بناس سيرتا! رأس حانوت قسنطيني أصلي مخلط على أصوله يوصلك في أبهى تغليف على عيني وراسي.", {"wilaya": "قسنطينة (25)", "market": "سوق الرحبة", "phone": "0550443322"}),
    ("cult_020", "CENTER", "market_places", "PRICE_INQUIRY", "NEUTRAL", "واش خويا شحال تحسبلي كيلو سردين نقي توصيل من سوق عين البنيان لبوزريعة؟", "مرحبا خويا! السردين طازج وصيد اليوم يدير 800 دج للكيلو وتوصيل لبوزريعة واجد دروك مع ليفرور مريڤل.", {"wilaya": "الجزائر (16)", "market": "سوق عين البنيان", "price_dzd": 800}),
    ("cult_021", "WEST", "slang_reaction", "AVAILABILITY_INQUIRY", "NEUTRAL", "خويا سلعتكم كابا أصلية ولا شناوة ومفرعسة؟ راني باغي نشري لسيدي بلعباس درك", "حرز تقلق روحك خويا العزيز! سلعتنا كابا أصلية 100% دوريجين، وادا لقيت فيها أدنى خربوشة نرجعولك دراهمك وبلا مزية.", {"wilaya": "سيدي بلعباس (22)"}),
    ("cult_022", "EAST", "slang_reaction", "BARGAINING", "NEUTRAL", "عيشك خويا ديرلي لافان في هاد الزوج صبابط راني نشري عليك ديما بلا تمسخير", "على عيني وراسي خويا الغالي وربي يبعد التمسخير! السومة نقصوهالك للخر ونديرولك 7,200 دج في بلاصة 8,500 دج وتوصيل باتنة باطل.", {"wilaya": "باتنة (5)", "discount": True}),
    ("cult_023", "CENTER", "slang_reaction", "GREETING", "POSITIVE", "واش خويا لعزيز قوسطو راه هايل والسلعة وصلتني حطة وهبال يعطيكم الصحة", "الله يسترك خويا العزيز ويدوم القوسطو العالي والضحكة! شهادتك هبال ونفرحو كي تعجبك السلعة، رانا هنا ديما.", {}),
    ("cult_024", "SOUTH", "slang_reaction", "ORDER", "POSITIVE", "واه خويا السلعة زينة والتاجر سيريو، اديني حبتين لغرداية وهاهو نومرو 0670332211", "على الراس والعين يا أهل ميزاب الكرام! طلبيتك مسجلة وحبتين في طريقهم لغرداية وربي يباركلك في رزقك.", {"wilaya": "غرداية (47)", "phone": "0670332211"}),
    ("cult_025", "GENERAL_DARJA", "proverb_wisdom", "GREETING", "POSITIVE", "الصنعة في اليد أمان من الفقر وسلعتكم متقونة ما شاء الله تبارك الرحمن", "بارك الله فيك وجازاك الله كل خير خويا الغالي! إتقان العمل عبادة وشرف لينا رضاك وثقتك الدائمة.", {}),

    # 25 More diverse cultural & regional real-world dialogues
    ("cult_026", "EAST", "landmarks", "DELIVERY_INQUIRY", "NEUTRAL", "خويا كاين توصيل لقصر أحمد باي بقسنطينة سطوب ديسك؟", "أكيد خويا العزيز، مكتب ياليدين في وسط سيرتا قريب جداً من قصر أحمد باي والتوصيل يدير 300 دج على عيني.", {"wilaya": "قسنطينة (25)", "landmark": "قصر أحمد باي"}),
    ("cult_027", "CENTER", "food_delivery", "ORDER", "POSITIVE", "واش خويا كاش شخشوخة ظفر بسكرية سخونة واصلة للعاصمة باب الواد 0661887766؟", "مريڤل خويا الغالي! الشخشوخة تخرجلك سخونة تفور بالحمص ولحم الخروف وتوصلك لباب الواد قبل الغداء صحيت.", {"wilaya": "الجزائر (16)", "commune": "باب الواد", "phone": "0661887766"}),
    ("cult_028", "WEST", "complaint_slang", "COMPLAINT", "NEGATIVE", "سلعتكم خردة ومفرعسة، وين راهي لاغارونتي لي زوختو بيها في الفيسبوك؟", "حقك علينا خويا وحرز تتقلق! حنا ما نزخوش وكلامنا كلمة وحدة، السلعة نبدلوهالك بوحدة جديدة دوريجين درك وبلا مزية.", {"urgency": "HIGH"}),
    ("cult_029", "EAST", "complaint_driver", "COMPLAINT", "NEGATIVE", "خويا راني مزعفان بزاف من ليفرور تاعكم في عنابة، عيطلي في وقت الماتش وما حبش يستنى 5 دقائق!", "متأسفين ياسر خويا العزيز ونعتذروا منك على تصرف السائق! درك نكلمو رئيس مركز عنابة ونوصلوهالك للدار باطل على عيني.", {"wilaya": "عنابة (23)", "urgency": "HIGH"}),
    ("cult_030", "WEST", "street_food", "ORDER", "POSITIVE", "كيراك خويا غايا، باغي كاسكروط كاران حامي مع بارد تشينة لوهران درك", "الله يسلمك خويا! كاران وهراني حر مع الكمون والهريسة وكازوز بارد راه واجد ومرحب بيك وبلا مزية.", {"wilaya": "وهران (31)"}),
    ("cult_031", "EAST", "shopping", "PRICE_INQUIRY", "NEUTRAL", "قداش السومة تاع هاد لفيستا الكحلة لسوق الرحبة بسيرتا؟", "السومة تدير 5,400 دج والسلعة باهية خلاص كابا تركية، ونوصلوهالك لسوق الرحبة في قسنطينة على عيني.", {"wilaya": "قسنطينة (25)", "price_dzd": 5400}),
    ("cult_032", "SOUTH", "dates_tradition", "ORDER", "POSITIVE", "مرحب بيك خويا، كاين تمور دقلة نور حرة من بسكرة لبشار؟ ورقمي 0670445566", "على الراس والعين يا أهل بشار الكرام! دقلة نور عسل طبيعي من نخيل بسكرة توصلك معبأة بإتقان وربي يباركلك.", {"wilaya": "بشار (8)", "phone": "0670445566"}),
    ("cult_033", "CENTER", "tech_market", "AVAILABILITY_INQUIRY", "NEUTRAL", "واش خويا كاش ما تسحق في بلفور الحراش رانا هنا نحوسو على باطري اصلية", "مرحبا بخويا وليد الحراش! الباطري أصلية 100% مع ضمان 6 أشهر وموجودة كولشي مريڤل كاش ما تسحق.", {"wilaya": "الجزائر (16)", "commune": "الحراش"}),
    ("cult_034", "EAST", "proverb_commerce", "BARGAINING", "NEUTRAL", "الجديد حبو والقديم لا تفرط فيه، راني زبون قديم من سطيف وديرلي سومة باهية", "على عيني وراسي زبوننا الوفي! ما نفرطوش فيك خلاص، نحسبولك الحبة بـ 3,200 دج في بلاصة 3,800 دج وتوصيل سطيف باطل.", {"wilaya": "سطيف (19)", "discount": True}),
    ("cult_035", "EAST", "proverb_ethics", "COMPLAINT", "NEGATIVE", "اللسان ما فيه عظم بصح ليفرور تاعكم هدر معايا بطريقة عيانة بزاف في باتنة!", "حقك على راسنا وعينينا خويا ونعتذروا أشد الاعتذار! هاد السلوك لا يمثل متجرنا، وتم تنبيه السائق وتوصيلك القادم مجاني تماماً.", {"wilaya": "باتنة (5)", "urgency": "HIGH"}),
    ("cult_036", "WEST", "proverb_satisfaction", "GREETING", "POSITIVE", "طاح الحك وصاب غطاه، هاد السبردينة لي كنت نحوس عليها في تلمسان سنين يعطيكم الصحة", "الله يحفظك ويسلمك خويا العزيز! بصحتك وراحتك وتلبسها بالصحة والهنا وبلا مزية، نتشرفو بخدمة ناس تلمسان ديما.", {"wilaya": "تلمسان (13)"}),
    ("cult_037", "CENTER", "proverb_deal", "BARGAINING", "NEUTRAL", "يا شاري دالة ويا بايع دالة، ساعدنا شوية في هاد لفيستا خويا لعزيز ربي يسهلك", "على الراس خويا! الدنيا بيع وشرا وأهم حاجة رضاكم، نقصولك 600 دج وتوصيل العاصمة باطل كاش ما تسحق.", {"discount": True}),
    ("cult_038", "GENERAL_DARJA", "proverb_kindness", "GREETING", "POSITIVE", "سعدك يا فاعل الخير، شكرا على الهدية والكابل لي بعثتوهم مع الكوموند ربي يكثر خيركم", "وفيك يبارك الله خويا العزيز! تستاهل كل خير وهاد الهدية عربون وفاء لثقتكم الغالية في متجرنا.", {}),
    ("cult_039", "WEST", "proverb_thrift", "BARGAINING", "NEUTRAL", "خبي قرشك الأبيض ليومك الأسود، راني نقتصد وديرلي ريميز مليحة في زوج حبات لوهران", "الله يسلمك خويا وحكمة في محلها! نديرلك تخفيض 1,200 دج في الزوج حبات وتوصيل ياليدين وهران باطل وبلا مزية.", {"wilaya": "وهران (31)", "quantity": 2}),
    ("cult_040", "CENTER", "proverb_destiny", "COMPLAINT", "NEGATIVE", "المكتوب ما منو هروب، تكسرت السلعة في الطريق لتيبازة ونستنى تعويض منكم دروك", "حقك مضمون 100% خويا وما تقلقش خلاص! نبعثولك وحدة جديدة مغلفة ومحمية غدوا الصباح وتعويض على التأخير صحيت.", {"wilaya": "تيبازة (42)"}),
    ("cult_041", "CENTER", "slang_praise", "GREETING", "POSITIVE", "خويا سلعتكم لوز ما شاء الله هبال في تيبازة شنوة، عجبت كامل لافامي", "الله يسترك خويا العزيز وربي يحفظك ويحفظ لافامي كاملة! شهادتكم فخر لينا وكاش ما تسحقو رانا هنا ديما.", {"wilaya": "تيبازة (42)", "commune": "شنوة"}),
    ("cult_042", "SOUTH", "desert_delivery", "ORDER", "POSITIVE", "خويا راني شاري كليماتيزور لتاغيت بشار وبشحال الديلي؟ نومرو 0670998811", "على الراس والعين خوتنا في تاغيت الساحرة! التوصيل مؤمن عبر كوليتريكس ويوصل في 3 أيام سالما غانما بإذن الله.", {"wilaya": "بني عباس (52)", "landmark": "تاغيت", "phone": "0670998811"}),
    ("cult_043", "EAST", "landmark_inquiry", "AVAILABILITY_INQUIRY", "NEUTRAL", "عيشك خويا كاش كاسكيطة دوريجين كيما لي يبيعو في عين الفوارة بسطيف؟", "نعم خويا الغالي، سلعة كابا أصلية 100% ونوعية ممتازة وتوصيل سطيف العالي متوفر غدوا على عيني.", {"wilaya": "سطيف (19)", "landmark": "عين الفوارة"}),
    ("cult_044", "CENTER", "quick_order", "ORDER", "POSITIVE", "واش خويا كولشي مريڤل؟ بعثلي 2 حبات تريكو كحل لأولاد فايت العاصمة 0661334455", "مريڤل خويا وليد أولاد فايت! زوج تريكوات في النوار مسجلين وغدوا يكونو عندك مع ليفرور صحيت.", {"wilaya": "الجزائر (16)", "commune": "أولاد فايت", "phone": "0661334455"}),
    ("cult_045", "WEST", "quick_order", "ORDER", "POSITIVE", "صايي خويا شريت هاك نميرو 0770554433 واديني حبة لمغنية بتلمسان", "الله يسلمك خويا ومرحبا بناس مغنية الأحرار! سلعتك مسجلة وتوصلك بعد غدوا ان شاء الله وبلا مزية.", {"wilaya": "تلمسان (13)", "commune": "مغنية", "phone": "0770554433"}),
    ("cult_046", "SOUTH", "desert_feedback", "GREETING", "POSITIVE", "مرحب بيك خويا، السلعة وصلت لتمنراست تبارك الله وزينة بزاف وربي يرزقكم من وسع", "وفيك يبارك الله خويا العزيز! فخورين بخدمة أهلنا في أقصى الجنوب وتمنراست الأبية، جازاكم الله خيرا.", {"wilaya": "تمنراست (11)"}),
    ("cult_047", "SOUTH", "quick_order", "ORDER", "POSITIVE", "واه خويا السومة باهية وسجللي طلبية للوادي سوف هاهو نميرو 0670889922", "على الراس والعين يا أهل قمار والوادي الكرام! الطلبية مسجلة وتوصلكم للمكتب في ياليدين وربي يباركلك.", {"wilaya": "الوادي (39)", "phone": "0670889922"}),
    ("cult_048", "EAST", "tech_inquiry", "PRICE_INQUIRY", "NEUTRAL", "عيشك خويا قداش السومة تاع كابل تيب سي أنكر لجيجل الكورنيش؟", "السومة 1,600 دج أصلي مع ضمان عام كامل وتوصيل جيجل يدير 350 دج برك على عيني وراسي.", {"wilaya": "جيجل (18)", "price_dzd": 1600}),
    ("cult_049", "CENTER", "fast_delivery", "DELIVERY_INQUIRY", "NEUTRAL", "واش خويا كاين توصيل للدرارية بالجزائر ليوما فالعشية راني مزروب؟", "أكيد خويا العزيز، التوصيل إكسبريس للدرارية متوفر اليوم قبل 18:00 وكولشي مريڤل كاش ما تسحق.", {"wilaya": "الجزائر (16)", "commune": "الدرارية"}),
    ("cult_050", "GENERAL_DARJA", "bargaining_fair", "BARGAINING", "NEUTRAL", "خويا هبلتونا بالسومات الزايدة، ديرولنا برومو شابة لولاد لبلاد رانا شاريين", "على الراس خويا وحقك علينا! دايرين برومو خاصة لولاد بلادنا تخفيض 20% على كامل المنتجات وتوصيل مخفض، مرحبا بيك.", {"discount": True}),
]

for row in ADDITIONAL_DATA:
    DIALOGUES.append({
        "id": row[0],
        "region": row[1],
        "domain": row[2],
        "intent": row[3],
        "sentiment": row[4],
        "customer_message": row[5],
        "merchant_response": row[6],
        "entities": row[7],
        "notes": f"Additional {row[1]} dialogue covering {row[2]} domain."
    })

def main():
    root = Path(__file__).resolve().parent.parent
    data_dir = root / "data"
    out_file = data_dir / "dialogues.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(DIALOGUES, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(DIALOGUES)} dialogues in {out_file.relative_to(root)}")

if __name__ == "__main__":
    main()
