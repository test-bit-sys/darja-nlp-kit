"""Builds a standalone, zero-dependency Web Playground for GitHub Pages in docs/index.html."""
import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    data_dir = root / 'data'
    docs_dir = root / 'docs'
    docs_dir.mkdir(parents=True, exist_ok=True)

    with open(data_dir / 'stopwords.json', 'r', encoding='utf-8') as f:
        stopwords_data = json.load(f)

    with open(data_dir / 'lexicon.json', 'r', encoding='utf-8') as f:
        lexicon_data = json.load(f)

    with open(data_dir / 'arabizi_rules.json', 'r', encoding='utf-8') as f:
        arabizi_rules = json.load(f)

    with open(data_dir / 'wilayas.json', 'r', encoding='utf-8') as f:
        wilayas_data = json.load(f)

    html_content = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>darja-nlp-kit | Algerian NLP Playground</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0b0f19;
      --card-bg: #111827;
      --card-border: #1f293d;
      --primary: #10b981;
      --primary-hover: #059669;
      --primary-glow: rgba(16, 185, 129, 0.25);
      --crimson: #ef4444;
      --cyan: #06b6d4;
      --text-main: #f3f4f6;
      --text-muted: #9ca3af;
      --accent: #3b82f6;
      --radius: 16px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Cairo', system-ui, -apple-system, sans-serif;
    }}

    body {{
      background-color: var(--bg);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      line-height: 1.6;
    }}

    .container {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 30px 20px 60px;
      width: 100%;
    }}

    /* Header */
    header {{
      text-align: center;
      margin-bottom: 40px;
    }}

    .logo-badge {{
      display: inline-flex;
      align-items: center;
      gap: 12px;
      padding: 8px 18px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 16px;
    }}

    .logo-badge span {{
      background: var(--primary);
      color: #000;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 11px;
    }}

    h1 {{
      font-size: 2.8rem;
      font-weight: 900;
      letter-spacing: -1px;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #ffffff 0%, #10b981 50%, #06b6d4 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    p.subtitle {{
      color: var(--text-muted);
      font-size: 1.15rem;
      max-width: 650px;
      margin: 0 auto 20px;
    }}

    .links-bar {{
      display: flex;
      justify-content: center;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .btn-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 16px;
      border-radius: 10px;
      background: #1e293b;
      color: #e2e8f0;
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid #334155;
      transition: all 0.2s ease;
    }}

    .btn-link:hover {{
      background: #334155;
      color: #fff;
      transform: translateY(-2px);
    }}

    /* Main Box */
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 24px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
      margin-bottom: 24px;
    }}

    .input-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}

    .input-header label {{
      font-weight: 700;
      font-size: 1rem;
      color: #e5e7eb;
    }}

    .char-count {{
      font-size: 12px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
    }}

    textarea {{
      width: 100%;
      height: 110px;
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 12px;
      padding: 14px 16px;
      color: #f8fafc;
      font-size: 1.1rem;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s;
    }}

    textarea:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-glow);
    }}

    /* Quick Samples */
    .samples-bar {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 14px;
      flex-wrap: wrap;
    }}

    .samples-label {{
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
    }}

    .sample-chip {{
      background: #1e293b;
      border: 1px solid #334155;
      padding: 5px 12px;
      border-radius: 8px;
      font-size: 12px;
      cursor: pointer;
      color: #cbd5e1;
      transition: all 0.15s;
    }}

    .sample-chip:hover {{
      background: var(--primary);
      color: #000;
      border-color: var(--primary);
    }}

    /* Grid layout for results */
    .results-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
      margin-top: 24px;
    }}

    .section-title {{
      font-size: 0.95rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .section-title::before {{
      content: '';
      width: 8px;
      height: 8px;
      background: var(--primary);
      border-radius: 50%;
      display: inline-block;
    }}

    /* Sentiment Card */
    .sentiment-banner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      border-radius: 12px;
      margin-bottom: 16px;
      background: #1e293b;
    }}

    .sentiment-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 1.1rem;
      font-weight: 800;
      padding: 6px 16px;
      border-radius: 999px;
    }}

    .badge-positive {{
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border: 1px solid #10b981;
    }}

    .badge-negative {{
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
      border: 1px solid #ef4444;
    }}

    .badge-mixed {{
      background: rgba(245, 158, 11, 0.2);
      color: #fbbf24;
      border: 1px solid #f59e0b;
    }}

    .badge-neutral {{
      background: rgba(148, 163, 184, 0.2);
      color: #cbd5e1;
      border: 1px solid #64748b;
    }}

    .score-display {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 1.3rem;
      font-weight: 700;
    }}

    .tokens-pill-box {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }}

    .token-pill {{
      padding: 3px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
    }}

    .token-pos {{
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .token-neg {{
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }}

    /* Wilayas & Entities Cards */
    .entity-tag {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 14px;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 10px;
      margin-right: 8px;
      margin-bottom: 8px;
      font-size: 13px;
    }}

    .entity-code {{
      background: var(--primary);
      color: #000;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 6px;
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
    }}

    .payment-tag {{
      background: rgba(6, 182, 212, 0.15);
      border: 1px solid rgba(6, 182, 212, 0.4);
      color: #38bdf8;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      display: inline-block;
      margin-bottom: 6px;
    }}

    .price-tag {{
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fcd34d;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      display: inline-block;
      margin-bottom: 6px;
    }}

    .carrier-tag {{
      background: rgba(168, 85, 247, 0.15);
      border: 1px solid rgba(168, 85, 247, 0.4);
      color: #c084fc;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      display: inline-block;
      margin-bottom: 6px;
    }}

    .mode-tag {{
      background: rgba(34, 197, 94, 0.15);
      border: 1px solid rgba(34, 197, 94, 0.4);
      color: #4ade80;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      display: inline-block;
      margin-bottom: 6px;
    }}

    .phone-tag {{
      background: rgba(236, 72, 153, 0.15);
      border: 1px solid rgba(236, 72, 153, 0.4);
      color: #f472b6;
      padding: 6px 12px;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      font-weight: 700;
      display: inline-block;
      margin-bottom: 6px;
    }}

    /* Text display boxes */
    .code-box {{
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 12px 14px;
      font-size: 14px;
      color: #e2e8f0;
      word-break: break-word;
      min-height: 48px;
      margin-bottom: 12px;
    }}

    /* Dialect Meter */
    .dialect-badge {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 10px 18px;
      background: #1e293b;
      border: 1px solid #3b82f6;
      border-radius: 12px;
      color: #60a5fa;
      font-weight: 800;
      font-size: 1.1rem;
    }}

    .empty-state {{
      color: var(--text-muted);
      font-size: 13px;
      font-style: italic;
    }}

    footer {{
      text-align: center;
      margin-top: auto;
      padding: 30px 20px;
      color: var(--text-muted);
      font-size: 13px;
      border-top: 1px solid var(--card-border);
    }}
  </style>
</head>
<body>

  <div class="container">
    <header>
      <div class="logo-badge">
        <span>DZ Open Suite</span>
        <span>Zero-Dependency</span>
        <span>69 Wilayas</span>
      </div>
      <h1>darja-nlp-kit</h1>
      <p class="subtitle">مختبر المعالجة اللغوية الطبيعية للهجة الجزائرية (الدارجة، الأرابيزي، والتناوب اللغوي الفرنسي)</p>
      <div class="links-bar">
        <a href="https://github.com/test-bit-sys/darja-nlp-kit" target="_blank" class="btn-link">
          ⭐ مستودع GitHub
        </a>
        <a href="https://pypi.org/project/darja-nlp-kit/" target="_blank" class="btn-link">
          📦 PyPI Package
        </a>
        <a href="https://www.npmjs.com/package/@dz-open-suite/darja-nlp-kit" target="_blank" class="btn-link">
          📦 npm Package
        </a>
      </div>
    </header>

    <div class="card">
      <div class="input-header">
        <label for="textInput">اكتب أو الصق نصاً بالدارجة الجزائرية أو الأرابيزي:</label>
        <span class="char-count" id="charCount">0 حرف</span>
      </div>
      <textarea id="textInput" placeholder="مثال: produit mli7 bzaf walakin livraison l wahran rotar chwiya, prix 4500 DA w khlass b baridimob">السلعة هاااااايلة بزاااااف و الخدمة فور، يعطيك الصحة! توصيل لبوسعادة و نخلصك بـ baridimob السعر زوج ملاين</textarea>
      
      <div class="samples-bar">
        <span class="samples-label">نماذج سريعة للتجربة:</span>
        <button class="sample-chip" onclick="loadSample(0)">🛒 تعليق متجر إيجابي</button>
        <button class="sample-chip" onclick="loadSample(1)">⚠️ تعليق سلبي ونفي معكوس</button>
        <button class="sample-chip" onclick="loadSample(2)">🔤 أرابيزي مع فرنسية وسعر</button>
        <button class="sample-chip" onclick="loadSample(3)">📍 لهجة وهران والولاية 31</button>
        <button class="sample-chip" onclick="loadSample(4)">📍 لهجة قسنطينة وسيرتا</button>
      </div>
    </div>

    <div class="results-grid">
      <!-- 1. Sentiment Card -->
      <div class="card">
        <div class="section-title">تحليل المشاعر (Sentiment Analysis)</div>
        <div class="sentiment-banner">
          <div id="sentimentBadge" class="sentiment-badge badge-positive">إيجابي (+)</div>
          <div class="score-display" id="sentimentScore">+0.90</div>
        </div>
        <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">الكلمات المؤثرة في التقييم:</div>
        <div id="tokensBox" class="tokens-pill-box"></div>
        <div id="negationFlag" style="margin-top: 10px; font-size: 12px; color: var(--cyan); display: none;">
          ⚡ تم رصد نفي معكوس في الجملة (Negation Inversion Active)
        </div>
      </div>

      <!-- 2. Wilayas (69) & Geo Card -->
      <div class="card">
        <div class="section-title">الولايات الجزائرية المرصودة (69 Wilayas - Law 26-06)</div>
        <div id="wilayasBox"></div>
      </div>

      <!-- 3. Payments & Prices Card -->
      <div class="card">
        <div class="section-title">طرق الدفع والأسعار المستخرجة (Payments & Prices)</div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">طرق الدفع:</div>
          <div id="paymentsBox"></div>
        </div>
        <div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">الأسعار والمبالغ:</div>
          <div id="pricesBox"></div>
        </div>
      </div>

      <!-- 4. Logistics & Phone Card -->
      <div class="card">
        <div class="section-title">شركات التوصيل ونمط الاستلام والهاتف (Logistics & Contact)</div>
        <div style="margin-bottom: 10px;">
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">شركة التوصيل:</div>
          <div id="deliveriesBox"></div>
        </div>
        <div style="margin-bottom: 10px;">
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">نمط التوصيل:</div>
          <div id="deliveryModeBox"></div>
        </div>
        <div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">أرقام الهاتف المرصودة:</div>
          <div id="phonesBox"></div>
        </div>
      </div>

      <!-- 5. Dialect Card -->
      <div class="card">
        <div class="section-title">كشف اللهجة الجهوية (Regional Dialect)</div>
        <div style="margin-bottom: 14px;">
          <div id="dialectBadge" class="dialect-badge">الوسط الجزائري (CENTER)</div>
        </div>
        <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">المؤشرات اللغوية المرصودة:</div>
        <div id="dialectMarkers" class="tokens-pill-box"></div>
      </div>

      <!-- 6. Arabizi & Normalization -->
      <div class="card" style="grid-column: 1 / -1;">
        <div class="section-title">معالجة الأرابيزي والتطبيع (Arabizi Transliteration & Normalizer)</div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
          <div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">تحويل الأرابيزي (مع الحفاظ على الكلمات الفرنسية والأرقام):</div>
            <div id="arabiziBox" class="code-box"></div>
          </div>
          <div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">النص بعد التطبيع وتخفيف التمطيط (Normalized):</div>
            <div id="normalizedBox" class="code-box"></div>
          </div>
          <div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">النص بعد تصفية الكلمات الشائعة (Stopwords Filtered):</div>
            <div id="stopwordsBox" class="code-box"></div>
          </div>
        </div>
      </div>

      <!-- 7. AI Agent Customer Assistant Simulator -->
      <div class="card" style="grid-column: 1 / -1; border-color: rgba(59, 130, 246, 0.4); background: radial-gradient(circle at top left, #0f1c3f, #111827);">
        <div class="section-title" style="color: #60a5fa;">🤖 محاكي وكيل الذكاء الاصطناعي الجزائري (AI Agent Assistant Simulator)</div>
        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 14px;">
          كيف يستقبل نموذج الذكاء الاصطناعي (مثل GPT-4o / Claude / Gemini) هذا الزبون عبر <strong>darja-nlp-kit</strong>، وكيف يطابق لهجته بدقة وحقائق مؤكدة دون أي هلوسة:
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px;">
          <div>
            <div style="font-size: 12px; color: #93c5fd; font-weight: 700; margin-bottom: 6px;">🧠 الـ System Prompt المحقون للذكاء الاصطناعي:</div>
            <pre id="agentPromptBox" style="background:#080c14; border:1px solid #1e293b; border-radius:10px; padding:12px; font-family:'JetBrains Mono',monospace; font-size:11px; color:#cbd5e1; max-height:170px; overflow-y:auto; white-space:pre-wrap;"></pre>
          </div>
          <div>
            <div style="font-size: 12px; color: #34d399; font-weight: 700; margin-bottom: 6px;">💬 رد الذكاء الاصطناعي البشري الواقعي (AI Agent Response):</div>
            <div id="agentReplyBox" style="background:#080c14; border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:16px; font-size:15px; color:#f0fdf4; line-height:1.7; min-height:80px; display:flex; align-items:center;"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <footer>
    <p><strong>darja-nlp-kit</strong> — Zero-dependency Algerian Darja NLP toolkit. Open Source under MIT License.</p>
    <p style="margin-top: 4px;">Developed as part of the <strong>DZ Open Suite</strong> ecosystem.</p>
  </footer>

  <script>
    // Embedded Linguistic Datasets
    const STOPWORDS_DATA = {json.dumps(stopwords_data, ensure_ascii=False)};
    const LEXICON_DATA = {json.dumps(lexicon_data, ensure_ascii=False)};
    const ARABIZI_RULES = {json.dumps(arabizi_rules, ensure_ascii=False)};
    const WILAYAS_DATA = {json.dumps(wilayas_data, ensure_ascii=False)};

    // Core Algorithms
    const ALEF_VARIANTS = /[\\u0622\\u0623\\u0625]/g;
    const TA_MARBUTA = /\\u0629/g;
    const ALEF_MAQSURA = /\\u0649/g;
    const TASHKEEL = /[\\u0610-\\u061A\\u064B-\\u065F\\u0670\\u06D6-\\u06DC\\u06DF-\\u06E4\\u06E7\\u06E8\\u06EA-\\u06ED]/g;
    const TATWEEL = /\\u0640/g;
    const ARABIC_ELONGATION = /(.)\\1{{2,}}/g;
    const LATIN_ELONGATION = /([a-zA-Z])\\1{{2,}}/g;
    const MULTI_SPACE = /\\s+/g;
    const MULTI_PUNCT = /([!?.]){{2,}}/g;
    const VALID_DOUBLES = new Set(['ll','ss','mm','nn','dd','tt','rr','ff','cc','pp','bb','gg','zz','ee','oo','aa']);

    function normalize(text) {{
      if (!text) return '';
      let res = text.replace(ALEF_VARIANTS, '\\u0627')
                    .replace(TA_MARBUTA, '\\u0647')
                    .replace(ALEF_MAQSURA, '\\u064A')
                    .replace(TASHKEEL, '')
                    .replace(TATWEEL, '')
                    .replace(ARABIC_ELONGATION, '$1')
                    .replace(LATIN_ELONGATION, (m, c) => VALID_DOUBLES.has(c.toLowerCase()+c.toLowerCase()) ? c+c : c)
                    .replace(MULTI_SPACE, ' ')
                    .replace(MULTI_PUNCT, '$1')
                    .trim();
      return res;
    }}

    function isFrenchWord(word) {{
      const lower = word.toLowerCase();
      if (ARABIZI_RULES.french_whitelist.includes(lower)) return true;
      for (const suffix of ARABIZI_RULES.french_suffixes) {{
        if (lower.endsWith(suffix) && lower.length > suffix.length + 2) return true;
      }}
      return false;
    }}

    function arabiziToArabic(text) {{
      if (!text) return '';
      const tokens = text.split(/(\\s+)/);
      const res = [];
      for (const token of tokens) {{
        if (/^\\s+$/.test(token) || !token) {{ res.push(token); continue; }}
        if (/^[\\u0600-\\u06FF]/.test(token)) {{ res.push(token); continue; }}
        if (isFrenchWord(token) || /^\\d+$/.test(token)) {{ res.push(token); continue; }}

        const lower = token.toLowerCase();
        if (ARABIZI_RULES.overrides[lower]) {{ res.push(ARABIZI_RULES.overrides[lower]); continue; }}

        let translit = '';
        let i = 0;
        while (i < lower.length) {{
          let matched = false;
          if (i + 1 < lower.length) {{
            const dg = lower.substring(i, i + 2);
            if (ARABIZI_RULES.digraphs[dg]) {{ translit += ARABIZI_RULES.digraphs[dg]; i += 2; matched = true; }}
          }}
          if (!matched) {{
            const ch = lower[i];
            if (/[0-9]/.test(ch) && ARABIZI_RULES.numbers[ch]) {{
              const before = i > 0 ? lower[i-1] : '';
              const after = i < lower.length - 1 ? lower[i+1] : '';
              const hasLetter = /[a-zA-Z\\u0600-\\u06FF]/.test(before) || /[a-zA-Z\\u0600-\\u06FF]/.test(after);
              translit += hasLetter ? ARABIZI_RULES.numbers[ch] : ch;
            }} else if (ARABIZI_RULES.singles[ch]) {{
              translit += ARABIZI_RULES.singles[ch];
            }} else {{
              translit += ch;
            }}
            i++;
          }}
        }}
        res.push(translit);
      }}
      return res.join('');
    }}

    function tokenize(text) {{
      if (!text) return {{ tokens: [], negations: [] }};
      const raw = text.split(/[\\s,.!?;:()[\\]{{}}"\'`\\u060C\\u061B\\u061F\\u0640]+/).filter(t => t.length > 0);
      const tokens = [];
      const negations = [];
      for (const token of raw) {{
        const m = token.match(/^ما(.+?)ش$/) || token.match(/^ma(.+?)ch$/i);
        if (m && m[1].length >= 2) {{
          negations.push({{ original: token, root: m[1], negated: true }});
        }}
        tokens.push(token);
      }}
      return {{ tokens, negations }};
    }}

    const STOPWORDS_SET = new Set();
    Object.values(STOPWORDS_DATA).forEach(list => list.forEach(w => {{ STOPWORDS_SET.add(w); STOPWORDS_SET.add(w.toLowerCase()); }}));
    const AR_PREFIXES = ['بال', 'وال', 'فال', 'كال', 'ال', 'و', 'ب', 'ل', 'ف', 'ك'];
    const AR_SUFFIXES = ['ين', 'ات', 'ة', 'ه'];

    function stripPrefix(token) {{
      for (const p of AR_PREFIXES) {{
        if (token.startsWith(p) && token.length > p.length + 1) return token.slice(p.length);
      }}
      return null;
    }}
    function stripSuffix(token) {{
      for (const s of AR_SUFFIXES) {{
        if (token.endsWith(s) && token.length > s.length + 1) return token.slice(0, -s.length);
      }}
      return null;
    }}

    function removeStopwords(text) {{
      const {{ tokens }} = tokenize(text);
      return tokens.filter(t => {{
        if (STOPWORDS_SET.has(t) || STOPWORDS_SET.has(t.toLowerCase())) return false;
        const sp = stripPrefix(t);
        if (sp && (STOPWORDS_SET.has(sp) || STOPWORDS_SET.has(sp.toLowerCase()))) return false;
        return true;
      }}).join(' ');
    }}

    function lookupScore(word) {{
      const lower = word.toLowerCase();
      if (LEXICON_DATA.positive[word] !== undefined) return LEXICON_DATA.positive[word];
      if (LEXICON_DATA.positive[lower] !== undefined) return LEXICON_DATA.positive[lower];
      if (LEXICON_DATA.negative[word] !== undefined) return LEXICON_DATA.negative[word];
      if (LEXICON_DATA.negative[lower] !== undefined) return LEXICON_DATA.negative[lower];
      return null;
    }}

    function findScore(token) {{
      let s = lookupScore(token);
      if (s !== null) return s;
      const sp = stripPrefix(token);
      if (sp) {{
        s = lookupScore(sp);
        if (s !== null) return s;
        const sBoth = stripSuffix(sp);
        if (sBoth) {{
          s = lookupScore(sBoth);
          if (s !== null) return s;
        }}
      }}
      const ss = stripSuffix(token);
      if (ss) {{
        s = lookupScore(ss);
        if (s !== null) return s;
      }}
      return null;
    }}

    function analyzeSentiment(text) {{
      if (!text) return {{ score: 0, label: 'NEUTRAL', positiveTokens: [], negativeTokens: [], negated: false }};
      const {{ tokens, negations }} = tokenize(text);
      const pos = [];
      const neg = [];
      let total = 0;
      let count = 0;
      let hasNeg = false;
      const circum = new Set(negations.map(n => n.original));

      for (let i = 0; i < tokens.length; i++) {{
        const t = tokens[i];
        if (circum.has(t)) {{
          hasNeg = true;
          const negInfo = negations.find(n => n.original === t);
          if (negInfo) {{
            const rScore = findScore(negInfo.root);
            if (rScore !== null) {{
              const flipped = rScore * -0.8;
              total += flipped; count++;
              if (flipped > 0) pos.push(t); else neg.push(t);
              continue;
            }}
          }}
        }}

        let score = findScore(t);
        if (score === null) continue;

        const prev = i > 0 ? tokens[i-1] : null;
        if (prev && (LEXICON_DATA.negators.includes(prev) || LEXICON_DATA.negators.includes(prev.toLowerCase()))) {{
          score = score * -0.8;
          hasNeg = true;
        }}

        const next = i + 1 < tokens.length ? tokens[i+1] : null;
        if (next && LEXICON_DATA.intensifiers[next]) score *= LEXICON_DATA.intensifiers[next];
        if (prev && LEXICON_DATA.intensifiers[prev] && !LEXICON_DATA.negators.includes(prev)) score *= LEXICON_DATA.intensifiers[prev];

        total += score;
        count++;
        if (score > 0) pos.push(t); else if (score < 0) neg.push(t);
      }}

      const finalScore = count > 0 ? Math.max(-1, Math.min(1, total / count)) : 0;
      const rounded = Math.round(finalScore * 100) / 100;
      let label = 'NEUTRAL';
      if (pos.length > 0 && neg.length > 0) label = 'MIXED';
      else if (rounded > 0.05) label = 'POSITIVE';
      else if (rounded < -0.05) label = 'NEGATIVE';

      return {{ score: rounded, label, positiveTokens: pos, negativeTokens: neg, negated: hasNeg }};
    }}

    function extractEntities(text) {{
      const wilayas = [];
      const addedCodes = new Set();
      const lower = text.toLowerCase();

      // Wilayas by code
      const codeReg = /(?:wilaya|w|ولاية|ولايه|l)\\s*([0-6]?[0-9])\\b/gi;
      let m;
      while ((m = codeReg.exec(text)) !== null) {{
        const num = parseInt(m[1], 10);
        if (num >= 1 && num <= 69 && !addedCodes.has(num)) {{
          const w = WILAYAS_DATA.find(x => x.code === num);
          if (w) {{ addedCodes.add(num); wilayas.push({{ ...w, matchedText: m[0] }}); }}
        }}
      }}

      // Wilayas by names/aliases
      for (const w of WILAYAS_DATA) {{
        if (addedCodes.has(w.code)) continue;
        const cands = [w.name_ar, w.name_fr, ...(w.aliases || [])];
        for (const cand of cands) {{
          if (!cand || cand.length < 2) continue;
          const cLower = cand.toLowerCase();
          const escaped = cLower.replace(/[-[\\]{{}}()*+?.,\\\\^$|#\\s]/g, '\\\\$&');
          const reg = new RegExp(`(^|\\s|[.,!?;:()])${{escaped}}($|\\s|[.,!?;:()])`, 'i');
          if (reg.test(lower) || (cLower.length > 3 && lower.includes(cLower))) {{
            addedCodes.add(w.code);
            wilayas.push({{ ...w, matchedText: cand }});
            break;
          }}
        }}
      }}

      // Payments
      const payments = [];
      const paymentPatterns = [
        {{ type: 'BARIDIMOB', label: 'BaridiMob (بريدي موب)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(baridimob|baridi\\s*mob|بريدي\\s*موب|بريديموب)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ type: 'EDAHABIA', label: 'Edahabia Card (البطاقة الذهبية)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(edahabia|dahabia|carte\\s*edahabia|الذهبيه|الذهبية|بالذهبية|بالذهبيه|بطاقة\\s*الذهبيه|لاكارط\\s*الذهبيه)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ type: 'CCP', label: 'CCP Account (حساب بريدي)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(ccp|سي\\s*سي\\s*بي|حساب\\s*بريدي|شيك\\s*بريدي|virement\\s*ccp)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ type: 'COD', label: 'Cash on Delivery (الدفع عند الاستلام)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(cod|cash\\s*on\\s*delivery|main\\s*[aà]\\s*main|الدفع\\s*عند\\s*الاستلام|كاش\\s*عند\\s*الاستلام|خلص\\s*كي\\s*تلحقك|كاش|يد\\s*بيد)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
      ];
      for (const p of paymentPatterns) {{
        const match = text.match(p.reg);
        if (match) payments.push({{ type: p.type, label: p.label, matched: match[0].trim() }});
      }}

      // Prices
      const prices = [];
      const priceNumReg = /(?:^|\\s|[^\\w\\u0600-\\u06FF])(\\d+(?:[.,]\\d+)?)\\s*(da|dzd|دج|دينار|الف|ألف|alf)(?=$|\\s|[^\\w\\u0600-\\u06FF])/gi;
      let pm;
      while ((pm = priceNumReg.exec(text)) !== null) {{
        let val = parseFloat(pm[1].replace(',', '.'));
        const u = pm[2].toLowerCase();
        if (u === 'الف' || u === 'ألف' || u === 'alf') val *= 1000;
        prices.push({{ raw: pm[0].trim(), amount: val }});
      }}

      // Dynamic millions (e.g. 2 mlayen, 3 ملاين)
      const dynMilReg = /(?:^|\\s|[^\\w\\u0600-\\u06FF])(\\d+(?:[.,]\\d+)?)\\s*(?:ملاين|ملايين|مليون|mlyon|mlayen|mlayin)(?=$|\\s|[^\\w\\u0600-\\u06FF])/gi;
      let dmDyn;
      while ((dmDyn = dynMilReg.exec(text)) !== null) {{
        const val = parseFloat(dmDyn[1].replace(',', '.')) * 10000;
        prices.push({{ raw: dmDyn[0].trim(), amount: val }});
      }}

      const darjaAmounts = [
        {{ reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(مية\\s*الف|100\\s*الف|mya|myat\\s*alf)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i, val: 1000 }},
        {{ reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(ميتين\\s*الف|200\\s*الف|mitin\\s*alf)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i, val: 2000 }},
        {{ reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(خمسمية\\s*الف|500\\s*الف|khams\\s*mya|500\\s*alf)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i, val: 5000 }},
        {{ reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(مليون|mlyon|1\\s*mlyon)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i, val: 10000 }},
        {{ reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(زوج\\s*ملاين|زوج\\s*ملايين|zoudj\\s*mlayen|zouj\\s*mlayen)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i, val: 20000 }},
        {{ reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(خمس\\s*ملاين|khams\\s*mlayen)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i, val: 50000 }},
        {{ reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(عشر\\s*ملاين|3achr\\s*mlayen)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i, val: 100000 }},
      ];
      for (const item of darjaAmounts) {{
        const dm = text.match(item.reg);
        if (dm) prices.push({{ raw: dm[0].trim(), amount: item.val }});
      }}

      // Deliveries
      const deliveries = [];
      const deliveryPatterns = [
        {{ company: 'YALIDINE', label: 'Yalidine Express (ياليدين)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(yalidine|yalidin|ياليدين)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ company: 'ZR_EXPRESS', label: 'ZR Express (زد ار اكسبرس)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(zr\\s*express|zr|زد\\s*ار\\s*اكسبرس|زد\\s*ار)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ company: 'MAYSTRO', label: 'Maystro Delivery (مايسترو)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(maystro\\s*delivery|maystro|مايسترو)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ company: 'PROCOLIS', label: 'Procolis (بروكولي)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(procolis|pro\\s*colis|بروكولي|بروكوليس)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ company: 'EMS', label: 'EMS Algérie Poste (البريد السريع)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(ems|ems\\s*algerie|البريد\\s*السريع)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ company: 'KAZITOUR', label: 'Kazitour Express (كازيتور)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(kazitour|kazi\\s*tour|كازيتور)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ company: 'GUEPEX', label: 'Guepex Express (قيباكس)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(guepex|قيباكس)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
      ];
      for (const d of deliveryPatterns) {{
        const m = text.match(d.reg);
        if (m) deliveries.push({{ company: d.company, label: d.label, matched: m[0].trim() }});
      }}

      // Delivery Mode
      let deliveryMode = null;
      const modePatterns = [
        {{ mode: 'STOP_DESK', label: 'Stop Desk (استلام من المكتب)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(stop\\s*desk|stopdesk|سطوب\\s*ديسك|ستوب\\s*ديسك|المكتب|فالبيرو|في\\s*البيرو|agence)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
        {{ mode: 'HOME_DELIVERY', label: 'Home Delivery (توصيل للمنزل)', reg: /(?:^|\\s|[^\\w\\u0600-\\u06FF])(a\\s*domicile|[aà]\\s*domicile|للدار|لباب\\s*الدار|توصيل\\s*للمنزل|توصيل\\s*للدار|فالدار)(?=$|\\s|[^\\w\\u0600-\\u06FF])/i }},
      ];
      for (const dm of modePatterns) {{
        const m = text.match(dm.reg);
        if (m) {{ deliveryMode = dm.label; break; }}
      }}

      // Phones
      const phones = [];
      const phoneReg = /(?:^|\\s|[^\\w\\u0600-\\u06FF])((?:\\+213|00213|0)\\s*(?:[5-7]|2[0-9]|3[0-9]|4[0-9])(?:[\\s.-]?\\d){{8}})(?=$|\\s|[^\\w\\u0600-\\u06FF])/gi;
      let phMatch;
      while ((phMatch = phoneReg.exec(text)) !== null) {{
        let raw = phMatch[1].trim();
        let norm = raw.replace(/[\\s.-]/g, '');
        if (norm.startsWith('00213')) norm = '0' + norm.slice(5);
        else if (norm.startsWith('+213')) norm = '0' + norm.slice(4);
        phones.push({{ raw, normalized: norm }});
      }}

      return {{ wilayas, payments, prices, deliveries, deliveryMode, phones }};
    }}

    function detectDialect(text) {{
      const markers = {{
        WEST: ['شوالا', 'شاكاين', 'شا', 'غايا', 'باغي', 'حرز', 'راك عاقل', 'شراكم', 'كيراك', 'كيراكم', 'درك', 'chwala', 'chakayn', 'ghaya', 'baghi', 'kirak', 'drk'],
        EAST: ['واشنهي', 'قداش', 'ياسر', 'ضرك', 'زي', 'باهي', 'علاشنهي', 'واشبيك', 'كفاه', 'ضروك', 'سيرتا', 'بونة', '9dach', 'yaser', 'bahi'],
        CENTER: ['واشنو', 'حكاية', 'دروك', 'هكدا', 'هكداك', 'حوايج', 'البهجة', 'العاصمة', 'دزاير', 'wachnou', 'hakda', 'hakdak'],
        SOUTH: ['واه', 'لاه', 'حتة', 'سوف', 'ميزاب', 'غرداية', 'ادرار', 'wah', 'lah', '7ata'],
      }};
      const lower = text.toLowerCase();
      const scores = {{ WEST: [], EAST: [], CENTER: [], SOUTH: [] }};
      for (const [reg, words] of Object.entries(markers)) {{
        for (const w of words) {{
          if (lower.includes(w.toLowerCase())) scores[reg].push(w);
        }}
      }}
      let top = 'GENERAL_DARJA';
      let max = 0;
      let detected = [];
      for (const [r, list] of Object.entries(scores)) {{
        if (list.length > max) {{ max = list.length; top = r; detected = list; }}
      }}
      return {{
        region: top,
        confidence: max > 0 ? Math.min(0.99, Math.round((0.6 + max * 0.15) * 100) / 100) : 0.5,
        detectedMarkers: detected,
      }};
    }}

    // UI Controller
    const inputArea = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');

    const SAMPLES = [
      "salam khoya rani hab nchrih b 2 mlayen l Constantine b yalidine stop desk. num ta3i: 0661234567",
      "السلعة هاااااايلة بزاااااف و الخدمة فور، يعطيك الصحة! توصيل لبوسعادة ياليدين ستوب ديسك كلمني في 0661234567",
      "khedma 3ayana w sil3a khorda wlah ma thechmou 7chitohali w l colis ja mfetchech!",
      "شوالا راك باغي خوية غايا درك؟ كاين توصيل للسانية ولاية 31 بـ zr express للدار و نخلصك كاش عند الاستلام",
      "واشنهي هادا قداش يدير ياسر باهي سيرتا نخلصك كاش بـ مية الف"
    ];

    function loadSample(idx) {{
      inputArea.value = SAMPLES[idx];
      processText();
    }}

    function processText() {{
      const text = inputArea.value;
      charCount.textContent = `${{text.length}} حرف`;

      // 1. Sentiment
      const sent = analyzeSentiment(text);
      const sBadge = document.getElementById('sentimentBadge');
      const sScore = document.getElementById('sentimentScore');
      const tokensBox = document.getElementById('tokensBox');
      const negFlag = document.getElementById('negationFlag');

      sScore.textContent = (sent.score >= 0 ? '+' : '') + sent.score.toFixed(2);
      sBadge.className = 'sentiment-badge ' + (
        sent.label === 'POSITIVE' ? 'badge-positive' :
        sent.label === 'NEGATIVE' ? 'badge-negative' :
        sent.label === 'MIXED' ? 'badge-mixed' : 'badge-neutral'
      );
      sBadge.textContent = {{
        POSITIVE: 'إيجابي (+)',
        NEGATIVE: 'سلبي (-)',
        MIXED: 'مختلط (~)',
        NEUTRAL: 'محايد (o)'
      }}[sent.label] || sent.label;

      tokensBox.innerHTML = '';
      sent.positiveTokens.forEach(t => {{
        tokensBox.innerHTML += `<span class="token-pill token-pos">+ ${{t}}</span>`;
      }});
      sent.negativeTokens.forEach(t => {{
        tokensBox.innerHTML += `<span class="token-pill token-neg">- ${{t}}</span>`;
      }});
      if (sent.positiveTokens.length === 0 && sent.negativeTokens.length === 0) {{
        tokensBox.innerHTML = '<span class="empty-state">لا توجد كلمات مشاعر مباشرة</span>';
      }}
      negFlag.style.display = sent.negated ? 'block' : 'none';

      // 2. Entities
      const entities = extractEntities(text);
      const wilayasBox = document.getElementById('wilayasBox');
      const paymentsBox = document.getElementById('paymentsBox');
      const pricesBox = document.getElementById('pricesBox');

      wilayasBox.innerHTML = '';
      if (entities.wilayas.length > 0) {{
        entities.wilayas.forEach(w => {{
          wilayasBox.innerHTML += `
            <div class="entity-tag">
              <span class="entity-code">${{w.code_str || w.code}}</span>
              <strong>${{w.name_ar}}</strong>
              <span style="color:var(--text-muted); font-size:11px;">(${{w.name_fr}})</span>
            </div>
          `;
        }});
      }} else {{
        wilayasBox.innerHTML = '<span class="empty-state">لم يتم رصد ولايات في النص</span>';
      }}

      paymentsBox.innerHTML = '';
      if (entities.payments.length > 0) {{
        entities.payments.forEach(p => {{
          paymentsBox.innerHTML += `<span class="payment-tag">${{p.label}}</span> `;
        }});
      }} else {{
        paymentsBox.innerHTML = '<span class="empty-state">لا توجد وسيلة دفع محددة</span>';
      }}

      pricesBox.innerHTML = '';
      if (entities.prices.length > 0) {{
        entities.prices.forEach(pr => {{
          pricesBox.innerHTML += `<span class="price-tag">${{pr.raw}} &rarr; ${{pr.amount.toLocaleString()}} دج</span> `;
        }});
      }} else {{
        pricesBox.innerHTML = '<span class="empty-state">لا توجد أسعار مرصودة</span>';
      }}

      // Logistics & Phones
      const deliveriesBox = document.getElementById('deliveriesBox');
      const deliveryModeBox = document.getElementById('deliveryModeBox');
      const phonesBox = document.getElementById('phonesBox');

      deliveriesBox.innerHTML = '';
      if (entities.deliveries && entities.deliveries.length > 0) {{
        entities.deliveries.forEach(d => {{
          deliveriesBox.innerHTML += `<span class="carrier-tag">${{d.label}}</span> `;
        }});
      }} else {{
        deliveriesBox.innerHTML = '<span class="empty-state">لم تحدد شركة توصيل</span>';
      }}

      if (entities.deliveryMode) {{
        deliveryModeBox.innerHTML = `<span class="mode-tag">${{entities.deliveryMode}}</span>`;
      }} else {{
        deliveryModeBox.innerHTML = '<span class="empty-state">لم يحدد نمط التوصيل (مكتب / منزل)</span>';
      }}

      phonesBox.innerHTML = '';
      if (entities.phones && entities.phones.length > 0) {{
        entities.phones.forEach(ph => {{
          phonesBox.innerHTML += `<span class="phone-tag">${{ph.raw}} &rarr; ${{ph.normalized}}</span> `;
        }});
      }} else {{
        phonesBox.innerHTML = '<span class="empty-state">لا توجد أرقام هواتف مرصودة</span>';
      }}

      // 3. Dialect
      const dialect = detectDialect(text);
      const dBadge = document.getElementById('dialectBadge');
      const dMarkers = document.getElementById('dialectMarkers');
      const regionNames = {{
        WEST: 'الغرب الجزائري (WEST - وهران وتلمسان)',
        EAST: 'الشرق الجزائري (EAST - قسنطينة وسطيف وعنابة)',
        CENTER: 'الوسط الجزائري (CENTER - الجزائر والبليدة)',
        SOUTH: 'الجنوب الجزائري (SOUTH - الصحراء والواحات)',
        GENERAL_DARJA: 'دارجة جزائرية عامة (GENERAL)'
      }};
      dBadge.textContent = regionNames[dialect.region] || dialect.region;
      dMarkers.innerHTML = '';
      if (dialect.detectedMarkers.length > 0) {{
        dialect.detectedMarkers.forEach(m => {{
          dMarkers.innerHTML += `<span class="token-pill" style="background:#1e293b; color:#60a5fa; border:1px solid #3b82f6;">${{m}}</span>`;
        }});
      }} else {{
        dMarkers.innerHTML = '<span class="empty-state">لا توجد مؤشرات جهوية حصرية</span>';
      }}

      // 4. Arabizi, Normalization, Stopwords
      const arabiziClean = arabiziToArabic(text);
      document.getElementById('arabiziBox').textContent = arabiziClean || '-';
      document.getElementById('normalizedBox').textContent = normalize(text) || '-';
      document.getElementById('stopwordsBox').textContent = removeStopwords(text) || '-';

      // 5. AI Agent Simulator
      const wilayaName = entities.wilayas.length > 0 ? entities.wilayas[0].name_ar + ' (' + entities.wilayas[0].code_str + ')' : null;
      const carrierName = entities.deliveries && entities.deliveries.length > 0 ? entities.deliveries[0].label : null;
      const priceText = entities.prices.length > 0 ? entities.prices[0].amount.toLocaleString() + ' دج' : null;

      const agentPrompt = `[سياق الزبون المستخرج بدقة عبر darja-nlp-kit]:
- الرسالة الأصلية: "${{text}}"
- الترجمة التفسيرية: "${{arabiziClean}}"
- اللهجة المستهدفة: ${{dialect.region}} (${{regionNames[dialect.region] || 'عامة'}})
- المزاج والشعور: ${{sent.label}} (الدرجة: ${{sent.score.toFixed(2)}})
- الولاية المؤكدة: ${{wilayaName || 'غير محددة'}}
- شركة التوصيل: ${{carrierName || 'غير محددة'}}
- نمط التوصيل: ${{entities.deliveryMode || 'غير محدد'}}
- المبالغ بالدينار: ${{priceText || 'غير محددة'}}
- وسائل الدفع: ${{entities.payments.length > 0 ? entities.payments.map(p => p.label).join(', ') : 'غير محددة'}}

[التعليمات]: طابق لهجة الزبون ومزاجه، وأجب بدارجة جزائرية عفوية ومحترمة (لا فصحى معربة)، والتزم بالأسعار والولايات بدون هلوسة.`;

      document.getElementById('agentPromptBox').textContent = agentPrompt;

      let agentReply = '';
      if (sent.label === 'NEGATIVE') {{
        agentReply = 'سلام عليكم خويا، حقك علينا ونعتذروا منك بزاف بزاف! ما تقلقش روحك كامل، المشكل نحلوهولك درك. قولي برك واش صرا بالضبط ونبدلولك السلعة ولا نرجعولك دراهمك في الحين.';
      }} else {{
        const targetWilaya = wilayaName ? 'لـ ' + wilayaName : 'عندك';
        const targetPrice = priceText ? 'والحساب راهو ' + priceText : 'والسعر مضبوط';
        const targetCarrier = carrierName ? 'مع ' + carrierName : 'مع شركة التوصيل';

        if (dialect.region === 'WEST') {{
          agentReply = `وعليكم السلام خويا لعزيز! مرحبا بيك، السلعة راها كاينة ونوصلوها ${{targetWilaya}} ${{targetCarrier}}. ${{targetPrice}}. تقدر تفيرسي في BaridiMob ولا تخلص كاش كي توصلك السلعة غايا!`;
        }} else if (dialect.region === 'EAST') {{
          agentReply = `أهلاً وسهلاً بيك خويا ربي يحفظك! سلعة لوز وضرك نوجدوهالك ${{targetWilaya}} ${{targetCarrier}}، ${{targetPrice}}. تقدر تخلص بالـ BaridiMob ولا تكاشي كي يوصلهالك الليفرور، عيشك!`;
        }} else {{
          agentReply = `سلام خويا، مرحبا بيك عندنا! ما كاش مشكل خلاص، السلعة متوفرة ونوصلوها ${{targetWilaya}} ${{targetCarrier}}، ${{targetPrice}}. بالنسبة للدفع تحب بريدي موب ولا كاش كي تلحقك السلعة للباب؟`;
        }}
      }}
      document.getElementById('agentReplyBox').textContent = agentReply;
    }}

    inputArea.addEventListener('input', processText);
    processText();
  </script>
</body>
</html>
"""

    out_file = docs_dir / 'index.html'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f'[OK] Standalone web playground generated successfully at: {out_file}')


if __name__ == '__main__':
    main()
