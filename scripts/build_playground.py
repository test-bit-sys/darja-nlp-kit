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

    with open(data_dir / 'dialects.json', 'r', encoding='utf-8') as f:
        dialects_data = json.load(f)

    with open(data_dir / 'dialogues.json', 'r', encoding='utf-8') as f:
        dialogues_data = json.load(f)

    with open(data_dir / 'culture.json', 'r', encoding='utf-8') as f:
        culture_data = json.load(f)

    with open(data_dir / 'slang.json', 'r', encoding='utf-8') as f:
        slang_data = json.load(f)

    with open(data_dir / 'profanity.json', 'r', encoding='utf-8') as f:
        profanity_data = json.load(f)

    with open(data_dir / 'dialogue_rules.json', 'r', encoding='utf-8') as f:
        dialogue_rules_data = json.load(f)

    with open(data_dir / 'memes.json', 'r', encoding='utf-8') as f:
        memes_data = json.load(f)

    with open(data_dir / 'franco_darja.json', 'r', encoding='utf-8') as f:
        franco_data = json.load(f)

    template = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>darja-nlp-kit | Algerian NLP & AI Agent Playground</title>
  <link rel="icon" type="image/jpeg" href="logo.jpg?v=2">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
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
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Cairo', system-ui, -apple-system, sans-serif;
    }

    body {
      background-color: var(--bg);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      line-height: 1.6;
    }

    .container {
      max-width: 1100px;
      margin: 0 auto;
      padding: 30px 20px 60px;
      width: 100%;
    }

    /* Header */
    header {
      text-align: center;
      margin-bottom: 40px;
    }

    .project-logo {
      width: 96px;
      height: 96px;
      border-radius: 22px;
      margin-bottom: 16px;
      box-shadow: 0 8px 30px rgba(16, 185, 129, 0.25), 0 0 10px rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.1);
      transition: transform 0.3s ease;
    }

    .project-logo:hover {
      transform: scale(1.05);
    }

    .logo-badge {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 8px 18px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 999px;
      font-size: 13px;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 16px;
    }

    .logo-badge span {
      background: var(--primary);
      color: #000;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 11px;
    }

    h1 {
      font-size: 2.8rem;
      font-weight: 900;
      letter-spacing: -0.5px;
      background: linear-gradient(135deg, #fff 40%, var(--primary) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 12px;
    }

    p.subtitle {
      color: var(--text-muted);
      font-size: 1.1rem;
      max-width: 680px;
      margin: 0 auto 20px;
    }

    .links-bar {
      display: flex;
      justify-content: center;
      gap: 14px;
      flex-wrap: wrap;
      margin-top: 10px;
    }

    .btn-link {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: #1e293b;
      color: #f1f5f9;
      text-decoration: none;
      border-radius: 10px;
      font-size: 13px;
      font-weight: 600;
      border: 1px solid #334155;
      transition: all 0.2s ease;
    }

    .btn-link:hover {
      background: #334155;
      border-color: var(--primary);
      transform: translateY(-2px);
    }

    /* Card base */
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }

    /* Textarea */
    .input-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }

    label {
      font-weight: 700;
      font-size: 15px;
      color: #e2e8f0;
    }

    .char-count {
      font-size: 12px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
    }

    textarea {
      width: 100%;
      height: 120px;
      background: #090d16;
      border: 2px solid #1e293b;
      border-radius: 12px;
      color: #fff;
      font-size: 16px;
      padding: 16px;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s;
      line-height: 1.6;
    }

    textarea:focus {
      border-color: var(--primary);
      box-shadow: 0 0 15px var(--primary-glow);
    }

    /* Samples chips */
    .samples-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
      align-items: center;
    }

    .samples-label {
      font-size: 12px;
      color: var(--text-muted);
      margin-left: 6px;
    }

    .sample-chip {
      background: #1e293b;
      border: 1px solid #334155;
      color: #cbd5e1;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .sample-chip:hover {
      background: #334155;
      color: #fff;
      border-color: var(--accent);
    }

    /* Results Grid */
    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 20px;
    }

    .section-title {
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--primary);
      font-weight: 800;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .section-title::before {
      content: '';
      display: inline-block;
      width: 6px;
      height: 14px;
      background: var(--primary);
      border-radius: 2px;
    }

    /* Intent Badge */
    .intent-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 10px;
      font-weight: 800;
      font-size: 1rem;
    }

    .intent-order { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }
    .intent-price { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid #3b82f6; }
    .intent-delivery { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #f59e0b; }
    .intent-availability { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid #a855f7; }
    .intent-complaint { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }
    .intent-greeting { background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid #06b6d4; }
    .intent-unknown { background: rgba(100, 116, 139, 0.15); color: #94a3b8; border: 1px solid #64748b; }

    /* Escalation Banner */
    .escalation-alert {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid #ef4444;
      border-radius: 12px;
      padding: 14px 18px;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      color: #fca5a5;
    }

    .escalation-healthy {
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 12px;
      padding: 10px 16px;
      margin-bottom: 20px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #6ee7b7;
      font-size: 13px;
    }

    /* Sentiment Display */
    .sentiment-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 18px;
      background: #090d16;
      border: 1px solid #1e293b;
      border-radius: 12px;
      margin-bottom: 14px;
    }

    .sentiment-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 8px;
      font-weight: 800;
      font-size: 14px;
    }

    .badge-positive { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }
    .badge-negative { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    .badge-neutral { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid #64748b; }
    .badge-mixed { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }

    .score-display {
      font-family: 'JetBrains Mono', monospace;
      font-size: 20px;
      font-weight: 700;
    }

    /* Entity Tags */
    .entity-tag {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 10px;
      font-size: 13px;
      margin: 4px;
    }

    .entity-code {
      background: var(--primary);
      color: #000;
      font-weight: 800;
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
    }

    .commune-badge {
      background: rgba(6, 182, 212, 0.2);
      color: #67e8f9;
      border: 1px solid #0891b2;
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 6px;
    }

    .payment-tag {
      background: rgba(168, 85, 247, 0.2);
      border: 1px solid #a855f7;
      color: #d8b4fe;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      display: inline-block;
      margin: 3px;
    }

    .price-tag {
      background: rgba(16, 185, 129, 0.2);
      border: 1px solid #10b981;
      color: #6ee7b7;
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      display: inline-block;
      margin: 3px;
    }

    .carrier-tag {
      background: rgba(245, 158, 11, 0.2);
      border: 1px solid #f59e0b;
      color: #fde68a;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      display: inline-block;
      margin: 3px;
    }

    .mode-tag {
      background: rgba(59, 130, 246, 0.2);
      border: 1px solid #3b82f6;
      color: #93c5fd;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      display: inline-block;
      margin: 3px;
    }

    .phone-tag {
      background: #0f172a;
      border: 1px solid #334155;
      padding: 6px 10px;
      border-radius: 8px;
      font-size: 12px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin: 4px;
    }

    .operator-tag {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .op-mobilis { background: #065f46; color: #a7f3d0; }
    .op-djezzy { background: #991b1b; color: #fecaca; }
    .op-ooredoo { background: #c2410c; color: #fed7aa; }
    .op-landline { background: #1e40af; color: #bfdbfe; }

    .wa-btn {
      background: #25d366;
      color: #000;
      font-weight: 700;
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 4px;
      text-decoration: none;
    }

    .qty-tag {
      background: rgba(14, 165, 233, 0.15);
      border: 1px solid #0284c7;
      color: #7dd3fc;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 700;
      display: inline-block;
      margin: 3px;
    }

    .attr-tag {
      background: rgba(236, 72, 153, 0.15);
      border: 1px solid #db2777;
      color: #f472b6;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      display: inline-block;
      margin: 3px;
    }

    /* Token pills */
    .tokens-pill-box {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }

    .token-pill {
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 12px;
      font-family: 'JetBrains Mono', monospace;
    }

    .token-pos { background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }
    .token-neg { background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }

    /* Text display boxes */
    .code-box {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 12px 14px;
      font-size: 14px;
      color: #e2e8f0;
      word-break: break-word;
      min-height: 48px;
      margin-bottom: 12px;
    }

    /* Dialect Meter */
    .dialect-badge {
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
    }

    .empty-state {
      color: var(--text-muted);
      font-size: 13px;
      font-style: italic;
    }

    footer {
      text-align: center;
      margin-top: auto;
      padding: 30px 20px;
      color: var(--text-muted);
      font-size: 13px;
      border-top: 1px solid var(--card-border);
    }
  </style>
</head>
<body>

  <div class="container">
    <header>
      <img src="logo.jpg?v=2" alt="darja-nlp-kit logo" class="project-logo">
      <br>
      <div class="logo-badge">
        <span>DZ Open Suite</span>
        <span>Zero-Dependency</span>
        <span>69 Wilayas & 550+ Communes</span>
        <span>AI Automation Ready</span>
      </div>
      <h1>darja-nlp-kit</h1>
      <p class="subtitle">حزمة الذكاء الاصطناعي والمعالجة اللغوية للدارجة الجزائرية: تفكيك النوايا، الولايات الـ 69، المشغلين، والتصعيد الذكي</p>
      <div class="links-bar">
        <a href="https://github.com/test-bit-sys/darja-nlp-kit" target="_blank" class="btn-link">
          ⭐ مستودع GitHub
        </a>
        <a href="https://pypi.org/project/darja-nlp-kit/" target="_blank" class="btn-link">
          📦 PyPI Package (Python)
        </a>
        <a href="https://www.npmjs.com/package/@dz-open-suite/darja-nlp-kit" target="_blank" class="btn-link">
          📦 npm Package (Node/TS)
        </a>
      </div>
    </header>

    <div class="card">
      <div class="input-header">
        <label for="textInput">اكتب أو الصق رسالة زبون جزائري (عربي / دارجة / أرابيزي):</label>
        <span class="char-count" id="charCount">0 حرف</span>
      </div>
      <textarea id="textInput" placeholder="اكتب رسالة للتحليل...">salam khoya hab 2 hbat k7la taille L b 2 mlayen w 500 alf l Rouiba fi Alger b yalidine. num ta3i: 0661234567</textarea>
      
      <div class="samples-bar">
        <span class="samples-label">نماذج سريعة للتجربة:</span>
        <button class="sample-chip" onclick="loadSample(0)">🛒 طلب 2 حبات كحلة + رويبة + موبيليس</button>
        <button class="sample-chip" onclick="loadSample(1)">💰 استفسار عن السعر وتوفر السلعة</button>
        <button class="sample-chip" onclick="loadSample(2)">🌟 شكر إيجابي + بلدية العلمة + جيزي</button>
        <button class="sample-chip" onclick="loadSample(3)">🚨 تصعيد عاجل: سراقين حشيتوهالي ونشكي</button>
        <button class="sample-chip" onclick="loadSample(4)">📍 لهجة وهران + دوزينة بونتير 42</button>
        <button class="sample-chip" onclick="loadSample(5)">🚚 استفسار عن التوصيل لقسنطينة + مية الف</button>
        <button class="sample-chip" onclick="loadSample(6)">🍲 ثقافة وأطباق: رشتة عاصمية لباب الواد</button>
        <button class="sample-chip" onclick="loadSample(7)">🔥 ميمز وسلانغ: تيكي تاكا وسلعة كابا</button>
        <button class="sample-chip" style="border-color:#10b981; color:#34d399;" onclick="loadSample(8)">💬 رد حواري: wach ya khoy</button>
        <button class="sample-chip" style="border-color:#f43f5e; color:#fb7185;" onclick="loadSample(9)">🛡️ كشف الشتائم: يا حمار</button>
        <button class="sample-chip" style="border-color:#ec4899; color:#f472b6;" onclick="loadSample(10)">🎭 ميمز: فاك يا حشيشة و زوخ وطير</button>
      </div>
    </div>

    <!-- Smart Escalation Status Card -->
    <div id="escalationStatusBox"></div>

    <div class="results-grid">
      <!-- 1. Customer Intent Card -->
      <div class="card">
        <div class="section-title">تحليل نية الزبون (Customer Intent Classification)</div>
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
          <div id="intentBadge" class="intent-badge intent-order">🛒 طلب شراء (ORDER)</div>
          <div id="intentConfidence" style="font-family:'JetBrains Mono',monospace; color:var(--text-muted); font-size:13px;">دقة 90%</div>
        </div>
        <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">الكلمات الدالة المرصودة:</div>
        <div id="intentKeywords" class="tokens-pill-box"></div>
      </div>

      <!-- 2. Sentiment Card -->
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

      <!-- 3. Wilayas (69) & Communes Card -->
      <div class="card">
        <div class="section-title">الولايات والبلديات (69 ولاية و 1,541 بلدية - معتمدة على algeria-geo)</div>
        <div id="wilayasBox"></div>
      </div>

      <!-- 4. Quantities & Attributes Card -->
      <div class="card">
        <div class="section-title">الكميات ومواصفات المنتج (Quantities & Attributes)</div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">الكميات الشعبية المستخرجة:</div>
          <div id="quantitiesBox"></div>
        </div>
        <div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">الألوان والمقاسات (Colors & Sizes):</div>
          <div id="attributesBox"></div>
        </div>
      </div>

      <!-- 5. Payments & Prices Card -->
      <div class="card">
        <div class="section-title">طرق الدفع والأسعار المستخرجة (Payments & Prices)</div>
        <div style="margin-bottom: 12px;">
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">طرق الدفع:</div>
          <div id="paymentsBox"></div>
        </div>
        <div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">الأسعار والمبالغ بالدينار (شاملة الملايين والألوف):</div>
          <div id="pricesBox"></div>
        </div>
      </div>

      <!-- 6. Logistics & Contact Card with Telecom Operator -->
      <div class="card">
        <div class="section-title">شركات التوصيل والمشغل ورابط واتساب (Logistics & Telecom)</div>
        <div style="margin-bottom: 10px;">
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">شركة ونمط التوصيل:</div>
          <div id="deliveriesBox"></div>
        </div>
        <div>
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">أرقام الهاتف مع المشغل (Mobilis/Djezzy/Ooredoo/Fixe):</div>
          <div id="phonesBox"></div>
        </div>
      </div>

      <!-- 7. Dialect Card -->
      <div class="card">
        <div class="section-title">كشف اللهجة الجهوية (Regional Dialect)</div>
        <div style="margin-bottom: 14px;">
          <div id="dialectBadge" class="dialect-badge">الوسط الجزائري (CENTER)</div>
        </div>
        <div style="font-size: 13px; color: var(--text-muted); margin-bottom: 6px;">المؤشرات اللغوية المرصودة:</div>
        <div id="dialectMarkers" class="tokens-pill-box"></div>
      </div>

      <!-- 8. Cultural Knowledge, Slang & Food Card -->
      <div class="card">
        <div class="section-title">المعالم، الأمثال والمصطلحات الشعبية (Culture, Slang & Food)</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">رصد التراث والأمثال الشعبية ومصطلحات التجارة:</div>
        <div id="culturalBox" style="display:flex; flex-direction:column; gap:6px;"></div>
      </div>

      <!-- 9. Arabizi & Normalization -->
      <div class="card">
        <div class="section-title">معالجة الأرابيزي والتطبيع (Arabizi & Normalizer)</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">الترجمة التفسيرية (Arabizi &rarr; Arabic):</div>
        <div id="arabiziBox" class="code-box"></div>
        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">النص المطبع (Normalized):</div>
        <div id="normalizedBox" class="code-box"></div>
      </div>

      <!-- 10. Natural Darja Dialogue Response Engine -->
      <div class="card" style="border-color: rgba(16, 185, 129, 0.4); background: radial-gradient(circle at top right, #062b1f, #111827);">
        <div class="section-title" style="color: #34d399;">💬 الردود الحوارية الطبيعية (Natural Darja Chatbot Engine)</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">توليد رد عفوي وطبيعي بلهجة الدارجة مطابق تماماً للغة السائل (مثلاً: wach ya khoy &rarr; we cv hamdoulah):</div>
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
          <span id="dialogueScriptBadge" class="token-pill" style="background:#065f46; color:#6ee7b7; border:1px solid #10b981;">Script</span>
          <span id="dialogueIntentBadge" class="token-pill" style="background:#1e293b; color:#93c5fd; border:1px solid #3b82f6;">Intent</span>
        </div>
        <div id="dialogueReplyBox" style="background:#080c14; border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:12px 16px; font-size:15px; color:#ecfdf5; line-height:1.6; font-weight:600;"></div>
      </div>

      <!-- 11. Content Moderation & Profanity Shield -->
      <div class="card" style="border-color: rgba(244, 63, 94, 0.4); background: radial-gradient(circle at top right, #2b0610, #111827);">
        <div class="section-title" style="color: #fb7185;">🛡️ درع سلامة المحتوى والكلمات البذيئة (Content Moderation Shield)</div>
        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">كشف الشتائم، الألفاظ البذيئة والسمية في الدارجة (عربي وعربيزي) مع الحجب التلقائي:</div>
        <div id="profanityStatusBox" style="margin-bottom:8px;"></div>
        <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 4px;">النص المحجوب (Censored Text):</div>
        <div id="censoredTextBox" class="code-box" style="color:#fda4af;"></div>
      </div>

      <!-- 10. AI Agent Customer Assistant Simulator -->
      <div class="card" style="grid-column: 1 / -1; border-color: rgba(59, 130, 246, 0.4); background: radial-gradient(circle at top left, #0f1c3f, #111827);">
        <div class="section-title" style="color: #60a5fa;">🤖 محاكي وكيل الذكاء الاصطناعي الجزائري (AI Agent Assistant Simulator)</div>
        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 14px;">
          كيف يستقبل نموذج الذكاء الاصطناعي (مثل GPT-4o / Claude / Gemini) هذا الزبون عبر <strong>darja-nlp-kit</strong>، مع مطابقة النية، اللهجة، الكميات، والمبالغ دون هلوسة:
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px;">
          <div>
            <div style="font-size: 12px; color: #93c5fd; font-weight: 700; margin-bottom: 6px;">🧠 الـ System Prompt المحقون للذكاء الاصطناعي:</div>
            <pre id="agentPromptBox" style="background:#080c14; border:1px solid #1e293b; border-radius:10px; padding:12px; font-family:'JetBrains Mono',monospace; font-size:11px; color:#cbd5e1; max-height:220px; overflow-y:auto; white-space:pre-wrap;"></pre>
          </div>
          <div>
            <div style="font-size: 12px; color: #34d399; font-weight: 700; margin-bottom: 6px;">💬 رد الذكاء الاصطناعي البشري الواقعي (AI Agent Response):</div>
            <div id="agentReplyBox" style="background:#080c14; border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:16px; font-size:15px; color:#f0fdf4; line-height:1.7; min-height:80px; display:flex; align-items:center;"></div>
          </div>
          <div style="grid-column: 1 / -1; margin-top: 4px;">
            <div style="font-size: 12px; color: #fbbf24; font-weight: 700; margin-bottom: 6px;">📚 عينة تدريب حقيقية مطابقة للهجة المستهدفة من قاعدة البيانات (150+ Dialogues Few-Shot):</div>
            <div id="matchingDialogueBox" style="background:#080c14; border:1px solid rgba(251,191,36,0.25); border-radius:10px; padding:12px 16px; font-size:13px; color:#fef3c7; line-height:1.7;"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <footer>
    <p><strong>darja-nlp-kit</strong> — Zero-dependency Algerian Darja NLP & AI Automation Toolkit. Open Source under MIT License.</p>
    <p style="margin-top: 4px;">Developed for Algerian developers, merchants, and AI automation creators.</p>
  </footer>

  <script>
    // Embedded Linguistic Datasets
    const STOPWORDS_DATA = __STOPWORDS_DATA__;
    const LEXICON_DATA = __LEXICON_DATA__;
    const ARABIZI_RULES = __ARABIZI_RULES__;
    const WILAYAS_DATA = __WILAYAS_DATA__;
    const DIALECTS_DATA = __DIALECTS_DATA__;
    const DIALOGUES_DATA = __DIALOGUES_DATA__;
    const CULTURE_DATA = __CULTURE_DATA__;
    const SLANG_DATA = __SLANG_DATA__;
    const PROFANITY_DATA = __PROFANITY_DATA__;
    const DIALOGUE_RULES_DATA = __DIALOGUE_RULES_DATA__;
    const MEMES_DATA = __MEMES_DATA__;
    const FRANCO_DATA = __FRANCO_DATA__;

    // Core Algorithms
    const ALEF_VARIANTS = /[\u0622\u0623\u0625]/g;
    const TA_MARBUTA = /\u0629/g;
    const ALEF_MAQSURA = /\u0649/g;
    const TASHKEEL = /[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED]/g;
    const TATWEEL = /\u0640/g;
    const ARABIC_ELONGATION = /(.)\1{2,}/g;
    const LATIN_ELONGATION = /([a-zA-Z])\1{2,}/g;
    const MULTI_SPACE = /\s+/g;
    const MULTI_PUNCT = /([!?.]){2,}/g;
    const VALID_DOUBLES = new Set(['ll','ss','mm','nn','dd','tt','rr','ff','cc','pp','bb','gg','zz','ee','oo','aa']);

    function normalize(text) {
      if (!text) return '';
      let res = text.replace(ALEF_VARIANTS, '\u0627')
                    .replace(TA_MARBUTA, '\u0647')
                    .replace(ALEF_MAQSURA, '\u064A')
                    .replace(TASHKEEL, '')
                    .replace(TATWEEL, '')
                    .replace(ARABIC_ELONGATION, '$1')
                    .replace(LATIN_ELONGATION, (m, c) => VALID_DOUBLES.has(c.toLowerCase()+c.toLowerCase()) ? c+c : c)
                    .replace(MULTI_SPACE, ' ')
                    .replace(MULTI_PUNCT, '$1')
                    .trim();
      return res;
    }

    function isFrenchWord(word) {
      const lower = word.toLowerCase();
      if (ARABIZI_RULES.french_whitelist.includes(lower)) return true;
      for (const suffix of ARABIZI_RULES.french_suffixes) {
        if (lower.endsWith(suffix) && lower.length > suffix.length + 2) return true;
      }
      return false;
    }

    function arabiziToArabic(text) {
      if (!text) return '';
      const tokens = text.split(/(\s+|[.,!?;:()]+)/);
      return tokens.map(tok => {
        if (!tok.trim() || /^[.,!?;:()]+$/.test(tok)) return tok;
        const lower = tok.toLowerCase();
        if (ARABIZI_RULES.overrides[lower]) return ARABIZI_RULES.overrides[lower];
        if (isFrenchWord(lower) || /^[0-9+]+$/.test(tok)) return tok;

        let res = lower;
        for (const [k, v] of Object.entries(ARABIZI_RULES.digraphs)) {
          res = res.replaceAll(k, v);
        }
        for (const [k, v] of Object.entries(ARABIZI_RULES.numbers)) {
          res = res.replaceAll(k, v);
        }
        for (const [k, v] of Object.entries(ARABIZI_RULES.singles)) {
          res = res.replaceAll(k, v);
        }
        return res;
      }).join('');
    }

    function removeStopwords(text) {
      if (!text) return '';
      const allStops = new Set();
      for (const list of Object.values(STOPWORDS_DATA)) {
        list.forEach(w => allStops.add(w.toLowerCase()));
      }
      const tokens = text.split(/\s+/);
      const filtered = tokens.filter(t => !allStops.has(t.toLowerCase()) && !allStops.has(normalize(t)));
      return filtered.join(' ');
    }

    function analyzeSentiment(text) {
      if (!text) return { score: 0, label: 'NEUTRAL', positiveTokens: [], negativeTokens: [], negated: false };
      const clean = normalize(text);
      const words = clean.split(/[\s,،!?;:.]+/).filter(Boolean);
      let total = 0, count = 0, hasNeg = false;
      const pos = [], neg = [];

      for (let i = 0; i < words.length; i++) {
        const w = words[i].toLowerCase();
        let score = null;
        let t = words[i];

        if (LEXICON_DATA.positive[w] !== undefined) {
          score = LEXICON_DATA.positive[w];
        } else if (LEXICON_DATA.negative[w] !== undefined) {
          score = LEXICON_DATA.negative[w];
        }

        if (score === null) continue;

        const prev = i > 0 ? words[i - 1].toLowerCase() : null;
        if (prev && LEXICON_DATA.negators.includes(prev)) {
          score = -score * 0.8;
          hasNeg = true;
        }
        if (prev && LEXICON_DATA.intensifiers[prev] && !LEXICON_DATA.negators.includes(prev)) {
          score *= LEXICON_DATA.intensifiers[prev];
        }

        total += score;
        count++;
        if (score > 0) pos.push(t); else if (score < 0) neg.push(t);
      }

      const finalScore = count > 0 ? Math.max(-1, Math.min(1, total / count)) : 0;
      const rounded = Math.round(finalScore * 100) / 100;
      let label = 'NEUTRAL';
      if (pos.length > 0 && neg.length > 0) label = 'MIXED';
      else if (rounded > 0.05) label = 'POSITIVE';
      else if (rounded < -0.05) label = 'NEGATIVE';

      return { score: rounded, label, positiveTokens: pos, negativeTokens: neg, negated: hasNeg };
    }

    function identifyIntent(text) {
      if (!text) return { intent: 'UNKNOWN', confidence: 0, matchedKeywords: [] };
      const lower = text.toLowerCase();
      const rules = [
        {
          intent: 'COMPLAINT',
          keywords: [
            'مكسرة', 'مكسر', 'ما وصلتش', 'ما لحقتش', 'روطار', 'سلعة عيانة', 'سلعة ميتة', 'حشيتوهالي',
            'حشاوها لي', 'بدلوهالي', 'روتور', 'رجعولي دراهمي', 'ما رديتوش', 'حقار', 'سراقين', 'سرقة',
            'فضيحة', 'سلعة مفاتشة', 'ماشي كيما الفوتو', 'ماشي كيما التصويرة', 'ناقصة', 'معطوبة', 'مخدوعة',
            'reclamation', 'retour', 'casse', 'mfetcha', 'retard', 'ma wesletch', '7chawhali',
            'arnaque', 'ser9a', 'khorda', 'naqsa'
          ]
        },
        {
          intent: 'ORDER',
          keywords: [
            'كوموندي', 'نكوموندي', 'كومونديلي', 'كوموندالي', 'باغي نشري', 'راني باغي', 'باغي', 'حاب نشري',
            'حبيت نشري', 'راني حاب', 'حاب', 'حبيت', 'ابعثلي', 'ابعثهالي', 'ابعثوهالي', 'احجزلي', 'حجز', 'احجز',
            'راني شاري', 'نشريها', 'نشري', 'جيبهالي', 'حاب نطلب', 'طلب شراء', 'نحتاج حبة', 'نحتاج زوج', 'نحتاج',
            'commander', 'ncommander', 'baghi nchri', 'rani baghi', 'baghi', 'hab nchri', '7ab nchri',
            'rani hab', 'rani 7ab', 'hab', '7ab', 'habb', 'nchri', 'chrit', 'nchriha', 'nchrihoum',
            'ab3atli', 'ab3athali', 'livrili', 'livrihali', 'livreli', '7jezli', 'reserver', 'je veux acheter'
          ]
        },
        {
          intent: 'DELIVERY_INQUIRY',
          keywords: [
            'التوصيل', 'توصيل', 'شحال التوصيل', 'شحال لا ليفريزون', 'كاين توصيل', 'توصلو', 'توصلوا',
            'وقتاش تلحق', 'وقتاش يوصل', 'شحال يقعد', 'شحال الوقت', 'توصيل للدار', 'توصيل للمكتب', 'توصيل متوفر',
            'livraison', 'la livraison', 'frais de livraison', 'délai', 'delai', 'livriw', 'touslou', 'chal livraison'
          ]
        },
        {
          intent: 'PRICE_INQUIRY',
          keywords: [
            'السعر', 'السومة', 'بشحال', 'شحال', 'شحال يدير', 'شحال راه يدير', 'بقداش', 'قداش', 'شحال السومة',
            'سومة', 'prix', 'bchhal', 'chhal', 'ch7al', 'bch7al', 'kadech', '9dach', 'c combien', 'combien'
          ]
        },
        {
          intent: 'AVAILABILITY_INQUIRY',
          keywords: [
            'متوفر', 'متوفرة', 'كاين منها', 'مازال كاين', 'مازالت كاينة', 'كاين ستوك', 'كاين كولور', 'كاين لاطاي',
            'متوفر هذا الموديل', 'خلاصت', 'dispo', 'disponible', 'disponibilité', 'kayen', 'mazal'
          ]
        },
        {
          intent: 'GREETING',
          keywords: [
            'سلام', 'سلام عليكم', 'السلام عليكم', 'صباح الخير', 'مساء الخير', 'صحا', 'صحيت', 'واش راك',
            'salam', 'slm', 'bonjour', 'bonsoir', 'salut', 'coucou', 'salam alikoum'
          ]
        }
      ];

      for (const rule of rules) {
        const matched = rule.keywords.filter(k => lower.includes(k.toLowerCase()));
        if (matched.length > 0) {
          return {
            intent: rule.intent,
            confidence: Math.min(0.98, 0.70 + matched.length * 0.1),
            matchedKeywords: matched
          };
        }
      }
      return { intent: 'UNKNOWN', confidence: 0, matchedKeywords: [] };
    }

    function detectEscalation(text) {
      if (!text) return { needsEscalation: false, urgency: 'NONE', reason: null, matchedTriggers: [], guideline: '' };
      const lower = text.toLowerCase();

      const legals = ['نشكي بيكم', 'لابوليس', 'حماية المستهلك', 'العدالة', 'نديرلكم شكوى', 'محكمة', 'la police', 'protection du consommateur', 'plainte', 'tribunal'];
      const mLegal = legals.filter(t => lower.includes(t.toLowerCase()));
      if (mLegal.length > 0) {
        return {
          needsEscalation: true,
          urgency: 'CRITICAL',
          reason: 'LEGAL_THREAT',
          matchedTriggers: mLegal,
          guideline: '🚨 الزبون يهدد بمتابعة قانونية أو شكوى رسمية! يجب تحويل المحادثة فوراً للإدارة وتجنب أي جدال آلي.'
        };
      }

      const angry = ['حشيتوهالي', 'حشاوها لي', 'سراقين', 'سرقة عيني عينك', 'فضيحة', 'رجعولي دراهمي', 'وكيلكم ربي', 'حقارين', 'الله لا يربحكم', 'بهدلتو بينا', 'خردة', '7chawhali', 'ser9a', 'arnaqueurs', 'voleurs'];
      const mAngry = angry.filter(t => lower.includes(t.toLowerCase()));
      if (mAngry.length > 0) {
        return {
          needsEscalation: true,
          urgency: 'HIGH',
          reason: 'ANGRY_CUSTOMER',
          matchedTriggers: mAngry,
          guideline: '⚠️ الزبون غاضب جداً ويتهم المتجر بسوء النية أو السرقة. يجب تدخل عون بشري لامتصاص الغضب وتقديم تعويض/استرجاع.'
        };
      }

      const human = ['احكي مع بنادم', 'مع انسان', 'مع بنادم', 'كاش انسان', 'عطيني المدير', 'خدمة الزبائن', 'عيطلي', 'كلمني', 'كلموني', 'appel moi', 'appelez moi', 'parler a un responsable', 'parler a un agent', 'service client', 'humain'];
      const mHuman = human.filter(t => lower.includes(t.toLowerCase()));
      if (mHuman.length > 0) {
        return {
          needsEscalation: true,
          urgency: 'HIGH',
          reason: 'HUMAN_REQUESTED',
          matchedTriggers: mHuman,
          guideline: '👤 الزبون يطلب التحدث مع شخص حقيقي أو مسؤول. تجنب الردود الآلية وسهّل التواصل البشري.'
        };
      }

      return { needsEscalation: false, urgency: 'NONE', reason: null, matchedTriggers: [], guideline: '' };
    }

    function extractQuantities(text) {
      const results = [];
      const unitWords = { 'زوج': 2, 'تلات': 3, 'تلاتة': 3, 'ربع': 4, 'ربعة': 4, 'خمس': 5, 'خمسة': 5, 'zouj': 2, 'tlata': 3 };
      const dynReg = /(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:\.\d+)?|زوج|تلات|تلاتة|ربع|ربعة|خمس|خمسة|zouj|tlata)\s*(حبات|حبة|حبه|شكاير|شكارة|باكيات|باكية|كراتن|كراطن|كرطونة|hbat|7bat|chkayer|bakyat|boites|cartons)(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let m;
      let masked = text;
      while ((m = dynReg.exec(text)) !== null) {
        const rawNum = m[1].toLowerCase();
        const rawUnit = m[2].toLowerCase();
        let val = unitWords[rawNum] !== undefined ? unitWords[rawNum] : (parseFloat(rawNum) || 1);
        let uNorm = rawUnit;
        if (['حبات', 'hbat', '7bat'].includes(rawUnit)) uNorm = 'حبة';
        else if (['شكاير', 'chkayer'].includes(rawUnit)) uNorm = 'شكارة';
        else if (['باكيات', 'bakyat', 'boites'].includes(rawUnit)) uNorm = 'باكية';
        else if (['كراتن', 'كراطن', 'cartons'].includes(rawUnit)) uNorm = 'كرطونة';
        results.push({ raw: m[0].trim(), value: val, unit: uNorm });
        masked = masked.slice(0, m.index) + ' '.repeat(m[0].length) + masked.slice(m.index + m[0].length);
      }

      // Fixed units like دوزينة
      const fixed = [
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(دوزينة|دزينة|douzina|douzaine)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 12, unit: 'دوزينة' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(حبة\s*وحدة|1\s*hba)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 1, unit: 'حبة' },
      ];
      for (const item of fixed) {
        const fm = masked.match(item.reg);
        if (fm) {
          results.push({ raw: fm[0].trim(), value: item.val, unit: item.unit });
        }
      }
      return results;
    }

    function extractProductAttributes(text) {
      const colors = [];
      const colorDefs = [
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(كحل|كحلة|noir|noire|k7al)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'كحل / noir' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بيض|بيضا|blanc|blanche|byad)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بيض / blanc' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(غوج|حمرا|rouge|7mar)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'غوج / rouge' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بلو|زرقة|bleu|bleue)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بلو / bleu' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(خضر|خضرا|vert|verte)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'خضر / vert' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بيج|beige)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بيج / beige' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(مارون|قهوي|marron)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'مارون / marron' },
      ];
      for (const c of colorDefs) {
        if (c.reg.test(text) && !colors.includes(c.label)) colors.push(c.label);
      }

      const sizes = [];
      const sizePats = [/\b(xxxl|3xl)\b/i, /\b(xxl|2xl)\b/i, /\b(xl)\b/i, /\b(l)\b/i, /\b(m)\b/i, /\b(s)\b/i];
      for (const sp of sizePats) {
        const sm = text.match(sp);
        if (sm) {
          const sVal = sm[1].toUpperCase();
          if (!sizes.includes(sVal)) sizes.push(sVal);
        }
      }
      const shoeReg = /(?:pointure|taille|مقاس|نمرة)?\s*([3-4][0-9])\b/gi;
      let shm;
      while ((shm = shoeReg.exec(text)) !== null) {
        const num = parseInt(shm[1], 10);
        if (num >= 35 && num <= 48 && !sizes.includes(shm[1])) sizes.push(shm[1]);
      }

      return { colors, sizes };
    }

    function extractEntities(text) {
      const wilayas = [];
      const lower = text.toLowerCase();
      const addedCodes = new Set();

      // Wilayas (69) direct code
      const codeRegex = /\b(?:wilaya|w|ولاية|ولايه|l)\s*([0-6]?[0-9])\b/gi;
      let cm;
      while ((cm = codeRegex.exec(text)) !== null) {
        const num = parseInt(cm[1], 10);
        if (num >= 1 && num <= 69 && !addedCodes.has(num)) {
          const w = WILAYAS_DATA.find(item => item.code === num);
          if (w) {
            addedCodes.add(num);
            wilayas.push({ ...w, matched: cm[0] });
          }
        }
      }

      // Wilayas names & aliases
      for (const w of WILAYAS_DATA) {
        if (addedCodes.has(w.code)) continue;
        for (const alias of w.aliases) {
          if (alias.length >= 3 && lower.includes(alias.toLowerCase())) {
            addedCodes.add(w.code);
            let comMatch = null;
            if (w.communes_sample && w.communes_sample.includes(alias)) comMatch = alias;
            else if (w.communes_fr_sample && w.communes_fr_sample.some(c => c.toLowerCase() === alias.toLowerCase())) comMatch = alias;
            wilayas.push({ ...w, matched: alias, commune: comMatch });
            break;
          }
        }
      }

      // Communes (550+)
      for (const w of WILAYAS_DATA) {
        if (addedCodes.has(w.code)) continue;
        const allComs = (w.communes_sample || []).concat(w.communes_fr_sample || []);
        for (const com of allComs) {
          if (com && com.length >= 3 && lower.includes(com.toLowerCase())) {
            addedCodes.add(w.code);
            wilayas.push({ ...w, matched: com, commune: com });
            break;
          }
        }
      }

      // Payments
      const payments = [];
      const payPatterns = [
        { type: 'BARIDIMOB', label: 'BaridiMob (بريدي موب)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(baridimob|baridi\s*mob|بريدي\s*موب|بريديموب)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { type: 'EDAHABIA', label: 'Carte Edahabia (البطاقة الذهبية)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(edahabia|dahabia|الذهبية|البطاقة\s*الذهبية)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { type: 'CCP', label: 'CCP (الحساب البريدي الجاري)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(ccp|سي\s*سي\s*بي)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { type: 'COD', label: 'Paiement à la livraison (الدفع عند الاستلام)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(cod|الدفع\s*عند\s*الاستلام|كي\s*يوصلني|كي\s*تلحق|كي\s*توصل|main\s*à\s*main)(?=$|\s|[^\w\u0600-\u06FF])/i },
      ];
      for (const p of payPatterns) {
        if (p.reg.test(text)) payments.push({ type: p.type, label: p.label });
      }

      // Prices & colloquial Darja amounts
      const prices = [];
      let maskedText = text;
      const millionsMap = { 'زوج': 2, 'تلات': 3, 'تلاتة': 3, 'ربع': 4, 'ربعة': 4, 'خمس': 5, 'خمسة': 5, 'عشر': 10, 'عشرة': 10, 'zouj': 2, 'tlata': 3 };
      const thousandsMap = { 'مية': 100, 'ميتين': 200, 'تلمية': 300, 'ربعمية': 400, 'خمسمية': 500, 'ستين': 60, 'سبعين': 70, 'mya': 100, 'mitin': 200, 'khamsmya': 500 };
      const mStr = 'زوج|تلات|تلاتة|ربع|ربعة|خمس|خمسة|ست|ستة|سبع|سبعة|تمن|تمنية|تسع|تسعة|عشر|عشرة|zouj|zoudj|tlata|tleta|rab3a|khamsa|setta|seb3a|tmenya|tes3a|3achra';
      const kStr = 'مية|ميتين|تلمية|تلاتمية|ربعمية|خمسمية|ستمية|سبعمية|تمنمية|تسعمية|عشرين|تلاتين|ربعين|خمسين|ستين|سبعين|تمانين|تسعين|mya|mitin|teltmya|khamsmya|khamsin';

      // 1. Compound prices (e.g. 2 mlayen w 500 alf)
      const compReg = new RegExp(`(?:^|\\s|[^\\w\\u0600-\\u06FF])(\\d+(?:[.,]\\d+)?|${mStr})?\\s*(?:ملاين|ملايين|مليون|mlyon|mlayen|mlayin)\\s*(?:و|\\+|et|w)\\s*(\\d+(?:[.,]\\d+)?|${kStr})?\\s*(?:الف|ألف|alf)(?=$|\\s|[^\\w\\u0600-\\u06FF])`, 'gi');
      let compM;
      while ((compM = compReg.exec(text)) !== null) {
        const rM = compM[1];
        const rK = compM[2];
        let mVal = 1;
        if (rM) {
          const k = rM.toLowerCase();
          mVal = millionsMap[k] !== undefined ? millionsMap[k] : (parseFloat(k.replace(',', '.')) || 1);
        }
        let kVal = 1;
        if (rK) {
          const k = rK.toLowerCase();
          kVal = thousandsMap[k] !== undefined ? thousandsMap[k] : (parseFloat(k.replace(',', '.')) || 0);
        }
        const total = (mVal * 10000) + (kVal * 10);
        prices.push({ raw: compM[0].trim(), amount: total });
        maskedText = maskedText.slice(0, compM.index) + ' '.repeat(compM[0].length) + maskedText.slice(compM.index + compM[0].length);
      }

      // 2. Numeric prices with currency
      const priceNumReg = /(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(da|dzd|دج|دينار|الف|ألف|alf)(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let pm;
      while ((pm = priceNumReg.exec(maskedText)) !== null) {
        let val = parseFloat(pm[1].replace(',', '.'));
        const u = pm[2].toLowerCase();
        if (u === 'الف' || u === 'ألف' || u === 'alf') val *= 1000;
        prices.push({ raw: pm[0].trim(), amount: val });
        maskedText = maskedText.slice(0, pm.index) + ' '.repeat(pm[0].length) + maskedText.slice(pm.index + pm[0].length);
      }

      // 3. Dynamic millions
      const dynMilReg = /(?:^|\s|[^\w\u0600-\u06FF])(\\d+(?:[.,]\\d+)?)\s*(?:ملاين|ملايين|مليون|mlyon|mlayen|mlayin)(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let dmDyn;
      while ((dmDyn = dynMilReg.exec(maskedText)) !== null) {
        const val = parseFloat(dmDyn[1].replace(',', '.')) * 10000;
        prices.push({ raw: dmDyn[0].trim(), amount: val });
        maskedText = maskedText.slice(0, dmDyn.index) + ' '.repeat(dmDyn[0].length) + maskedText.slice(dmDyn.index + dmDyn[0].length);
      }

      // 4. Fixed colloquial amounts
      const darjaAmounts = [
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(مية\s*الف|100\s*الف|mya|myat\s*alf)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 1000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(ميتين\s*الف|200\s*الف|mitin\s*alf)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 2000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(خمسمية\s*الف|500\s*الف|khams\s*mya|500\s*alf)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 5000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(مليون|mlyon|1\s*mlyon)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 10000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(زوج\s*ملاين|زوج\s*ملايين|zoudj\s*mlayen|zouj\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 20000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(خمس\s*ملاين|khams\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 50000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(عشر\s*ملاين|3achr\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 100000 },
      ];
      for (const item of darjaAmounts) {
        const dm = maskedText.match(item.reg);
        if (dm) {
          prices.push({ raw: dm[0].trim(), amount: item.val });
          maskedText = maskedText.slice(0, dm.index) + ' '.repeat(dm[0].length) + maskedText.slice(dm.index + dm[0].length);
        }
      }

      // Deliveries
      const deliveries = [];
      const deliveryPatterns = [
        { company: 'YALIDINE', label: 'Yalidine Express (ياليدين)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(yalidine|yalidin|ياليدين)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'ZR_EXPRESS', label: 'ZR Express (زد ار اكسبرس)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(zr\s*express|zr|زد\s*ار\s*اكسبرس|زد\s*ار)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'MAYSTRO', label: 'Maystro Delivery (مايسترو)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(maystro\s*delivery|maystro|مايسترو)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'PROCOLIS', label: 'Procolis (بروكولي)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(procolis|pro\s*colis|بروكولي|بروكوليس)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'EMS', label: 'EMS Algérie Poste (البريد السريع)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(ems|ems\s*algerie|البريد\s*السريع)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'KAZITOUR', label: 'Kazitour Express (كازيتور)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(kazitour|kazi\s*tour|كازيتور)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'GUEPEX', label: 'Guepex Express (قيباكس)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(guepex|قيباكس)(?=$|\s|[^\w\u0600-\u06FF])/i },
      ];
      for (const d of deliveryPatterns) {
        const m = text.match(d.reg);
        if (m) deliveries.push({ company: d.company, label: d.label, matched: m[0].trim() });
      }

      // Delivery Mode
      let deliveryMode = null;
      const modePatterns = [
        { mode: 'STOP_DESK', label: 'Stop Desk (استلام من المكتب)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(stop\s*desk|stopdesk|سطوب\s*ديسك|ستوب\s*ديسك|المكتب|فالبيرو|في\s*البيرو|agence)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { mode: 'HOME_DELIVERY', label: 'Home Delivery (توصيل للمنزل)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(a\s*domicile|[aà]\s*domicile|للدار|لباب\s*الدار|توصيل\s*للمنزل|توصيل\s*للدار|فالدار)(?=$|\s|[^\w\u0600-\u06FF])/i },
      ];
      for (const dm of modePatterns) {
        const m = text.match(dm.reg);
        if (m) { deliveryMode = dm.label; break; }
      }

      // Phones & Telecom Operator
      const phones = [];
      const phoneReg = /(?:^|\s|[^\w\u0600-\u06FF])((?:\+213|00213|0)\s*(?:[5-7](?:[\s.-]?\d){8}|(?:2[0-9]|3[0-9]|4[0-9])(?:[\s.-]?\d){6}))(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let phMatch;
      while ((phMatch = phoneReg.exec(text)) !== null) {
        let raw = phMatch[1].trim();
        let norm = raw.replace(/[\s.-]/g, '');
        if (norm.startsWith('00213')) norm = '0' + norm.slice(5);
        else if (norm.startsWith('+213')) norm = '0' + norm.slice(4);

        let op = null, opLabel = null, opClass = '';
        const pref = norm.slice(0, 2);
        if (pref === '06') { op = 'MOBILIS'; opLabel = 'Mobilis (موبيليس)'; opClass = 'op-mobilis'; }
        else if (pref === '07') { op = 'DJEZZY'; opLabel = 'Djezzy (جيزي)'; opClass = 'op-djezzy'; }
        else if (pref === '05') { op = 'OOREDOO'; opLabel = 'Ooredoo (أوريدو)'; opClass = 'op-ooredoo'; }
        else if (['02', '03', '04'].includes(pref)) { op = 'ALGERIE_TELECOM'; opLabel = 'Fixe (الهاتف الثابت)'; opClass = 'op-landline'; }

        const waUrl = (norm.length === 10 && ['05', '06', '07'].includes(pref)) ? `https://wa.me/213${norm.slice(1)}` : null;
        phones.push({ raw, normalized: norm, operator: op, operatorLabel: opLabel, opClass, waUrl });
      }

      return { wilayas, payments, prices, deliveries, deliveryMode, phones };
    }

    function detectDialect(text) {
      const markers = {
        WEST: ['شوالا', 'شاكاين', 'شا', 'غايا', 'باغي', 'حرز', 'راك عاقل', 'شراكم', 'كيراك', 'كيراكم', 'درك', 'chwala', 'chakayn', 'ghaya', 'baghi', 'kirak', 'drk'],
        EAST: ['واشنهي', 'قداش', 'ياسر', 'ضرك', 'زي', 'باهي', 'علاشنهي', 'واشبيك', 'كفاه', 'ضروك', 'سيرتا', 'بونة', '9dach', 'yaser', 'bahi'],
        CENTER: ['واشنو', 'حكاية', 'دروك', 'هكدا', 'هكداك', 'حوايج', 'البهجة', 'العاصمة', 'دزاير', 'wachnou', 'hakda', 'hakdak'],
        SOUTH: ['واه', 'لاه', 'حتة', 'سوف', 'ميزاب', 'غرداية', 'ادرار', 'wah', 'lah', '7ata'],
      };
      const lower = text.toLowerCase();
      const scores = { WEST: [], EAST: [], CENTER: [], SOUTH: [] };
      for (const [reg, words] of Object.entries(markers)) {
        for (const w of words) {
          if (lower.includes(w.toLowerCase())) scores[reg].push(w);
        }
      }
      let top = 'GENERAL_DARJA';
      let max = 0;
      let detected = [];
      for (const [r, list] of Object.entries(scores)) {
        if (list.length > max) { max = list.length; top = r; detected = list; }
      }
      return {
        region: top,
        confidence: max > 0 ? Math.min(0.99, Math.round((0.6 + max * 0.15) * 100) / 100) : 0.5,
        detectedMarkers: detected,
      };
    }

    const GENERIC_CULTURE_STOP = new Set(['سلعة', 'سوق', 'حي', 'شارع', 'باب', 'واد', 'ساحة', 'جبل', 'جبال', 'طاجين', 'طبق', 'أكلة']);

    function extractKeywords(text) {
      if (!text) return [];
      const clean = text.split(' (')[0].trim();
      const parts = text.split(/[/(),]|\s+و/);
      const res = new Set([text, clean]);
      for (const part of parts) {
        const p = part.trim();
        if (p.length > 2 && !GENERIC_CULTURE_STOP.has(p)) {
          res.add(p);
          if (p.startsWith('ال') && p.length > 3) {
            res.add(p.slice(2));
          } else if (!p.startsWith('ال')) {
            res.add('ال' + p);
          }
          const words = p.split(/\s+/);
          if (words.length === 2) {
            for (const w of words) {
              if (w.length > 3 && !GENERIC_CULTURE_STOP.has(w)) {
                res.add(w);
                if (w.startsWith('ال') && w.length > 4) {
                  res.add(w.slice(2));
                } else if (!w.startsWith('ال')) {
                  res.add('ال' + w);
                }
              }
            }
          }
        }
      }
      return Array.from(res).filter(x => x.length > 2 && !GENERIC_CULTURE_STOP.has(x));
    }

    function detectCulturalReferences(text) {
      if (!text || !text.trim()) {
        return {
          hasCulturalReference: false,
          proverbs: [],
          memesAndTrends: [],
          landmarks: [],
          gastronomy: [],
          slangExpressions: [],
          allMatches: [],
          culturalSummary: 'لا توجد إشارات ثقافية خاصة.'
        };
      }
      const lowerText = text.toLowerCase();
      const cultureDb = (typeof CULTURE_DATA !== 'undefined' && CULTURE_DATA) ? CULTURE_DATA : { proverbs: [], memes_and_trends: [], landmarks: [], gastronomy: [] };
      const slangDb = (typeof SLANG_DATA !== 'undefined' && SLANG_DATA) ? SLANG_DATA : { expressions: [] };

      const matchedProverbs = [];
      const matchedMemes = [];
      const matchedLandmarks = [];
      const matchedGastronomy = [];
      const matchedSlang = [];

      // 1. Proverbs
      for (const p of cultureDb.proverbs || []) {
        const pText = p.text || '';
        const pArabizi = p.arabizi || '';
        if ((pText && text.includes(pText)) || (pArabizi && lowerText.includes(pArabizi.toLowerCase()))) {
          matchedProverbs.push({
            matchedText: text.includes(pText) ? pText : pArabizi,
            category: 'proverb',
            canonicalName: pText,
            meaning: p.meaning || '',
            metadata: { category: p.category, region: p.region }
          });
        }
      }

      // 2. Memes & Trends
      for (const m of cultureDb.memes_and_trends || []) {
        const mPhrase = m.phrase || '';
        const mArabizi = m.arabizi || '';
        if ((mPhrase && text.includes(mPhrase)) || (mArabizi && lowerText.includes(mArabizi.toLowerCase()))) {
          matchedMemes.push({
            matchedText: text.includes(mPhrase) ? mPhrase : mArabizi,
            category: 'meme_trend',
            canonicalName: mPhrase,
            meaning: m.meaning || '',
            metadata: { tone: m.tone, context: m.context }
          });
        }
      }

      // 3. Landmarks
      for (const lmk of cultureDb.landmarks || []) {
        const lName = lmk.name || '';
        const keywords = extractKeywords(lName);
        for (const kw of keywords) {
          if (kw && text.includes(kw)) {
            matchedLandmarks.push({
              matchedText: kw,
              category: 'landmark',
              canonicalName: lName,
              meaning: lmk.description || '',
              metadata: { city: lmk.city, wilaya_code: lmk.wilaya_code }
            });
            break;
          }
        }
      }

      // 4. Gastronomy
      for (const f of cultureDb.gastronomy || []) {
        const fName = f.name || '';
        const fArabizi = f.arabizi || '';
        const keywords = extractKeywords(fName);
        let matched = false;
        for (const kw of keywords) {
          if (kw && text.includes(kw)) {
            matchedGastronomy.push({
              matchedText: kw,
              category: 'gastronomy',
              canonicalName: fName,
              meaning: f.description || '',
              metadata: { origin: f.origin, category: f.category }
            });
            matched = true;
            break;
          }
        }
        if (!matched && fArabizi) {
          const parts = fArabizi.split('/');
          for (const part of parts) {
            if (part.trim() && lowerText.includes(part.trim().toLowerCase())) {
              matchedGastronomy.push({
                matchedText: part.trim(),
                category: 'gastronomy',
                canonicalName: fName,
                meaning: f.description || '',
                metadata: { origin: f.origin, category: f.category }
              });
              break;
            }
          }
        }
      }

      // 5. Slang Expressions
      for (const s of slangDb.expressions || []) {
        const sTerm = s.term || '';
        const sArabizi = s.arabizi || '';
        const keywords = extractKeywords(sTerm);
        let matched = false;
        for (const kw of keywords) {
          if (kw && text.includes(kw)) {
            matchedSlang.push({
              matchedText: kw,
              category: 'slang',
              canonicalName: sTerm,
              meaning: s.meaning || '',
              metadata: { type: s.type, polarity: s.polarity }
            });
            matched = true;
            break;
          }
        }
        if (!matched && sArabizi && lowerText.includes(sArabizi.toLowerCase())) {
          matchedSlang.push({
            matchedText: sArabizi,
            category: 'slang',
            canonicalName: sTerm,
            meaning: s.meaning || '',
            metadata: { type: s.type, polarity: s.polarity }
          });
        }
      }

      const allMatches = [
        ...matchedProverbs,
        ...matchedMemes,
        ...matchedLandmarks,
        ...matchedGastronomy,
        ...matchedSlang
      ];

      const summaryParts = [];
      if (matchedProverbs.length > 0) summaryParts.push(`أمثال شعبية: ${matchedProverbs.map(p => `"${p.canonicalName}"`).join('، ')}`);
      if (matchedMemes.length > 0) summaryParts.push(`ترندات وميمز: ${matchedMemes.map(m => `"${m.canonicalName}"`).join('، ')}`);
      if (matchedLandmarks.length > 0) summaryParts.push(`معالم وأسواق: ${matchedLandmarks.map(l => `"${l.canonicalName}"`).join('، ')}`);
      if (matchedGastronomy.length > 0) summaryParts.push(`مأكولات جزائرية: ${matchedGastronomy.map(f => `"${f.canonicalName}"`).join('، ')}`);
      if (matchedSlang.length > 0) summaryParts.push(`مصطلحات شارع: ${matchedSlang.map(s => `"${s.canonicalName}"`).join('، ')}`);

      return {
        hasCulturalReference: allMatches.length > 0,
        proverbs: matchedProverbs,
        memesAndTrends: matchedMemes,
        landmarks: matchedLandmarks,
        gastronomy: matchedGastronomy,
        slangExpressions: matchedSlang,
        allMatches,
        culturalSummary: summaryParts.length > 0 ? summaryParts.join(' | ') : 'لا توجد إشارات ثقافية خاصة.'
      };
    }

    function detectScript(text) {
      const latinCount = (text.match(/[a-zA-Z]/g) || []).length;
      const arabicCount = (text.match(/[\u0600-\u06FF]/g) || []).length;
      return arabicCount > latinCount ? 'arabic' : 'arabizi';
    }

    function respondToDarja(text, persona = 'casual') {
      if (!text || !text.trim()) {
        return { reply: 'مرحباً بيك خويا، كاش ما نسحقو نخدموك؟', intent: 'EMPTY', script: 'arabic' };
      }
      const resolvedScript = detectScript(text);
      const normInput = text.toLowerCase().replace(/[!?.,;:\-_/\\]+/g, ' ').replace(/\s+/g, ' ').trim();
      const rules = (DIALOGUE_RULES_DATA && DIALOGUE_RULES_DATA.rules) || [];

      for (const rule of rules) {
        const patterns = resolvedScript === 'arabizi' ? rule.patterns_arabizi : rule.patterns_arabic;
        const altPatterns = resolvedScript === 'arabizi' ? rule.patterns_arabic : rule.patterns_arabizi;

        for (const p of patterns) {
          const normP = p.toLowerCase().trim();
          if (normInput.includes(normP) || normP.includes(normInput)) {
            const responses = resolvedScript === 'arabizi' ? rule.responses_arabizi : rule.responses_arabic;
            let chosen = responses[0] || '';
            if (persona === 'merchant' && rule.intent === 'WELLBEING_INQUIRY') {
              chosen = resolvedScript === 'arabizi' ? 'We cv hamdoulah kho! Marhba bik f la boutique ta3na, kash ma khasek sel3a?' : 'لاباس الحمد لله ربي يحفظك خويا! مرحباً بيك في متجرنا، كاش ما راك تحوس سلعة؟';
            }
            return { reply: chosen, intent: rule.intent, script: resolvedScript };
          }
        }
        for (const p of altPatterns) {
          const normP = p.toLowerCase().trim();
          if (normInput.includes(normP)) {
            const responses = resolvedScript === 'arabizi' ? rule.responses_arabizi : rule.responses_arabic;
            return { reply: responses[0] || '', intent: rule.intent, script: resolvedScript };
          }
        }
      }

      if (resolvedScript === 'arabizi') {
        return { reply: 'We cv hamdoulah w nta kho? Marhba bik!', intent: 'CASUAL_CHAT', script: 'arabizi' };
      }
      return { reply: 'مرحباً بيك خويا العزيز! واش راك وكاش ما نسحقو نخدموك؟', intent: 'CASUAL_CHAT', script: 'arabic' };
    }

    function detectProfanity(text) {
      if (!text || !text.trim()) return { isProfane: false, severity: 'none', matches: [], censoredText: text };
      const termsList = (PROFANITY_DATA && PROFANITY_DATA.terms) || [];
      const normText = text.toLowerCase().replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/(.)\1{2,}/g, '$1$1');
      const matches = [];
      const censoredChars = text.split('');
      let highestSeverity = 'none';
      const severityOrder = { none: 0, low: 1, medium: 2, high: 3 };

      for (const item of termsList) {
        const variants = [];
        if (item.ar) variants.push(item.ar);
        if (item.arabizi) variants.push(...item.arabizi);

        for (const v of variants) {
          if (!v) continue;
          const escaped = v.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const pattern = new RegExp(`(?<![\\w\u0600-\u06FF])${escaped}(?![\\w\u0600-\u06FF])`, 'gi');
          let m;
          while ((m = pattern.exec(normText)) !== null) {
            const start = m.index;
            const end = start + m[0].length;
            matches.push({ term: item.term || v, category: item.category, severity: item.severity, matchedText: text.slice(start, end) });
            if (severityOrder[item.severity] > severityOrder[highestSeverity]) highestSeverity = item.severity;
            for (let i = start; i < Math.min(end, censoredChars.length); i++) censoredChars[i] = '*';
          }
        }
      }
      const isProfane = matches.length > 0;
      return {
        isProfane,
        severity: isProfane ? highestSeverity : 'none',
        matches,
        censoredText: censoredChars.join('').replace(/\*+/g, '***')
      };
    }

    // UI Controller
    const inputArea = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');

    const SAMPLES = [
      "salam khoya hab 2 hbat k7la taille L b 2 mlayen w 500 alf l Rouiba fi Alger b yalidine. num ta3i: 0661234567",
      "بشحال هاذي خاوة السومة تاعها قداش؟ كاش جديد متوفر منها ولا خلاصت؟",
      "السلعة هاااااايلة بزاااااف و الخدمة فور، يعطيك الصحة! توصيل للعلمة سطيف رقمي 0770112233 و نخلصك بـ baridimob",
      "سراقين حشيتوهالي رجعولي دراهمي سلعة خردة وما رديتوش عليا ونشكي بيكم للعدالة ولابوليس!",
      "شوالا راك باغي خوية غايا درك؟ حاب دوزينة مقاس 42 لعين الترك ولاية 31 بـ zr express للدار و نخلصك كاش",
      "واشنهي هادا قداش التوصيل لقسنطينة سيرتا و وقتاش تلحق؟ نخلصك كاش بـ مية الف",
      "طاح الحك وصاب غطاه، ابعثلي رشتة عاصمية و طبق شخشوخة لباب الواد و نخلصك كاش",
      "تيكي تاكا يا خويا الكولي وصلني وسلعتكم كابا أصلية ولوز وهبال يعطيكم الصحة",
      "wach ya khoy",
      "يا حمار ما تبعثليش سلعة خردة وناقصة",
      "قالو فاك يا حشيشة و زوخ وطير و وان تو ثري فيفا لالجيري"
    ];

    function loadSample(idx) {
      inputArea.value = SAMPLES[idx];
      processText();
    }

    function processText() {
      const text = inputArea.value;
      charCount.textContent = `${text.length} حرف`;

      // Escalation Detection
      const esc = detectEscalation(text);
      const escBox = document.getElementById('escalationStatusBox');
      if (esc.needsEscalation) {
        escBox.innerHTML = `
          <div class="escalation-alert">
            <span style="font-size:22px;">🚨</span>
            <div>
              <div style="font-weight:800; font-size:15px; color:#f87171;">تنبيه تصعيد بشري عاجل (Human Escalation Required)</div>
              <div style="font-size:13px; margin-top:2px;">السبب: <strong>${esc.reason}</strong> (درجة الإلحاح: <strong>${esc.urgency}</strong>) — ${esc.guideline}</div>
              <div style="font-size:11px; color:#fca5a5; margin-top:4px;">الكلمات المفتاحية المرصودة: ${esc.matchedTriggers.join(', ')}</div>
            </div>
          </div>
        `;
      } else {
        escBox.innerHTML = `
          <div class="escalation-healthy">
            <span>✅</span>
            <span>محادثة طبيعية: لا تتطلب تدخلاً بشرياً عاجلاً، يمكن لوكيل الذكاء الاصطناعي الرد تلقائياً.</span>
          </div>
        `;
      }

      // 1. Intent Classification
      const intentRes = identifyIntent(text);
      const iBadge = document.getElementById('intentBadge');
      const iConf = document.getElementById('intentConfidence');
      const iKws = document.getElementById('intentKeywords');

      const intentDisplay = {
        ORDER: { label: '🛒 طلب شراء (ORDER)', cls: 'intent-order' },
        PRICE_INQUIRY: { label: '💰 استفسار عن السعر (PRICE_INQUIRY)', cls: 'intent-price' },
        DELIVERY_INQUIRY: { label: '🚚 استفسار عن التوصيل (DELIVERY_INQUIRY)', cls: 'intent-delivery' },
        AVAILABILITY_INQUIRY: { label: '📦 توفر السلعة (AVAILABILITY_INQUIRY)', cls: 'intent-availability' },
        COMPLAINT: { label: '⚠️ شكوى / مشكلة (COMPLAINT)', cls: 'intent-complaint' },
        GREETING: { label: '👋 تحية وتواصل (GREETING)', cls: 'intent-greeting' },
        UNKNOWN: { label: '❓ غير محدد (UNKNOWN)', cls: 'intent-unknown' }
      };

      const info = intentDisplay[intentRes.intent] || intentDisplay.UNKNOWN;
      iBadge.className = 'intent-badge ' + info.cls;
      iBadge.textContent = info.label;
      iConf.textContent = intentRes.confidence > 0 ? `دقة ${(intentRes.confidence * 100).toFixed(0)}%` : '-';

      iKws.innerHTML = '';
      if (intentRes.matchedKeywords.length > 0) {
        intentRes.matchedKeywords.forEach(k => {
          iKws.innerHTML += `<span class="token-pill" style="background:#1e293b; color:#38bdf8; border:1px solid #0284c7;">${k}</span>`;
        });
      } else {
        iKws.innerHTML = '<span class="empty-state">لا توجد كلمات نية صريحة</span>';
      }

      // 2. Sentiment
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
      sBadge.textContent = {
        POSITIVE: 'إيجابي (+)',
        NEGATIVE: 'سلبي (-)',
        MIXED: 'مختلط (~)',
        NEUTRAL: 'محايد (o)'
      }[sent.label] || sent.label;

      tokensBox.innerHTML = '';
      sent.positiveTokens.forEach(t => {
        tokensBox.innerHTML += `<span class="token-pill token-pos">+ ${t}</span>`;
      });
      sent.negativeTokens.forEach(t => {
        tokensBox.innerHTML += `<span class="token-pill token-neg">- ${t}</span>`;
      });
      if (sent.positiveTokens.length === 0 && sent.negativeTokens.length === 0) {
        tokensBox.innerHTML = '<span class="empty-state">لا توجد كلمات مشاعر مباشرة</span>';
      }
      negFlag.style.display = sent.negated ? 'block' : 'none';

      // 3. Wilayas & Entities
      const entities = extractEntities(text);
      const wilayasBox = document.getElementById('wilayasBox');
      const paymentsBox = document.getElementById('paymentsBox');
      const pricesBox = document.getElementById('pricesBox');

      wilayasBox.innerHTML = '';
      if (entities.wilayas.length > 0) {
        entities.wilayas.forEach(w => {
          const comBadge = w.commune ? `<span class="commune-badge">📍 بلدية ${w.commune}</span>` : '';
          wilayasBox.innerHTML += `
            <div class="entity-tag">
              <span class="entity-code">${w.code_str || w.code}</span>
              <strong>${w.name_ar}</strong>
              <span style="color:var(--text-muted); font-size:11px;">(${w.name_fr})</span>
              ${comBadge}
            </div>
          `;
        });
      } else {
        wilayasBox.innerHTML = '<span class="empty-state">لم يتم رصد ولايات أو بلديات في النص</span>';
      }

      // 4. Quantities & Product Attributes
      const quantities = extractQuantities(text);
      const attrs = extractProductAttributes(text);
      const quantitiesBox = document.getElementById('quantitiesBox');
      const attributesBox = document.getElementById('attributesBox');

      quantitiesBox.innerHTML = '';
      if (quantities.length > 0) {
        quantities.forEach(q => {
          quantitiesBox.innerHTML += `<span class="qty-tag">📦 ${q.value} ${q.unit} (${q.raw})</span> `;
        });
      } else {
        quantitiesBox.innerHTML = '<span class="empty-state">لم ترصد كميات محددة</span>';
      }

      attributesBox.innerHTML = '';
      if (attrs.colors.length > 0 || attrs.sizes.length > 0) {
        attrs.colors.forEach(c => {
          attributesBox.innerHTML += `<span class="attr-tag">🎨 ${c}</span> `;
        });
        attrs.sizes.forEach(s => {
          attributesBox.innerHTML += `<span class="attr-tag">📏 مقاس ${s}</span> `;
        });
      } else {
        attributesBox.innerHTML = '<span class="empty-state">لا توجد ألوان أو مقاسات مرصودة</span>';
      }

      // Payments & Prices
      paymentsBox.innerHTML = '';
      if (entities.payments.length > 0) {
        entities.payments.forEach(p => {
          paymentsBox.innerHTML += `<span class="payment-tag">${p.label}</span> `;
        });
      } else {
        paymentsBox.innerHTML = '<span class="empty-state">لا توجد وسيلة دفع محددة</span>';
      }

      pricesBox.innerHTML = '';
      if (entities.prices.length > 0) {
        entities.prices.forEach(pr => {
          pricesBox.innerHTML += `<span class="price-tag">${pr.raw} &rarr; ${pr.amount.toLocaleString()} دج</span> `;
        });
      } else {
        pricesBox.innerHTML = '<span class="empty-state">لا توجد أسعار مرصودة</span>';
      }

      // Logistics & Phones with Operator & WhatsApp
      const deliveriesBox = document.getElementById('deliveriesBox');
      const phonesBox = document.getElementById('phonesBox');

      deliveriesBox.innerHTML = '';
      if (entities.deliveries && entities.deliveries.length > 0) {
        entities.deliveries.forEach(d => {
          deliveriesBox.innerHTML += `<span class="carrier-tag">${d.label}</span> `;
        });
      }
      if (entities.deliveryMode) {
        deliveriesBox.innerHTML += `<span class="mode-tag">${entities.deliveryMode}</span>`;
      }
      if ((!entities.deliveries || entities.deliveries.length === 0) && !entities.deliveryMode) {
        deliveriesBox.innerHTML = '<span class="empty-state">لم تحدد شركة توصيل أو نمط</span>';
      }

      phonesBox.innerHTML = '';
      if (entities.phones && entities.phones.length > 0) {
        entities.phones.forEach(ph => {
          const opBadge = ph.operatorLabel ? `<span class="operator-tag ${ph.opClass}">${ph.operatorLabel}</span>` : '';
          const waLink = ph.waUrl ? `<a href="${ph.waUrl}" target="_blank" class="wa-btn">💬 واتساب</a>` : '';
          phonesBox.innerHTML += `
            <div class="phone-tag">
              <span>📞 ${ph.normalized}</span>
              ${opBadge}
              ${waLink}
            </div>
          `;
        });
      } else {
        phonesBox.innerHTML = '<span class="empty-state">لا توجد أرقام هواتف مرصودة</span>';
      }

      // 5. Dialect
      const dialect = detectDialect(text);
      const dBadge = document.getElementById('dialectBadge');
      const dMarkers = document.getElementById('dialectMarkers');
      const regionNames = {
        WEST: 'الغرب الجزائري (WEST - وهران وتلمسان)',
        EAST: 'الشرق الجزائري (EAST - قسنطينة وسطيف وعنابة)',
        CENTER: 'الوسط الجزائري (CENTER - الجزائر والبليدة)',
        SOUTH: 'الجنوب الجزائري (SOUTH - الصحراء والواحات)',
        GENERAL_DARJA: 'دارجة جزائرية عامة (GENERAL)'
      };
      dBadge.textContent = regionNames[dialect.region] || dialect.region;
      dMarkers.innerHTML = '';
      if (dialect.detectedMarkers.length > 0) {
        dialect.detectedMarkers.forEach(m => {
          dMarkers.innerHTML += `<span class="token-pill" style="background:#1e293b; color:#60a5fa; border:1px solid #3b82f6;">${m}</span>`;
        });
      } else {
        dMarkers.innerHTML = '<span class="empty-state">لا توجد مؤشرات جهوية حصرية</span>';
      }

      // 6. Cultural & Slang Detection
      const cultural = detectCulturalReferences(text);
      const cultBox = document.getElementById('culturalBox');
      cultBox.innerHTML = '';
      if (cultural.allMatches.length > 0) {
        cultural.allMatches.forEach(m => {
          let badgeStyle = 'background:rgba(59,130,246,0.15); border:1px solid #3b82f6; color:#60a5fa;';
          let icon = '🏛️';
          let catTitle = 'معلم / سوق';
          if (m.category === 'proverb') {
            badgeStyle = 'background:rgba(245,158,11,0.15); border:1px solid #f59e0b; color:#fbbf24;';
            icon = '📜';
            catTitle = 'مثل شعبي';
          } else if (m.category === 'meme_trend') {
            badgeStyle = 'background:rgba(236,72,153,0.15); border:1px solid #ec4899; color:#f472b6;';
            icon = '🎭';
            catTitle = 'ترند / ميم';
          } else if (m.category === 'gastronomy') {
            badgeStyle = 'background:rgba(16,185,129,0.15); border:1px solid #10b981; color:#34d399;';
            icon = '🍲';
            catTitle = 'أكلة / طبق';
          } else if (m.category === 'slang') {
            badgeStyle = 'background:rgba(139,92,246,0.15); border:1px solid #8b5cf6; color:#a78bfa;';
            icon = '💬';
            catTitle = 'مصطلح شارع';
          }
          cultBox.innerHTML += `
            <div style="${badgeStyle} border-radius:8px; padding:6px 10px; font-size:12px; display:flex; align-items:center; gap:8px;">
              <span style="font-size:16px;">${icon}</span>
              <div>
                <strong>${catTitle}: ${m.canonicalName}</strong>
                <span style="opacity:0.85; margin-right:6px;">(${m.meaning})</span>
              </div>
            </div>
          `;
        });
      } else {
        cultBox.innerHTML = '<span class="empty-state">لا توجد إشارات شعبية أو أمثال في النص</span>';
      }

      // 7. Arabizi & Normalization
      const arabiziClean = arabiziToArabic(text);
      document.getElementById('arabiziBox').textContent = arabiziClean || '-';
      document.getElementById('normalizedBox').textContent = normalize(text) || '-';

      // 8. Natural Darja Dialogue Response Engine
      const chatRes = respondToDarja(text);
      document.getElementById('dialogueReplyBox').textContent = chatRes.reply;
      const scriptBadge = document.getElementById('dialogueScriptBadge');
      scriptBadge.textContent = chatRes.script === 'arabizi' ? '🔤 Arabizi' : '🔤 عربية';
      const intentBadge = document.getElementById('dialogueIntentBadge');
      intentBadge.textContent = chatRes.intent;

      // 9. Content Moderation & Profanity Shield
      const profRes = detectProfanity(text);
      const profStatusBox = document.getElementById('profanityStatusBox');
      const censoredBox = document.getElementById('censoredTextBox');
      censoredBox.textContent = profRes.censoredText;
      if (profRes.isProfane) {
        profStatusBox.innerHTML = `
          <div style="background:rgba(239,68,68,0.15); border:1px solid #ef4444; color:#f87171; border-radius:8px; padding:8px 12px; font-size:13px; font-weight:700;">
            ⚠️ تم رصد محتوى بذيء أو شتائم (درجة الخطورة: ${profRes.severity.toUpperCase()}) — ${profRes.matches.length} كلمة مرصودة
          </div>
        `;
      } else {
        profStatusBox.innerHTML = `
          <div style="background:rgba(16,185,129,0.15); border:1px solid #10b981; color:#34d399; border-radius:8px; padding:8px 12px; font-size:13px; font-weight:700;">
            ✅ المحتوى آمن ونظيف (Clean & Safe)
          </div>
        `;
      }

      // 8. AI Agent Simulator
      let wilayaName = null;
      if (entities.wilayas.length > 0) {
        const firstW = entities.wilayas[0];
        const comPart = firstW.commune ? ' - بلدية ' + firstW.commune : '';
        wilayaName = `${firstW.name_ar} (${firstW.code_str || firstW.code})${comPart}`;
      }
      const carrierName = entities.deliveries && entities.deliveries.length > 0 ? entities.deliveries[0].label : null;
      const priceText = entities.prices.length > 0 ? entities.prices[0].amount.toLocaleString() + ' دج' : null;
      const qtyText = quantities.length > 0 ? quantities.map(q => `${q.value} ${q.unit}`).join(', ') : 'غير محددة';
      const attrText = (attrs.colors.concat(attrs.sizes)).join(' | ') || 'غير محدد';

      const escNotice = esc.needsEscalation ? `\n🚨 [تنبيه تصعيد عاجل]: ${esc.reason} (${esc.urgency}) - ${esc.guideline}\n` : '';
      const culturalLine = cultural.hasCulturalReference ? `\n- المراجع الثقافية والتراثية المرصودة: ${cultural.culturalSummary}` : '';

      const agentPrompt = `أنت مساعد خدمة عملاء ذكي وبشري لمتجر إلكتروني جزائري 'Bazar El Djazair'.${escNotice}
[سياق الزبون المستخرج بدقة عبر darja-nlp-kit]:
- الرسالة الأصلية: "${text}"
- الترجمة التفسيرية: "${arabiziClean}"
- النية الأساسية (Intent): ${intentRes.intent} (${info.label})
- المنطقة واللهجة: ${dialect.region} (${regionNames[dialect.region] || 'عامة'})
- المزاج والشعور: ${sent.label} (الدرجة: ${sent.score.toFixed(2)})
- الولاية والبلدية: ${wilayaName || 'غير محددة'}
- الكمية المطلوبة: ${qtyText}
- المواصفات (ألوان ومقاسات): ${attrText}
- شركة التوصيل: ${carrierName || 'غير محددة'}
- المبالغ بالدينار: ${priceText || 'غير محددة'}
- وسائل الدفع: ${entities.payments.length > 0 ? entities.payments.map(p => p.label).join(', ') : 'غير محددة'}
- أرقام الهاتف: ${entities.phones.length > 0 ? entities.phones.map(ph => ph.normalized + (ph.operatorLabel ? ' ('+ph.operatorLabel+')' : '')).join(', ') : 'غير متوفرة'}${culturalLine}

[التعليمات]: طابق نية الزبون ولهجته بدقة، وأجب بدارجة جزائرية عفوية ومحترمة (لا فصحى معربة)، والتزم بالأسعار والولايات بدون أي هلوسة.`;

      document.getElementById('agentPromptBox').textContent = agentPrompt;

      let agentReply = '';
      if (esc.needsEscalation) {
        agentReply = '🚨 تنبيه النظام: تم إيقاف الرد الآلي وتحويل المحادثة لمشرف خدمة العملاء البشري بسبب التصعيد (' + esc.reason + ').';
      } else if (cultural.proverbs.length > 0) {
        const prov = cultural.proverbs[0];
        agentReply = `وعليكم السلام خويا لعزيز! كيما يقول المثل الشعبي "${prov.canonicalName}". رانا في الخدمة وسلعتنا مضمونة ونوصلوها حتى لباب دارك، مرحب بيك في كل وقت!`;
      } else if (cultural.gastronomy.length > 0) {
        const food = cultural.gastronomy[0];
        agentReply = `أهلاً وسهلاً خويا! بصحتكم مسبقاً ${food.canonicalName}، بنة وهمة وشان. سلعتنا راهي واجدة والتوصيل متوفر لجميع الولايات مع خيار الدفع عند الاستلام!`;
      } else if (intentRes.intent === 'COMPLAINT' || sent.label === 'NEGATIVE') {
        agentReply = 'سلام عليكم خويا، حقك علينا ونعتذروا منك بزاف بزاف! ما تقلقش روحك كامل، المشكل نحلوهولك درك. قولي برك واش صرا بالضبط ونبدلولك السلعة ولا نرجعولك دراهمك في الحين.';
      } else if (intentRes.intent === 'PRICE_INQUIRY') {
        const pDesc = priceText ? `السعر راهو ${priceText}` : 'السعر راهو مدروس وفي متناول الجميع';
        agentReply = `وعليكم السلام خويا لعزيز! ${pDesc}. والتوصيل متوفر لجميع الولايات (خدمة سريعة للدار أو المكتب). تحب نسجلك طلبية؟`;
      } else if (intentRes.intent === 'AVAILABILITY_INQUIRY') {
        agentReply = 'أهلاً خويا! السلعة مازالت متوفرة والستوك كاين، بصح الكمية محدودة بزاف. إذا راك مهتم ابعثلي معلوماتك درك نريڤلوهالك قبل ما تفرى!';
      } else {
        const targetWilaya = wilayaName ? 'لـ ' + wilayaName : 'عندك';
        const targetPrice = priceText ? 'والحساب راهو ' + priceText : 'والسعر مضبوط';
        const targetCarrier = carrierName ? 'مع ' + carrierName : 'مع شركة التوصيل';

        if (dialect.region === 'WEST') {
          agentReply = `وعليكم السلام خويا لعزيز! مرحبا بيك، السلعة راها كاينة ونوصلوها ${targetWilaya} ${targetCarrier}. ${targetPrice}. تقدر تفيرسي في BaridiMob ولا تخلص كاش كي توصلك السلعة غايا!`;
        } else if (dialect.region === 'EAST') {
          agentReply = `أهلاً وسهلاً بيك خويا ربي يحفظك! سلعة لوز وضرك نوجدوهالك ${targetWilaya} ${targetCarrier}، ${targetPrice}. تقدر تخلص بالـ BaridiMob ولا تكاشي كي يوصلهالك الليفرور، عيشك!`;
        } else if (dialect.region === 'SOUTH') {
          agentReply = `أهلاً وسهلاً بيك خويا وعلى الراس والعين! السلعة زينة ومضمونة وتوصلكم ${targetWilaya} ${targetCarrier}، ${targetPrice}. وربي يباركلك في رزقك. مرحب بيك في كل وقت!`;
        } else {
          agentReply = `سلام خويا، مرحبا بيك عندنا! ما كاش مشكل خلاص، السلعة متوفرة ونوصلوها ${targetWilaya} ${targetCarrier}، ${targetPrice}. بالنسبة للدفع تحب بريدي موب ولا كاش كي تلحقك السلعة للباب؟`;
        }
      }
      document.getElementById('agentReplyBox').textContent = agentReply;

      // Match few-shot dialogue
      const matchedDialogue = (DIALOGUES_DATA || []).find(d => d.region === dialect.region && d.intent === intentRes.intent)
        || (DIALOGUES_DATA || []).find(d => d.region === dialect.region)
        || (DIALOGUES_DATA || [])[0];

      const diagBox = document.getElementById('matchingDialogueBox');
      if (matchedDialogue && diagBox) {
        diagBox.innerHTML = `
          <div style="margin-bottom:6px;"><span style="background:#3b82f6; color:#fff; font-size:11px; padding:2px 7px; border-radius:4px; font-weight:700;">${matchedDialogue.region}</span> <span style="color:#f59e0b; font-weight:700;">سؤال الزبون:</span> "${matchedDialogue.customer_message}"</div>
          <div><span style="background:#10b981; color:#fff; font-size:11px; padding:2px 7px; border-radius:4px; font-weight:700;">رد التاجر البشري</span> <span style="color:#34d399; font-weight:700;">رد التاجر الواقعي:</span> "${matchedDialogue.merchant_response}"</div>
        `;
      }
    }

    inputArea.addEventListener('input', processText);
    processText();
  </script>
</body>
</html>
"""

    html_content = template.replace(
        '__STOPWORDS_DATA__', json.dumps(stopwords_data, ensure_ascii=False)
    ).replace(
        '__LEXICON_DATA__', json.dumps(lexicon_data, ensure_ascii=False)
    ).replace(
        '__ARABIZI_RULES__', json.dumps(arabizi_rules, ensure_ascii=False)
    ).replace(
        '__WILAYAS_DATA__', json.dumps(wilayas_data, ensure_ascii=False)
    ).replace(
        '__DIALECTS_DATA__', json.dumps(dialects_data, ensure_ascii=False)
    ).replace(
        '__DIALOGUES_DATA__', json.dumps(dialogues_data, ensure_ascii=False)
    ).replace(
        '__CULTURE_DATA__', json.dumps(culture_data, ensure_ascii=False)
    ).replace(
        '__SLANG_DATA__', json.dumps(slang_data, ensure_ascii=False)
    ).replace(
        '__PROFANITY_DATA__', json.dumps(profanity_data, ensure_ascii=False)
    ).replace(
        '__DIALOGUE_RULES_DATA__', json.dumps(dialogue_rules_data, ensure_ascii=False)
    ).replace(
        '__MEMES_DATA__', json.dumps(memes_data, ensure_ascii=False)
    ).replace(
        '__FRANCO_DATA__', json.dumps(franco_data, ensure_ascii=False)
    )

    out_file = docs_dir / 'index.html'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f'[OK] Standalone web playground generated successfully at: {out_file}')


if __name__ == '__main__':
    main()
