"""
Enrich data/wilayas.json with major commercial communes, dairas, and transliterated aliases.
"""
import json
from pathlib import Path

COMMUNES_BY_WILAYA = {
    1: {  # Adrar
        "ar": ["أدرار", "تيميمون", "رقان", "أولف", "زاوية كنتة", "تسابيت", "فنوغيل"],
        "fr": ["Adrar", "Timimoun", "Reggane", "Aoulef", "Zaouiet Kounta", "Tsabit", "Fenoughil"]
    },
    2: {  # Chlef
        "ar": ["الشلف", "تنس", "بوقادير", "وادي الفضة", "الشطية", "عين مران", "أولاد فارس", "تاوقريت", "زبوجة"],
        "fr": ["Chlef", "Tenes", "Boukadir", "Oued Fodda", "Chettia", "Ain Merane", "Ouled Fares", "Taougrit", "Zeboudja"]
    },
    3: {  # Laghouat
        "ar": ["الأغواط", "حاسي الرمل", "آفلو", "قصر الحيران", "عين ماضي", "سيدي مخلوف", "البيضاء"],
        "fr": ["Laghouat", "Hassi R'Mel", "Aflou", "Ksar El Hirane", "Ain Madhi", "Sidi Makhlouf", "El Beidha"]
    },
    4: {  # Oum El Bouaghi
        "ar": ["أم البواقي", "عين فكرون", "عين البيضاء", "عين مليلة", "مسكيانة", "قصر الصبيحي", "سيقوس"],
        "fr": ["Oum El Bouaghi", "Ain Fakroun", "Ain Beida", "Ain M'lila", "Meskiana", "Ksar Sbahi", "Sigus"]
    },
    5: {  # Batna
        "ar": ["باتنة", "بريكة", "عين التوتة", "مروانة", "تازولت", "نقاوص", "أريس", "المعذر", "رأس العيون", "سريانة"],
        "fr": ["Batna", "Barika", "Ain Touta", "Merouana", "Tazoult", "N'Gaous", "Arris", "El Madher", "Ras El Aioun", "Seriana"]
    },
    6: {  # Bejaia
        "ar": ["بجاية", "أقبو", "القصر", "أميزور", "خراطة", "تيشي", "صدوق", "سيدي عيش", "أوقاس", "إغيل علي", "تازمالت"],
        "fr": ["Bejaia", "Akbou", "El Kseur", "Amizour", "Kherrata", "Tichy", "Seddouk", "Sidi Aich", "Aokas", "Ighil Ali", "Tazmalt"]
    },
    7: {  # Biskra
        "ar": ["بسكرة", "طولقة", "سيدي عقبة", "أولاد جلال", "الدوسن", "القنطرة", "فوغالة", "جمورة", "أورلال"],
        "fr": ["Biskra", "Tolga", "Sidi Okba", "Ouled Djellal", "Doucen", "El Kantara", "Foughala", "Djemorah", "Ourlal"]
    },
    8: {  # Bechar
        "ar": ["بشار", "القنادسة", "بني ونيف", "تاغيت", "العبادلة", "تبلبالة"],
        "fr": ["Bechar", "Kenadsa", "Beni Ounif", "Taghit", "Abadla", "Tabelbala"]
    },
    9: {  # Blida
        "ar": ["البليدة", "بوفاريك", "أولاد يعيش", "العفرون", "موزاية", "بوقرة", "وادي العلايق", "الصومعة", "الشبلي", "بوعرفة", "الأربعاء", "مفتاح"],
        "fr": ["Blida", "Boufarik", "Ouled Yaich", "El Affroun", "Mouzaia", "Bougara", "Oued Alleug", "Soumaa", "Chebli", "Bouarfa", "Larbaa", "Meftah"]
    },
    10: {  # Bouira
        "ar": ["البويرة", "الأخضرية", "سور الغزلان", "عين بسام", "مشدالة", "بئر غبالو", "القادرية", "حيزر", "أهل القصر"],
        "fr": ["Bouira", "Lakhdaria", "Sour El Ghozlane", "Ain Bessem", "M'Chedallah", "Bir Ghbalou", "Kadiria", "Haizer", "Ahl El Ksar"]
    },
    11: {  # Tamanrasset
        "ar": ["تمنراست", "عين امقل", "أبلسة", "إيدلس", "تاظروك"],
        "fr": ["Tamanrasset", "Ain Amguel", "Abalessa", "Idles", "Tazrouk"]
    },
    12: {  # Tebessa
        "ar": ["تبسة", "بئر العاتر", "الشريعة", "الونزة", "العوينات", "الكويف", "مرسط", "الماء الأبيض", "نقرين"],
        "fr": ["Tebessa", "Bir El Ater", "Cheria", "Ouenza", "El Aouinet", "El Kouif", "Morsott", "El Ma Labiodh", "Negrine"]
    },
    13: {  # Tlemcen
        "ar": ["تلمسان", "مغنية", "سبدو", "الغزوات", "منصورة", "الرمشي", "الحناية", "شتوان", "ندرومة", "أولاد ميمون", "باب العسة", "بني صاف"],
        "fr": ["Tlemcen", "Maghnia", "Sebdou", "Ghazaouet", "Mansourah", "Remchi", "Hennaya", "Chetouane", "Nedroma", "Ouled Mimoun", "Bab El Assa"]
    },
    14: {  # Tiaret
        "ar": ["تيارت", "فرندة", "قصر الشلالة", "السوقر", "مهدية", "رحوية", "الدحموني", "حمادية"],
        "fr": ["Tiaret", "Frenda", "Ksar Chellala", "Sougueur", "Mahdia", "Rahouia", "Dahmouni", "Hamadia"]
    },
    15: {  # Tizi Ouzou
        "ar": ["تيزي وزو", "ذراع بن خدة", "عزازقة", "بوغني", "واضية", "تيقزيرت", "ذراع الميزان", "عين الحمام", "أزفون", "الأربعاء نايث إيراثن", "واقنون", "تادمايت"],
        "fr": ["Tizi Ouzou", "Draa Ben Khedda", "Azazga", "Boghni", "Ouadhia", "Tigzirt", "Draa El Mizan", "Ain El Hammam", "Azeffoun", "Larbaa Nath Irathen", "Ouaguenoun", "Tadmait"]
    },
    16: {  # Alger
        "ar": [
            "الجزائر", "باب الوادي", "القبة", "الحراش", "باب الزوار", "حيدرة", "رويبة", "الشراقة", "درارية",
            "بئر مراد رايس", "بئر خادم", "دالي ابراهيم", "بن عكنون", "براقي", "بوزريعة", "زرالدة", "سطاوالي",
            "عين طاية", "الرغاية", "برج الكيفان", "الكاليتوس", "بئر توتة", "الأبيار", "المرادية", "بولوغين",
            "عين البنيان", "سيدي امحمد", "باش جراح", "الحميز", "المقارية", "المحالمة", "الدويرة", "باباحسن",
            "خرايسية", "السحاولة", "البليدة", "الرويسات", "المدنية", "القصبة"
        ],
        "fr": [
            "Alger", "Bab El Oued", "Kouba", "El Harrach", "Bab Ezzouar", "Hydra", "Rouiba", "Cheraga", "Draria",
            "Bir Mourad Rais", "Birkhadem", "Dely Ibrahim", "Ben Aknoun", "Baraki", "Bouzareah", "Zeralda", "Staoueli",
            "Ain Taya", "Reghaia", "Bordj El Kiffan", "Les Eucalyptus", "Birtouta", "El Biar", "El Mouradia", "Bologhine",
            "Ain Benian", "Sidi M'Hamed", "Bachedjerrah", "El Hamiz", "El Magharia", "Mehalma", "Douera", "Baba Hassen",
            "Khraicia", "Saoula", "El Madania", "Casbah"
        ]
    },
    17: {  # Djelfa
        "ar": ["الجلفة", "عين وسارة", "مسعد", "حاسي بحبح", "الشارف", "دار الشيوخ", "الإدريسية", "البيرين", "حد الصحاري"],
        "fr": ["Djelfa", "Ain Oussera", "Messaad", "Hassi Bahbah", "Charef", "Dar Chioukh", "El Idrissia", "Birine", "Had Sahary"]
    },
    18: {  # Jijel
        "ar": ["جيجل", "الطاهير", "الميلية", "العوانة", "زيامة منصورية", "الشقفة", "العنصر", "تاكسنة", "جيملة"],
        "fr": ["Jijel", "Taher", "El Milia", "El Aouana", "Ziama Mansouriah", "Chekfa", "El Ancer", "Taxenna", "Djimla"]
    },
    19: {  # Setif
        "ar": ["سطيف", "العلمة", "عين ولمان", "عين الكبيرة", "عين أرنات", "بوقاعة", "بني ورتيلان", "عموشة", "صالح باي", "قجال", "بابور", "جميلة"],
        "fr": ["Setif", "El Eulma", "Ain Oulmene", "Ain El Kebira", "Ain Arnat", "Bougaa", "Beni Ourtilane", "Amoucha", "Salah Bey", "Guidjel", "Babor", "Djemila"]
    },
    20: {  # Saida
        "ar": ["سعيدة", "يوب", "الحساسنة", "سيدي بوبكر", "أولاد إبراهيم", "عين الحجر"],
        "fr": ["Saida", "Youb", "Hassasna", "Sidi Boubekeur", "Ouled Brahim", "Ain El Hadjar"]
    },
    21: {  # Skikda
        "ar": ["سكيكدة", "القل", "الحروش", "عزابة", "تمالوس", "فلفلة", "رمضان جمال", "سيدي مزغيش", "بني بشير"],
        "fr": ["Skikda", "Collo", "El Harrouch", "Azzaba", "Tamalous", "Filfila", "Ramdane Djamel", "Sidi Mezghiche", "Beni Bechir"]
    },
    22: {  # Sidi Bel Abbes
        "ar": ["سيدي بلعباس", "تلاغ", "سفيزف", "ابن باديس", "مصطفى بن براهيم", "رأس الماء", "مرحوم", "تنيرة"],
        "fr": ["Sidi Bel Abbes", "Telagh", "Sfisef", "Ben Badis", "Mostefa Ben Brahim", "Ras El Ma", "Marhoum", "Tenira"]
    },
    23: {  # Annaba
        "ar": ["عنابة", "البوني", "الحجار", "برحال", "سيدي عمار", "سرايدي", "عين الباردة", "شطايبي"],
        "fr": ["Annaba", "El Bouni", "El Hadjar", "Berrahal", "Sidi Amar", "Seraidi", "Ain Berda", "Chetaibi"]
    },
    24: {  # Guelma
        "ar": ["قالمة", "وادي الزناتي", "بوشقوف", "هيليوبوليس", "حمام دباغ", "بلخير", "عين مخلوف", "قلعة بوصبع"],
        "fr": ["Guelma", "Oued Zenati", "Bouchegouf", "Heliopolis", "Hammam Debagh", "Belkheir", "Ain Makhlouf", "Guelaat Bou Sbaa"]
    },
    25: {  # Constantine
        "ar": ["قسنطينة", "الخروب", "علي منجلي", "حامة بوزيان", "زيغود يوسف", "عين السمارة", "ديدوش مراد", "ابن باديس", "عين عبيد"],
        "fr": ["Constantine", "El Khroub", "Ali Mendjeli", "Hamma Bouziane", "Zighoud Youcef", "Ain Smara", "Didouche Mourad", "Ibn Badis", "Ain Abid"]
    },
    26: {  # Medea
        "ar": ["المدية", "وزرة", "البرواقية", "قصر البخاري", "بني سليمان", "شلالة العذاورة", "تابلاط", "العمارية", "سيدي نعمان", "عين بوسعادة"],
        "fr": ["Medea", "Ouzera", "Berrouaghia", "Ksar El Boukhari", "Beni Slimane", "Chellalat El Adhaoura", "Tablat", "El Omaria", "Sidi Naamane"]
    },
    27: {  # Mostaganem
        "ar": ["مستغانم", "عين تادلس", "ماسرى", "حاسي مماش", "سيدي علي", "بوقيرات", "خير الدين", "سيدي لخضر", "عشعاشة"],
        "fr": ["Mostaganem", "Ain Tedeles", "Mesra", "Hassi Mameche", "Sidi Ali", "Bouguirat", "Kheir Eddine", "Sidi Lakhdar", "Achaacha"]
    },
    28: {  # M'Sila
        "ar": ["المسيلة", "بوسعادة", "مقرة", "حمام الضلعة", "سيدي عيسى", "أولاد دراج", "عين الحجل", "سليم", "الهامل", "بن سرور"],
        "fr": ["M'Sila", "Bou Saada", "Magra", "Hammam Dhalaa", "Sidi Aissa", "Ouled Derradj", "Ain El Hadjel", "Slim", "El Hamel", "Ben Srour"]
    },
    29: {  # Mascara
        "ar": ["معسكر", "سيق", "تيغنيف", "المحمدية", "وادي الأبطال", "غريس", "عوف", "زهانة", "فروحة"],
        "fr": ["Mascara", "Sig", "Tighennif", "Mohammadia", "Oued El Abtal", "Ghriss", "Aouf", "Zahana", "Froha"]
    },
    30: {  # Ouargla
        "ar": ["ورقلة", "حاسي مسعود", "تقرت", "تماسين", "سيدي خويلد", "الرويسات", "الطيبات", "أنقوسة"],
        "fr": ["Ouargla", "Hassi Messaoud", "Touggourt", "Temacine", "Sidi Khouiled", "Rouissat", "Taibet", "N'Goussa"]
    },
    31: {  # Oran
        "ar": ["وهران", "السانية", "عين الترك", "أرزيو", "بئر الجير", "مسرغين", "بطيوة", "قديل", "وادي تليلات", "الكرمة", "بوسفر", "العنصر"],
        "fr": ["Oran", "Es Senia", "Ain El Turk", "Arzew", "Bir El Djir", "Messerghin", "Bethioua", "Gdyel", "Oued Tlelat", "El Kerma", "Bousfer", "El Ancor"]
    },
    32: {  # El Bayadh
        "ar": ["البيض", "الأبيض سيدي الشيخ", "بوعلام", "بريزينة", "الرقاصة", "بوقطب", "الكاف الأحمر"],
        "fr": ["El Bayadh", "El Abiodh Sidi Cheikh", "Boualem", "Brezina", "Rogassa", "Bougtob", "El Kheiter"]
    },
    33: {  # Illizi
        "ar": ["إليزي", "جانت", "عين أمناس", "برج الحواس", "دبداب"],
        "fr": ["Illizi", "Djanet", "In Amenas", "Bordj El Haouas", "Debdeb"]
    },
    34: {  # Bordj Bou Arreridj
        "ar": ["برج بوعريريج", "رأس الوادي", "المنصورة", "مجانة", "الحمادية", "برج زمورة", "الياشير", "عين تاغروت", "بئر قاصد علي"],
        "fr": ["Bordj Bou Arreridj", "Ras El Oued", "Mansoura", "Medjana", "El Hamadia", "Bordj Zemoura", "El Achir", "Ain Taghrout", "Bir Kasdali"]
    },
    35: {  # Boumerdes
        "ar": ["بومرداس", "دلس", "الثنية", "برج منايل", "بودواو", "خميس الخشنة", "يسر", "قورصو", "زموري", "سي مصطفى", "الناصرية", "تيجلابين", "حمادي"],
        "fr": ["Boumerdes", "Dellys", "Thenia", "Bordj Menaiel", "Boudouaou", "Khemis El Khechna", "Isser", "Corso", "Zemmouri", "Si Mustapha", "Naciria", "Tidjelabine", "Hammadi"]
    },
    36: {  # El Tarf
        "ar": ["الطارف", "القالة", "بن مهيدي", "بوثلجة", "الذرعان", "بوحجار", "الشط", "عين العسل"],
        "fr": ["El Tarf", "El Kala", "Ben M'Hidi", "Boutheldja", "Drean", "Bouhadjar", "Echatt", "Ain El Assel"]
    },
    37: {  # Tindouf
        "ar": ["تندوف", "أم العسل"],
        "fr": ["Tindouf", "Oum El Assel"]
    },
    38: {  # Tissemsilt
        "ar": ["تيسمسيلت", "ثنية الحد", "خميستي", "برج بونعامة", "لرجام", "عماري"],
        "fr": ["Tissemsilt", "Theniet El Had", "Khemisti", "Bordj Bounaama", "Lardjem", "Ammari"]
    },
    39: {  # El Oued
        "ar": ["الوادي", "قمار", "حاسي خليفة", "الدبيلة", "الرقيبة", "جامعة", "المغير", "البياضة", "الرباح", "المقرن"],
        "fr": ["El Oued", "Guemar", "Hassi Khalifa", "Debila", "Reguiba", "Djamaa", "El Meghaier", "El Bayadha", "Robbah", "Magrane"]
    },
    40: {  # Khenchela
        "ar": ["خنشلة", "ششار", "قايس", "المحمل", "بابار", "عين الطويلة", "الحامة", "بوحمامة"],
        "fr": ["Khenchela", "Chechar", "Kais", "El Mahmal", "Babar", "Ain Touila", "El Hamma", "Bouhmama"]
    },
    41: {  # Souk Ahras
        "ar": ["سوق أهراس", "سدراتة", "المراهنة", "تاورة", "مداوروش", "أولاد دريس", "أم العظائم", "المشروحة"],
        "fr": ["Souk Ahras", "Sedrata", "M'Daourouch", "Taoura", "Merahna", "Ouled Driss", "Oum El Adhaim", "Mechroha"]
    },
    42: {  # Tipaza
        "ar": ["تيبازة", "شرشال", "القليعة", "فوكة", "حطاطبة", "بواسماعيل", "الداموس", "حجرة النص", "قوراية", "سيدي راشد", "عين تاقورايت", "سيدي غيلاس"],
        "fr": ["Tipaza", "Cherchell", "Kolea", "Fouka", "Hattatba", "Bou Ismail", "Damous", "Hadjret En Nouss", "Gouraya", "Sidi Rached", "Ain Tagourait", "Sidi Ghiles"]
    },
    43: {  # Mila
        "ar": ["ميلة", "شلغوم العيد", "تلاغمة", "تاجنانت", "فرجيوة", "زغاية", "وادي العثمانية", "سيدي مروان", "القرارم قوقة", "عين التين"],
        "fr": ["Mila", "Chelghoum Laid", "Teleghma", "Tadjenanet", "Ferdjioua", "Zeghaia", "Oued Athmania", "Sidi Merouane", "Grarem Gouga", "Ain Tine"]
    },
    44: {  # Ain Defla
        "ar": ["عين الدفلى", "خميس مليانة", "العطاف", "مليانة", "جليدة", "روينا", "جندل", "بوراشد", "الحسنية", "بومدفع", "سيدي لخضر"],
        "fr": ["Ain Defla", "Khemis Miliana", "El Attaf", "Miliana", "Djelida", "Rouina", "Djendel", "Bourached", "El Hassania", "Boumedfaa", "Sidi Lakhdar"]
    },
    45: {  # Naama
        "ar": ["النعامة", "المشرية", "عين الصفراء", "عسلة", "صفيصيفة", "مكمن بن عمار", "تيوت", "جنين بورزق"],
        "fr": ["Naama", "Mecheria", "Ain Sefra", "Asla", "Sfissifa", "Makman Ben Amer", "Tiout", "Djenienne Bourezg"]
    },
    46: {  # Ain Temouchent
        "ar": ["عين تموشنت", "بني صاف", "حمام بوحجر", "العامرية", "عين الكيحل", "ولهاصة", "عين الطلبة", "المالح"],
        "fr": ["Ain Temouchent", "Beni Saf", "Hammam Bouhadjar", "El Amria", "Ain Kihel", "Oulhassa", "Ain Tolba", "El Malah"]
    },
    47: {  # Ghardaia
        "ar": ["غرداية", "متليلي", "بريان", "القرارة", "بني يزقن", "العطف", "المنيعة", "ضاية بن ضحوة", "زلفانة", "سبسب"],
        "fr": ["Ghardaia", "Metlili", "Berriane", "El Guerrara", "Beni Isguen", "El Atteuf", "El Menia", "Dhayet Bendhahoua", "Zelfana", "Sebseb"]
    },
    48: {  # Relizane
        "ar": ["غليزان", "وادي ارهيو", "مازونة", "زمورة", "يلل", "جديوية", "حمري", "عمي موسى", "بلعسل", "مطمر"],
        "fr": ["Relizane", "Oued Rhiou", "Mazouna", "Zemmora", "Yellel", "Djidioua", "Hamri", "Ammi Moussa", "Belassel", "Matmar"]
    },
    49: {  # Timimoun
        "ar": ["تيميمون", "أوقروت", "تنركوك", "شروين", "دلدول", "طلمين"],
        "fr": ["Timimoun", "Aougrout", "Tinerkouk", "Charouine", "Deldoul", "Talmine"]
    },
    50: {  # Bordj Badji Mokhtar
        "ar": ["برج باجي مختار", "تيمياوين"],
        "fr": ["Bordj Badji Mokhtar", "Timiaouine"]
    },
    51: {  # Ouled Djellal
        "ar": ["أولاد جلال", "سيدي خالد", "البسباس", "رأس الميعاد", "الدوسن", "الشعيبة"],
        "fr": ["Ouled Djellal", "Sidi Khaled", "Besbes", "Ras El Miad", "Doucen", "Chaiba"]
    },
    52: {  # Beni Abbes
        "ar": ["بني عباس", "إقلي", "كرزاز", "تيمودي", "الواتة", "بني يخلف", "أولاد خضير"],
        "fr": ["Beni Abbes", "Igli", "Kerzaz", "Timoudi", "El Ouata", "Beni Ikhlef", "Ouled Khoudir"]
    },
    53: {  # In Salah
        "ar": ["عين صالح", "إين غار", "فقارة الزاوية"],
        "fr": ["In Salah", "In Ghar", "Foggaret Ezzoua"]
    },
    54: {  # In Guezzam
        "ar": ["عين قزام", "تين زواتين"],
        "fr": ["In Guezzam", "Tin Zaouatine"]
    },
    55: {  # Touggourt
        "ar": ["تقرت", "تماسين", "النزلة", "بلدة عمر", "الطيبات", "المنقر", "بن ناصر", "سيدي سليمان"],
        "fr": ["Touggourt", "Temacine", "Nezla", "Blidet Amor", "Taibet", "El Mennguer", "Benaceur", "Sidi Slimane"]
    },
    56: {  # Djanet
        "ar": ["جانت", "برج الحواس"],
        "fr": ["Djanet", "Bordj El Haouas"]
    },
    57: {  # El M'Ghair
        "ar": ["المغير", "جامعة", "سيدي خليل", "أم الطيور", "المرارة", "تندلة"],
        "fr": ["El M'Ghair", "Djamaa", "Sidi Khellil", "Oum Touyour", "El Mrara", "Tendla"]
    },
    58: {  # El Meniaa
        "ar": ["المنيعة", "حاسي الفحل", "حاسي القارة"],
        "fr": ["El Meniaa", "Hassi El Gara", "Hassi Fehal"]
    },
    59: {  # Aflou
        "ar": ["آفلو", "سيدي بوزيد", "تاجرونة", "الغيشة", "سبقاق", "تاويالة", "بريدة"],
        "fr": ["Aflou", "Sidi Bouzid", "Tadjerouna", "El Ghicha", "Sebgag", "Taouiala", "Brida"]
    },
    60: {  # Barika
        "ar": ["بريكة", "بيطام", "أمدوكال", "أولاد عمار", "سفيان"],
        "fr": ["Barika", "Bitam", "M'doukal", "Ouled Ammar", "Soufiane"]
    },
    61: {  # El Kantara
        "ar": ["القنطرة", "عين زعطوط", "لوطاية"],
        "fr": ["El Kantara", "Ain Zaatout", "El Outaya"]
    },
    62: {  # Bir El Ater
        "ar": ["بئر العاتر", "نقرين", "صفصاف الوسرى", "فركان", "أم علي"],
        "fr": ["Bir El Ater", "Negrine", "Safsaf El Ouesra", "Ferkane", "Oum Ali"]
    },
    63: {  # El Aricha
        "ar": ["العريشة", "القور", "البويهي"],
        "fr": ["El Aricha", "El Gor", "El Bouihi"]
    },
    64: {  # Ksar Chellala
        "ar": ["قصر الشلالة", "زمالة الأمير عبد القادر", "الرشايقة", "سرغين"],
        "fr": ["Ksar Chellala", "Zmalet El Emir Abdelkader", "Rechaiga", "Serghine"]
    },
    65: {  # Ain Oussera
        "ar": ["عين وسارة", "البيرين", "القرنيني", "بنهار"],
        "fr": ["Ain Oussera", "Birine", "Guernini", "Benhar"]
    },
    66: {  # Messaad
        "ar": ["مسعد", "دلدول", "سيدي بايزيد", "فيض البطمة", "عمورة", "سلمانة"],
        "fr": ["Messaad", "Deldoul", "Sidi Baizid", "Faidh El Botma", "Amourah", "Selmana"]
    },
    67: {  # Ksar El Boukhari
        "ar": ["قصر البخاري", "مفتاح", "سانق", "أولاد هلال", "بوغزول"],
        "fr": ["Ksar El Boukhari", "Meftah", "Saneg", "Ouled Hellal", "Boughzoul"]
    },
    68: {  # Bou Saada
        "ar": ["بوسعادة", "بن سرور", "الهامل", "تامسة", "ولماس", "محمد بوضياف"],
        "fr": ["Bou Saada", "Ben Srour", "El Hamel", "Tamsa", "Oultene", "Mohamed Boudiaf"]
    },
    69: {  # El Abiodh Sidi Cheikh
        "ar": ["الأبيض سيدي الشيخ", "بريزينة", "البنود", "عين العراك", "الشقيق"],
        "fr": ["El Abiodh Sidi Cheikh", "Brezina", "El Bnoude", "Ain El Orak", "El Kheiter"]
    }
}


def main():
    root = Path(__file__).resolve().parent.parent
    wilayas_file = root / "data" / "wilayas.json"

    with open(wilayas_file, "r", encoding="utf-8") as f:
        wilayas = json.load(f)

    updated_count = 0
    total_communes = 0

    for w in wilayas:
        code = w["code"]
        if code in COMMUNES_BY_WILAYA:
            c_data = COMMUNES_BY_WILAYA[code]
            w["communes_sample"] = c_data["ar"]
            w["communes_fr_sample"] = c_data["fr"]
            updated_count += 1
            total_communes += len(c_data["ar"])

    with open(wilayas_file, "w", encoding="utf-8") as f:
        json.dump(wilayas, f, ensure_ascii=False, indent=2)

    print(f"[OK] Updated {updated_count} wilayas with {total_communes} major Algerian communes!")


if __name__ == "__main__":
    main()
