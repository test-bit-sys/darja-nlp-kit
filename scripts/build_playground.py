"""Builds a standalone, zero-dependency Web Playground Studio for GitHub Pages in docs/index.html."""
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

    sentiment_model_path = data_dir / 'sentiment_model.json'
    sentiment_model_data = (
        json.load(open(sentiment_model_path, 'r', encoding='utf-8'))
        if sentiment_model_path.exists()
        else {}
    )

    dialogue_kb_path = data_dir / 'dialogue_kb.json'
    dialogue_kb_data = (
        json.load(open(dialogue_kb_path, 'r', encoding='utf-8'))
        if dialogue_kb_path.exists()
        else {'entries': []}
    )

    template = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>darja-nlp-kit | استوديو المعالجة اللغوية للدارجة الجزائرية</title>
  <meta name="description" content="Zero-dependency dual-language (Python & TypeScript) NLP toolkit for Algerian Darja: 69 Wilayas, Hybrid 55K ML Sentiment, DarjaPipeline, DarjaClassifier, DarjaChat.">
  <link rel="icon" type="image/jpeg" href="logo.jpg?v=2">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #060a12;
      --bg-elevated: #0c1220;
      --card-bg: #101829;
      --card-bg-alt: #0d1424;
      --border: #1e293b;
      --border-strong: #2b3b55;
      --primary: #10b981;
      --primary-hover: #059669;
      --primary-soft: rgba(16, 185, 129, 0.14);
      --primary-glow: rgba(16, 185, 129, 0.25);
      --crimson: #ef4444;
      --crimson-soft: rgba(239, 68, 68, 0.14);
      --amber: #f59e0b;
      --amber-soft: rgba(245, 158, 11, 0.14);
      --blue: #3b82f6;
      --blue-soft: rgba(59, 130, 246, 0.14);
      --cyan: #06b6d4;
      --purple: #a855f7;
      --text: #f1f5f9;
      --text-secondary: #cbd5e1;
      --text-muted: #94a3b8;
      --radius: 16px;
      --radius-sm: 10px;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg);
      background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(16, 185, 129, 0.12), transparent),
        radial-gradient(ellipse 50% 40% at 90% 10%, rgba(239, 68, 68, 0.05), transparent);
      color: var(--text);
      font-family: 'Cairo', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.6;
      overflow-x: hidden;
    }

    code, pre, .mono {
      font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace;
      direction: ltr;
      unicode-bidi: isolate;
    }

    /* Sticky Topbar */
    .topbar {
      position: sticky;
      top: 0;
      z-index: 50;
      background: rgba(6, 10, 18, 0.85);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border);
    }

    .topbar-inner {
      max-width: 1200px;
      margin: 0 auto;
      padding: 10px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      flex-wrap: wrap;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      text-decoration: none;
      color: var(--text);
    }

    .brand-logo {
      width: 36px;
      height: 36px;
      border-radius: 9px;
      object-fit: cover;
      border: 1px solid var(--border-strong);
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.2);
    }

    .brand-title {
      font-weight: 900;
      font-size: 0.98rem;
      letter-spacing: -0.3px;
      display: flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }

    .brand-pill {
      font-size: 10px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 999px;
      background: var(--primary-soft);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.35);
    }

    .nav-tabs {
      display: flex;
      align-items: center;
      gap: 4px;
      background: var(--bg-elevated);
      padding: 4px;
      border-radius: 11px;
      border: 1px solid var(--border);
      flex-wrap: wrap;
    }

    .nav-tab {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 11px;
      border-radius: 7px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-family: inherit;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.18s ease;
    }

    .nav-tab:hover {
      color: var(--text);
      background: rgba(255, 255, 255, 0.04);
    }

    .nav-tab.active {
      background: var(--primary);
      color: #03150e;
      box-shadow: 0 2px 12px var(--primary-glow);
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .icon-link {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 6px 10px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--bg-elevated);
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
      transition: all 0.18s ease;
    }

    .icon-link:hover {
      border-color: var(--primary);
      color: #fff;
      transform: translateY(-1px);
    }

    /* Main Container */
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 18px 20px 60px;
      width: 100%;
    }

    /* Hero */
    .hero {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      padding: 6px 0 18px;
      margin-bottom: 6px;
    }

    .hero-logo-wrap {
      position: relative;
      margin-bottom: 10px;
    }

    .hero-logo {
      width: 68px;
      height: 68px;
      border-radius: 17px;
      object-fit: cover;
      border: 1px solid rgba(255, 255, 255, 0.14);
      box-shadow: 0 10px 26px rgba(16, 185, 129, 0.22);
    }

    .hero h1 {
      font-size: clamp(1.75rem, 3.6vw, 2.45rem);
      font-weight: 900;
      letter-spacing: -0.5px;
      line-height: 1.2;
      margin-bottom: 8px;
      background: linear-gradient(135deg, #ffffff 35%, #34d399 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero p {
      max-width: 740px;
      color: var(--text-muted);
      font-size: 14.5px;
      margin-bottom: 14px;
    }

    .stats-strip {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 10px;
    }

    .stat-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 999px;
      background: var(--card-bg);
      border: 1px solid var(--border);
      font-size: 12px;
      color: var(--text-secondary);
      font-weight: 600;
    }

    .stat-pill strong {
      color: #34d399;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Panels / Views */
    .tab-panel {
      display: none;
    }

    .tab-panel.active {
      display: block;
      animation: fadeIn 0.2s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Cards */
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 12px 28px -12px rgba(0, 0, 0, 0.5);
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }

    .section-title {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
      font-weight: 800;
      color: #34d399;
      letter-spacing: 0.2px;
    }

    .section-title svg {
      flex-shrink: 0;
    }

    /* Form Controls */
    textarea, input[type="text"], select {
      width: 100%;
      background: #070b13;
      border: 1.5px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-family: inherit;
      font-size: 15px;
      padding: 13px 16px;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    textarea:focus, input[type="text"]:focus, select:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
    }

    textarea.main-input {
      height: 112px;
      resize: vertical;
      line-height: 1.65;
    }

    .controls-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--border);
    }

    .seg-group {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: #070b13;
      border: 1px solid var(--border);
      padding: 3px;
      border-radius: 10px;
    }

    .seg-label {
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 700;
      margin-left: 6px;
    }

    .seg-btn {
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-family: inherit;
      font-size: 12px;
      font-weight: 700;
      padding: 5px 11px;
      border-radius: 7px;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .seg-btn:hover {
      color: var(--text);
    }

    .seg-btn.active {
      background: #1e293b;
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.35);
    }

    .samples-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 7px;
      margin-top: 14px;
      align-items: center;
    }

    .sample-chip {
      background: #0f172a;
      border: 1px solid var(--border-strong);
      color: var(--text-secondary);
      padding: 5px 11px;
      border-radius: 8px;
      font-family: inherit;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .sample-chip:hover {
      background: #1e293b;
      color: #fff;
      border-color: var(--primary);
      transform: translateY(-1px);
    }

    .sample-chip.highlight-emerald {
      border-color: rgba(16, 185, 129, 0.5);
      color: #6ee7b7;
    }

    .sample-chip.highlight-danger {
      border-color: rgba(239, 68, 68, 0.45);
      color: #fca5a5;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      padding: 9px 16px;
      border-radius: 10px;
      border: 1px solid transparent;
      font-family: inherit;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.16s ease;
    }

    .btn-primary {
      background: var(--primary);
      color: #03150e;
    }

    .btn-primary:hover {
      background: var(--primary-hover);
      color: #fff;
    }

    .btn-secondary {
      background: #1e293b;
      border-color: var(--border-strong);
      color: var(--text);
    }

    .btn-secondary:hover {
      border-color: var(--primary);
      background: #263449;
    }

    /* Results Grid */
    .results-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(330px, 1fr));
      gap: 18px;
    }

    .full-span {
      grid-column: 1 / -1;
    }

    /* Badges & Tags */
    .intent-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 14px;
      border-radius: 10px;
      font-weight: 800;
      font-size: 14px;
    }
    .intent-order { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }
    .intent-price { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid #3b82f6; }
    .intent-delivery { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid #f59e0b; }
    .intent-availability { background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid #a855f7; }
    .intent-complaint { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }
    .intent-greeting { background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid #06b6d4; }
    .intent-unknown { background: rgba(100, 116, 139, 0.15); color: #94a3b8; border: 1px solid #64748b; }

    .escalation-alert {
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.55);
      border-radius: 14px;
      padding: 14px 18px;
      margin-bottom: 18px;
      display: flex;
      align-items: flex-start;
      gap: 12px;
      color: #fca5a5;
    }

    .escalation-healthy {
      background: rgba(16, 185, 129, 0.08);
      border: 1px solid rgba(16, 185, 129, 0.28);
      border-radius: 12px;
      padding: 10px 16px;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #6ee7b7;
      font-size: 13px;
    }

    .sentiment-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 16px;
      background: #070b13;
      border: 1px solid var(--border);
      border-radius: 12px;
      margin-bottom: 12px;
    }

    .sentiment-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 8px;
      font-weight: 800;
      font-size: 13px;
    }
    .badge-positive { background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid #10b981; }
    .badge-negative { background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid #ef4444; }
    .badge-neutral { background: rgba(148, 163, 184, 0.16); color: #cbd5e1; border: 1px solid #64748b; }
    .badge-mixed { background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid #f59e0b; }

    .prob-bar-wrap {
      margin: 10px 0 12px;
    }

    .prob-bar-track {
      display: flex;
      height: 8px;
      border-radius: 999px;
      overflow: hidden;
      background: #1e293b;
      margin-bottom: 6px;
    }

    .prob-seg-pos { background: #10b981; transition: width 0.25s ease; }
    .prob-seg-neu { background: #64748b; transition: width 0.25s ease; }
    .prob-seg-neg { background: #ef4444; transition: width 0.25s ease; }

    .prob-legend {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
    }

    .pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 6px;
    }

    .token-pill {
      padding: 3px 9px;
      border-radius: 6px;
      font-size: 12px;
      font-family: 'JetBrains Mono', monospace;
      direction: ltr;
      unicode-bidi: isolate;
    }
    .token-pos { background: rgba(16, 185, 129, 0.14); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }
    .token-neg { background: rgba(239, 68, 68, 0.14); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
    .token-info { background: #0f172a; color: #7dd3fc; border: 1px solid #0369a1; }

    .entity-tag {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 11px;
      background: #0f172a;
      border: 1px solid var(--border-strong);
      border-radius: 10px;
      font-size: 13px;
      margin: 3px;
    }

    .entity-code {
      background: var(--primary);
      color: #03150e;
      font-weight: 800;
      font-size: 11px;
      padding: 2px 6px;
      border-radius: 5px;
      font-family: 'JetBrains Mono', monospace;
    }

    .commune-badge {
      background: rgba(6, 182, 212, 0.16);
      color: #67e8f9;
      border: 1px solid #0891b2;
      font-size: 11px;
      padding: 1px 7px;
      border-radius: 5px;
    }

    .era69-badge {
      background: rgba(245, 158, 11, 0.16);
      color: #fcd34d;
      border: 1px solid rgba(245, 158, 11, 0.45);
      font-size: 10px;
      font-weight: 800;
      padding: 1px 6px;
      border-radius: 5px;
    }

    .payment-tag {
      background: rgba(168, 85, 247, 0.15);
      border: 1px solid rgba(168, 85, 247, 0.5);
      color: #e9d5ff;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      display: inline-block;
      margin: 3px;
    }

    .price-tag {
      background: rgba(16, 185, 129, 0.16);
      border: 1px solid #10b981;
      color: #6ee7b7;
      padding: 5px 11px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      display: inline-block;
      margin: 3px;
    }

    .carrier-tag {
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.55);
      color: #fde68a;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      display: inline-block;
      margin: 3px;
    }

    .mode-tag {
      background: rgba(59, 130, 246, 0.16);
      border: 1px solid rgba(59, 130, 246, 0.55);
      color: #93c5fd;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      display: inline-block;
      margin: 3px;
    }

    .phone-tag {
      background: #070b13;
      border: 1px solid var(--border-strong);
      padding: 6px 10px;
      border-radius: 9px;
      font-size: 12px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin: 3px;
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
      color: #03150e;
      font-weight: 800;
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 5px;
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
      background: rgba(236, 72, 153, 0.14);
      border: 1px solid #db2777;
      color: #f9a8d4;
      padding: 4px 10px;
      border-radius: 8px;
      font-size: 12px;
      display: inline-block;
      margin: 3px;
    }

    .code-box {
      background: #070b13;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 11px 14px;
      font-size: 14px;
      color: var(--text);
      word-break: break-word;
      min-height: 44px;
      margin-bottom: 10px;
    }

    .pre-code {
      background: #070b13;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      line-height: 1.55;
      color: #cbd5e1;
      max-height: 290px;
      overflow: auto;
      white-space: pre-wrap;
      direction: ltr;
      text-align: left;
    }

    .empty-state {
      color: var(--text-muted);
      font-size: 13px;
      font-style: italic;
    }

    /* Multi-turn Chat Simulator */
    .chat-layout {
      display: grid;
      grid-template-columns: minmax(0, 1.5fr) minmax(290px, 1fr);
      gap: 20px;
    }

    @media (max-width: 860px) {
      .chat-layout { grid-template-columns: 1fr; }
    }

    .chat-messages {
      background: #070b13;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
      height: 390px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 12px;
    }

    .msg-row {
      display: flex;
      flex-direction: column;
      max-width: 82%;
    }

    .msg-row.user { align-self: flex-start; }
    .msg-row.assistant { align-self: flex-end; }

    .msg-bubble {
      padding: 10px 14px;
      border-radius: 13px;
      font-size: 14px;
      line-height: 1.55;
    }

    .msg-row.user .msg-bubble {
      background: #1e293b;
      border: 1px solid var(--border-strong);
      color: #f8fafc;
      border-bottom-right-radius: 4px;
    }

    .msg-row.assistant .msg-bubble {
      background: rgba(16, 185, 129, 0.14);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #ecfdf5;
      border-bottom-left-radius: 4px;
    }

    .msg-meta {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 4px;
      font-family: 'JetBrains Mono', monospace;
    }

    .slot-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 12px;
      background: #070b13;
      border: 1px solid var(--border);
      border-radius: 9px;
      font-size: 13px;
      margin-bottom: 8px;
      gap: 8px;
    }

    .slot-label {
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 700;
    }

    .slot-value {
      color: var(--text);
      font-weight: 700;
      text-align: left;
    }

    /* Classifier Studio */
    .clf-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 20px;
    }

    .metric-row {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-bottom: 14px;
    }

    .metric-box {
      background: #070b13;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      text-align: center;
    }

    .metric-val {
      font-size: 1.4rem;
      font-weight: 800;
      color: #34d399;
      font-family: 'JetBrains Mono', monospace;
    }

    .metric-lbl {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    /* Wilayas Grid */
    .wilaya-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 12px;
      margin-top: 14px;
    }

    .wilaya-card {
      background: #070b13;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
      transition: border-color 0.15s ease;
    }

    .wilaya-card:hover {
      border-color: var(--primary);
    }

    /* Footer */
    footer {
      text-align: center;
      margin-top: auto;
      padding: 26px 20px;
      color: var(--text-muted);
      font-size: 13px;
      border-top: 1px solid var(--border);
      background: var(--bg-elevated);
    }

    footer a {
      color: #34d399;
      text-decoration: none;
    }

    @media (max-width: 640px) {
      .topbar-inner { justify-content: center; }
      .results-grid { grid-template-columns: 1fr; }
      .metric-row { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>

  <!-- Top Navigation -->
  <nav class="topbar">
    <div class="topbar-inner">
      <a href="#top" class="brand" onclick="switchTab('analyzer'); return false;">
        <img src="logo.jpg?v=2" alt="darja-nlp-kit" class="brand-logo">
        <div>
          <div class="brand-title">
            <span dir="ltr">darja-nlp-kit</span>
            <span class="brand-pill" dir="ltr">v2.0</span>
          </div>
        </div>
      </a>

      <div class="nav-tabs" role="tablist">
        <button class="nav-tab active" data-tab="analyzer" onclick="switchTab('analyzer')">المحلل الموحد</button>
        <button class="nav-tab" data-tab="chat" onclick="switchTab('chat')">المحادثة الذكية</button>
        <button class="nav-tab" data-tab="classifier" onclick="switchTab('classifier')">استوديو المصنف</button>
        <button class="nav-tab" data-tab="explorer" onclick="switchTab('explorer')">الولايات والبيانات</button>
      </div>

      <div class="nav-links">
        <a href="https://github.com/test-bit-sys/darja-nlp-kit" target="_blank" rel="noopener" class="icon-link">GitHub</a>
        <a href="https://pypi.org/project/darja-nlp-kit/" target="_blank" rel="noopener" class="icon-link">PyPI</a>
        <a href="https://www.npmjs.com/package/@dz-open-suite/darja-nlp-kit" target="_blank" rel="noopener" class="icon-link">npm</a>
      </div>
    </div>
  </nav>

  <div class="container" id="top">
    <!-- Hero -->
    <header class="hero">
      <div class="hero-logo-wrap">
        <img src="logo.jpg?v=2" alt="darja-nlp-kit official logo" class="hero-logo">
      </div>
      <h1>بيئة التجربة التفاعلية للدارجة الجزائرية</h1>
      <p>
        تشغيل مباشر في المتصفح بدون خوادم: نفس خوارزميات <span dir="ltr" style="unicode-bidi:isolate;">Python &amp; TypeScript</span> لتحليل المشاعر (55K عينة)، استخراج الولايات الـ 69 والبلديات الـ 1,541، فهم الأسعار بالدارجة، الرد التلقائي، وتدريب المصنفات.
      </p>
      <div class="stats-strip">
        <span class="stat-pill"><strong>69</strong> ولاية و <strong>1,541</strong> بلدية</span>
        <span class="stat-pill"><strong>55,732</strong> عينة تدريب حقيقية</span>
        <span class="stat-pill"><strong>8,000</strong> ميزة ML مدمجة</span>
        <span class="stat-pill"><strong>599</strong> مرجع KB حواري</span>
        <span class="stat-pill"><strong>0</strong> اعتماديات خارجية</span>
      </div>
    </header>

    <!-- TAB 1: UNIFIED ANALYZER (DarjaPipeline) -->
    <section id="tab-analyzer" class="tab-panel active">
      <div class="card">
        <div class="card-header">
          <label for="textInput" style="font-weight:800; font-size:15px;">أدخل نصاً أو رسالة زبون جزائري (عربي / دارجة / أرابيزي / فرنسي):</label>
          <span class="mono" id="charCount" style="font-size:12px; color:var(--text-muted);">0 chars</span>
        </div>

        <textarea id="textInput" dir="auto" class="main-input" placeholder="اكتب جملة بالدارجة أو العربيزي لتحليلها فورياً...">hab nchri 2 hbat XL noir b 500 doro aflou yalidine baridimob 0661234567</textarea>

        <div class="samples-bar">
          <span style="font-size:12px; color:var(--text-muted); font-weight:700; margin-left:4px;">نماذج واقعية:</span>
          <button class="sample-chip highlight-emerald" onclick="loadSample(0)">طلب شراء + أفلو 59 + دورو</button>
          <button class="sample-chip" onclick="loadSample(1)">استفسار عن السعر والتوفر</button>
          <button class="sample-chip" onclick="loadSample(2)">تقييم إيجابي + العلمة + جيزي</button>
          <button class="sample-chip highlight-danger" onclick="loadSample(3)">تصعيد عاجل وشكوى</button>
          <button class="sample-chip" onclick="loadSample(4)">لهجة وهران + دوزينة + بونتير</button>
          <button class="sample-chip" onclick="loadSample(5)">أطباق وأمثال: رشتة وباب الواد</button>
          <button class="sample-chip" onclick="loadSample(6)">ميمز وفرانكو-دارجة: ncommandi caba</button>
          <button class="sample-chip highlight-emerald" onclick="loadSample(7)">تحية عفوية: wach ya khoy</button>
          <button class="sample-chip highlight-danger" onclick="loadSample(8)">اختبار درع الشتائم</button>
          <button class="sample-chip" onclick="loadSample(9)">ميمز جزائرية فيروسية</button>
          <button class="sample-chip" onclick="loadSample(10)">مفاوضة DziriAlign KB</button>
          <button class="sample-chip" onclick="loadSample(11)">إشادة 55K ML: Thbliiii bravo souade</button>
        </div>

        <div class="controls-row">
          <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span class="seg-label">وضع المشاعر:</span>
            <div class="seg-group" id="sentimentModeGroup">
              <button class="seg-btn active" data-mode="hybrid" onclick="setSentimentMode('hybrid')">هجين (Hybrid)</button>
              <button class="seg-btn" data-mode="ml" onclick="setSentimentMode('ml')">نموذج ML (55K)</button>
              <button class="seg-btn" data-mode="lexicon" onclick="setSentimentMode('lexicon')">القاموس فقط</button>
            </div>
          </div>

          <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span class="seg-label">شخصية الرد:</span>
            <div class="seg-group" id="personaGroup">
              <button class="seg-btn active" data-persona="merchant" onclick="setPersona('merchant')">تاجر (Merchant)</button>
              <button class="seg-btn" data-persona="casual" onclick="setPersona('casual')">ودي (Casual)</button>
              <button class="seg-btn" data-persona="assistant" onclick="setPersona('assistant')">مساعد رسمي (Assistant)</button>
            </div>
          </div>
        </div>
      </div>

      <div id="escalationStatusBox"></div>

      <div class="results-grid">
        <!-- 1. Intent -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
              تحليل نية الزبون (Intent Classification)
            </div>
            <span id="intentConfidence" style="font-size:12px; color:var(--text-muted); font-weight:700;">-</span>
          </div>
          <div style="margin-bottom:12px;">
            <div id="intentBadge" class="intent-badge intent-order">ORDER</div>
          </div>
          <div style="font-size:12px; color:var(--text-muted);">المفاتيح اللغوية المرصودة:</div>
          <div id="intentKeywords" class="pill-row"></div>
        </div>

        <!-- 2. Sentiment v2 -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              تحليل المشاعر الهجين (Sentiment v2)
            </div>
            <span id="sentimentMethodBadge" class="token-pill token-info">hybrid</span>
          </div>
          <div class="sentiment-banner">
            <div id="sentimentBadge" class="sentiment-badge badge-neutral">محايد</div>
            <div id="sentimentScore" class="mono" style="font-size:20px; font-weight:800;">0.00</div>
          </div>
          <div class="prob-bar-wrap">
            <div class="prob-bar-track">
              <div id="probBarPos" class="prob-seg-pos" style="width:33%;"></div>
              <div id="probBarNeu" class="prob-seg-neu" style="width:34%;"></div>
              <div id="probBarNeg" class="prob-seg-neg" style="width:33%;"></div>
            </div>
            <div class="prob-legend" id="probLegend" dir="ltr">POS 0% | NEU 100% | NEG 0%</div>
          </div>
          <div style="font-size:12px; color:var(--text-muted);">المؤثرات والكلمات المرصودة:</div>
          <div id="tokensBox" class="pill-row"></div>
          <div id="negationFlag" style="margin-top:10px; font-size:12px; color:var(--cyan); display:none;">
            تم رصد أسلوب نفي أو نفي مضاعف في العبارة
          </div>
        </div>

        <!-- 3. Wilayas & Communes -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              الولايات الـ 69 والبلديات (Algeria-Geo)
            </div>
          </div>
          <div id="wilayasBox"></div>
        </div>

        <!-- 4. Quantities & Attributes -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
              الكميات والمواصفات (Quantities & Attributes)
            </div>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:4px;">الكميات بالدارجة:</div>
            <div id="quantitiesBox"></div>
          </div>
          <div>
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:4px;">الألوان والمقاسات:</div>
            <div id="attributesBox"></div>
          </div>
        </div>

        <!-- 5. Payments & Prices -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="1" y="4" width="22" height="16" rx="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
              طرق الدفع والأسعار بالدينار (دورو / ملايين)
            </div>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:4px;">وسائل الدفع:</div>
            <div id="paymentsBox"></div>
          </div>
          <div>
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:4px;">المبالغ المحولة تلقائياً:</div>
            <div id="pricesBox"></div>
          </div>
        </div>

        <!-- 6. Deliveries & Telecom -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
              التوصيل، المتعاملين، وروابط واتساب
            </div>
          </div>
          <div style="margin-bottom:10px;">
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:4px;">شركة ونمط التوصيل:</div>
            <div id="deliveriesBox"></div>
          </div>
          <div>
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:4px;">أرقام الهاتف:</div>
            <div id="phonesBox"></div>
          </div>
        </div>

        <!-- 7. Dialect -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
              كشف اللهجة الجهوية (Regional Dialect)
            </div>
            <span id="dialectConfidence" style="font-size:12px; color:var(--text-muted); font-weight:700;">-</span>
          </div>
          <div style="margin-bottom:12px;">
            <span id="dialectBadge" class="intent-badge intent-price">GENERAL_DARJA</span>
          </div>
          <div style="font-size:12px; color:var(--text-muted);">المؤشرات اللغوية الدقيقة:</div>
          <div id="dialectMarkers" class="pill-row"></div>
        </div>

        <!-- 8. Culture, Memes & Franco-Darja -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
              الثقافة، الميمز، والفرانكو-دارجة
            </div>
          </div>
          <div id="culturalBox" style="display:flex; flex-direction:column; gap:7px;"></div>
        </div>

        <!-- 9. Arabizi + Moderation -->
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              التطبيع، العربيزي، ودرع الشتائم
            </div>
          </div>
          <div style="font-size:12px; color:var(--text-muted); margin-bottom:4px;">التحويل للعربية (Arabizi to Arabic):</div>
          <div id="arabiziBox" dir="auto" class="code-box"></div>
          <div style="font-size:12px; color:var(--text-muted); margin-bottom:4px;">حالة سلامة المحتوى والمراجعة:</div>
          <div id="profanityStatusBox" style="margin-bottom:8px;"></div>
          <div id="censoredTextBox" dir="auto" class="code-box" style="margin-bottom:0; color:#fda4af;"></div>
        </div>

        <!-- 10. Dialogue & KB Engine -->
        <div class="card full-span" style="border-color: rgba(16, 185, 129, 0.4); background: linear-gradient(135deg, rgba(6, 43, 31, 0.5), var(--card-bg));">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              محرك الردود بالدارجة + الاسترجاع من <span dir="ltr">DziriAlign</span> و<span dir="ltr">DziriEval</span>
            </div>
            <div style="display:flex; gap:6px; flex-wrap:wrap;">
              <span id="dialogueScriptBadge" class="token-pill token-pos">script</span>
              <span id="dialogueSourceBadge" class="token-pill token-info">source</span>
              <span id="dialogueIntentBadge" class="token-pill" style="background:#1e293b; color:#cbd5e1; border:1px solid #334155;">intent</span>
            </div>
          </div>
          <div id="dialogueReplyBox" dir="auto" style="background:#070b13; border:1px solid rgba(16,185,129,0.35); border-radius:12px; padding:14px 18px; font-size:16px; font-weight:700; color:#ecfdf5;"></div>
        </div>

        <!-- 11. Developer Output & AI Agent Grounding Drawer -->
        <div class="card full-span" style="border-color: rgba(59, 130, 246, 0.4);">
          <div class="card-header">
            <div class="section-title" style="color:#60a5fa;">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              مخرجات المطورين ومحاكاة وكيل الذكاء الاصطناعي
            </div>
            <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
              <div class="seg-group">
                <button class="seg-btn active" data-devtab="json" onclick="switchDevTab('json')">JSON Report</button>
                <button class="seg-btn" data-devtab="code" onclick="switchDevTab('code')">Python &amp; TS</button>
                <button class="seg-btn" data-devtab="agent" onclick="switchDevTab('agent')">LLM Prompt</button>
              </div>
              <button class="btn btn-secondary" onclick="copyDevOutput()" id="copyDevBtn" style="padding:5px 12px; font-size:12px;">نسخ</button>
            </div>
          </div>

          <div id="devTab-json">
            <pre id="jsonReportPre" class="pre-code"></pre>
          </div>
          <div id="devTab-code" style="display:none;">
            <pre id="codeSnippetPre" class="pre-code"></pre>
          </div>
          <div id="devTab-agent" style="display:none;">
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:14px;">
              <div>
                <div style="font-size:12px; color:#93c5fd; font-weight:700; margin-bottom:6px;">System Prompt المستخرج:</div>
                <pre id="agentPromptBox" class="pre-code" style="direction:rtl; text-align:right;"></pre>
              </div>
              <div>
                <div style="font-size:12px; color:#34d399; font-weight:700; margin-bottom:6px;">محاكاة الرد الذكي المحكوم بالحقائق:</div>
                <div id="agentReplyBox" dir="auto" style="background:#070b13; border:1px solid rgba(16,185,129,0.3); border-radius:10px; padding:14px; font-size:14px; color:#f0fdf4; min-height:110px; margin-bottom:10px;"></div>
                <div style="font-size:12px; color:#fbbf24; font-weight:700; margin-bottom:6px;">أقرب حوار تدريبي مطابق للهجة:</div>
                <div id="matchingDialogueBox" style="background:#070b13; border:1px solid rgba(245,158,11,0.28); border-radius:10px; padding:11px 14px; font-size:13px; color:#fef3c7;"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 2: MULTI-TURN CHAT (DarjaChat) -->
    <section id="tab-chat" class="tab-panel">
      <div class="card">
        <div class="card-header">
          <div class="section-title">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
            محاكي الجلسات الحوارية (<span dir="ltr">DarjaChat Multi-Turn Slot Filling</span>)
          </div>
          <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <button class="btn btn-primary" onclick="runChatAutoDemo()">تشغيل سيناريو طلبية كامل</button>
            <button class="btn btn-secondary" onclick="resetChatSession()">جلسة جديدة</button>
          </div>
        </div>
        <p style="font-size:13px; color:var(--text-muted); margin-bottom:14px;">
          أرسل عدة رسائل متتالية كما يفعل الزبون الحقيقي: الجلسة تحفظ اللغة واللهجة والولاية والكمية والهاتف عبر الأدوار وتطلب فقط المعلومات الناقصة حتى تأكيد الطلبية.
        </p>

        <div class="chat-layout">
          <div>
            <div id="chatMessages" class="chat-messages"></div>
            <div style="display:flex; gap:8px;">
              <input type="text" id="chatInput" dir="auto" placeholder="اكتب رسالة الزبون هنا واضغط Enter..." onkeydown="if(event.key==='Enter') sendChatTurn();">
              <button class="btn btn-primary" onclick="sendChatTurn()" style="white-space:nowrap;">إرسال</button>
            </div>
            <div class="samples-bar" style="margin-top:10px;">
              <span style="font-size:12px; color:var(--text-muted);">رسائل جاهزة:</span>
              <button class="sample-chip" dir="ltr" onclick="sendQuickChat('wach ya khoy')">wach ya khoy</button>
              <button class="sample-chip" dir="ltr" onclick="sendQuickChat('hab nchri 2 hbat noir XL')">hab nchri 2 hbat noir XL</button>
              <button class="sample-chip" dir="ltr" onclick="sendQuickChat('l aflou b yalidine')">l aflou b yalidine</button>
              <button class="sample-chip" dir="ltr" onclick="sendQuickChat('0661234567 baridimob')">0661234567 baridimob</button>
              <button class="sample-chip highlight-danger" onclick="sendQuickChat('سراقين حشيتوهالي')">سراقين حشيتوهالي</button>
            </div>
          </div>

          <div style="background:#090e1a; border:1px solid var(--border); border-radius:14px; padding:16px;">
            <div class="card-header" style="margin-bottom:10px;">
              <span style="font-weight:800; font-size:14px; color:#34d399;">حالة الطلبية والبيانات المستخرجة</span>
              <span id="chatReadyBadge" class="token-pill token-info">جاري التجميع</span>
            </div>
            <div id="chatSlotsPanel"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 3: IN-BROWSER CLASSIFIER STUDIO (DarjaClassifier) -->
    <section id="tab-classifier" class="tab-panel">
      <div class="clf-grid">
        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
              بيانات التدريب (صيغة: النص | التصنيف)
            </div>
            <div style="display:flex; gap:6px; flex-wrap:wrap;">
              <button class="btn btn-secondary" style="padding:5px 10px; font-size:12px;" onclick="loadClfPreset('commerce')">بيانات متجر</button>
              <button class="btn btn-secondary" style="padding:5px 10px; font-size:12px;" onclick="loadClfPreset('dialect')">لهجات جهوية</button>
            </div>
          </div>
          <textarea id="clfTrainData" style="height:260px; font-family:'Cairo', monospace; font-size:13px; line-height:1.7;"></textarea>
          <div style="display:flex; gap:10px; margin-top:12px; flex-wrap:wrap;">
            <button class="btn btn-primary" onclick="trainBrowserClassifier()">تدريب وتقييم النموذج الآن</button>
            <button class="btn btn-secondary" onclick="downloadClassifierModel()">تنزيل النموذج (JSON لـ Python وJS)</button>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="section-title">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
              تقييم الأداء والاختبار الحي (DarjaClassifier)
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-box">
              <div id="clfAccVal" class="metric-val">-</div>
              <div class="metric-lbl">الدقة (Accuracy)</div>
            </div>
            <div class="metric-box">
              <div id="clfF1Val" class="metric-val">-</div>
              <div class="metric-lbl">Macro-F1</div>
            </div>
            <div class="metric-box">
              <div id="clfVocabVal" class="metric-val">-</div>
              <div class="metric-lbl">حجم المفردات (N-grams)</div>
            </div>
          </div>

          <label for="clfTestInput" style="font-size:13px; font-weight:700; display:block; margin-bottom:6px;">اختبر النموذج المدرب بأي جملة بالدارجة:</label>
          <input type="text" id="clfTestInput" value="شحال السومة تاع السبردينة لسطيف؟" oninput="predictWithBrowserClf()">

          <div id="clfPredBox" style="margin-top:14px; background:#070b13; border:1px solid var(--border); border-radius:12px; padding:14px;"></div>
          <p style="font-size:12px; color:var(--text-muted); margin-top:12px;">
            ملف JSON المصدر متوافق 100% مع <code>DarjaClassifier.load("classifier_model.json")</code> في Python وTypeScript.
          </p>
        </div>
      </div>
    </section>

    <!-- TAB 4: 69 WILAYAS EXPLORER & BENCHMARKS -->
    <section id="tab-explorer" class="tab-panel">
      <div class="card">
        <div class="card-header">
          <div class="section-title">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            النتائج القياسية الفعلية على معيار 600 عينة جزائرية (eval_benchmark.json)
          </div>
        </div>
        <div class="metric-row" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));">
          <div class="metric-box">
            <div class="metric-val">70.83%</div>
            <div class="metric-lbl">وضع ML الخالص (425/600)</div>
          </div>
          <div class="metric-box">
            <div class="metric-val">68.00%</div>
            <div class="metric-lbl">الوضع الهجين Hybrid (408/600)</div>
          </div>
          <div class="metric-box">
            <div class="metric-val">85.56%</div>
            <div class="metric-lbl">دقة ML على Algerian_sentiment</div>
          </div>
          <div class="metric-box">
            <div class="metric-val">8,628 + 1,000</div>
            <div class="metric-lbl">عينات SFT + أزواج DPO حقيقية</div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:12px;">
          <pre class="pre-code" style="max-height:110px;"># Python
pip install darja-nlp-kit
darja-nlp analyze "salam kho hab nchri 2 hbat..."
darja-nlp eval --mode ml</pre>
          <pre class="pre-code" style="max-height:110px;"># Node.js / TypeScript
npm install @dz-open-suite/darja-nlp-kit
npx darja-nlp eval --mode hybrid
npx darja-nlp server --port 8080</pre>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="section-title">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            مستكشف الولايات الـ 69 والبلديات (متزامن مع algeria-geo)
          </div>
          <div class="seg-group">
            <button class="seg-btn active" data-wfilter="all" onclick="setWilayaFilter('all')">جميع الولايات (69)</button>
            <button class="seg-btn" data-wfilter="era69" onclick="setWilayaFilter('era69')">الولايات الجديدة (59–69)</button>
          </div>
        </div>
        <input type="text" id="wilayaSearchInput" placeholder="ابحث بالاسم بالعربية أو الفرنسية أو الرمز أو البلدية (مثال: أفلو، وهران، 31، العلمة)..." oninput="renderWilayasExplorer()">
        <div id="wilayaCountInfo" style="font-size:12px; color:var(--text-muted); margin-top:8px;"></div>
        <div id="wilayaExplorerGrid" class="wilaya-grid"></div>
      </div>
    </section>
  </div>

  <footer>
    <p dir="ltr"><strong>darja-nlp-kit</strong> — Zero-Dependency Algerian Darja NLP Toolkit (Python &amp; TypeScript). Open Source under MIT License.</p>
    <p style="margin-top:6px;">
      <a href="https://github.com/test-bit-sys/darja-nlp-kit" target="_blank" rel="noopener">GitHub Repository</a>
      &middot;
      <a href="https://github.com/test-bit-sys/algeria-geo" target="_blank" rel="noopener">Algeria-Geo 69 Wilayas</a>
    </p>
  </footer>

  <script>
    // Embedded Linguistic Datasets & Trained Models
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
    const SENTIMENT_MODEL = __SENTIMENT_MODEL__;
    const DIALOGUE_KB_DATA = __DIALOGUE_KB_DATA__;

    // UI State
    let sentimentMode = 'hybrid';
    let currentPersona = 'merchant';
    let currentDevTab = 'json';
    let currentWilayaFilter = 'all';
    let lastAnalyzeReport = null;

    function escapeHtml(str) {
      return String(str ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    // Core Tokenizer (exact parity with TS & Python)
    function tokenize(text) {
      if (!text) return { tokens: [], hasCircumfixNegation: false };
      const arabicNegRe = /ما[^\s]+ش(?=\s|$|[.,!?;:])/g;
      const arabiziNegRe = /\bma[a-zA-Z0-9']+ch\b/gi;
      const hasCircumfixNegation = arabicNegRe.test(text) || arabiziNegRe.test(text);
      const clean = text.replace(/[.,!?;:()\[\]{}"'«»؟،؛]/g, ' ');
      const tokens = clean.split(/\s+/).filter(Boolean);
      return { tokens, hasCircumfixNegation };
    }

    // Normalizer
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
      return text.replace(ALEF_VARIANTS, '\u0627')
                 .replace(TA_MARBUTA, '\u0647')
                 .replace(ALEF_MAQSURA, '\u064A')
                 .replace(TASHKEEL, '')
                 .replace(TATWEEL, '')
                 .replace(ARABIC_ELONGATION, '$1')
                 .replace(LATIN_ELONGATION, (m, c) => VALID_DOUBLES.has(c.toLowerCase()+c.toLowerCase()) ? c+c : c)
                 .replace(MULTI_SPACE, ' ')
                 .replace(MULTI_PUNCT, '$1')
                 .trim();
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
        for (const [k, v] of Object.entries(ARABIZI_RULES.digraphs)) res = res.replaceAll(k, v);
        for (const [k, v] of Object.entries(ARABIZI_RULES.numbers)) res = res.replaceAll(k, v);
        for (const [k, v] of Object.entries(ARABIZI_RULES.singles)) res = res.replaceAll(k, v);
        return res;
      }).join('');
    }

    // 55K ML Sentiment Predictor
    function predictMlSentiment(text) {
      if (!SENTIMENT_MODEL || !SENTIMENT_MODEL.priors || !SENTIMENT_MODEL.weights) return null;
      let t = text.toLowerCase().replace(/https?:\/\/\S+|@\w+/g, ' ')
                  .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
                  .replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
                  .replace(/(.)\1{2,}/g, '$1$1');
      const toks = t.match(/[a-zA-Z0-9\u0621-\u064A\u0671-\u06D3]+|[\u{1F300}-\u{1FAFF}\u2600-\u27BF]+/gu) || [];
      if (toks.length === 0) return null;
      const feats = [...toks];
      for (let i = 0; i < toks.length - 1; i++) feats.push(toks[i] + '_' + toks[i + 1]);
      for (const w of toks) {
        if (w.length >= 5 && /^[a-zA-Z\u0621-\u064A\u0671-\u06D3]+$/.test(w)) {
          feats.push('p3:' + w.slice(0, 3));
          feats.push('s3:' + w.slice(-3));
        }
      }
      const scores = [...SENTIMENT_MODEL.priors];
      const mPos = [], mNeg = [];
      let hits = 0;
      for (const f of feats) {
        const wt = SENTIMENT_MODEL.weights[f];
        if (wt) {
          hits++;
          scores[0] += wt[0]; scores[1] += wt[1]; scores[2] += wt[2];
          if (!f.includes('_') && !f.startsWith('p3:') && !f.startsWith('s3:')) {
            if (wt[2] - wt[0] > 0.4 && !mPos.includes(f)) mPos.push(f);
            else if (wt[0] - wt[2] > 0.4 && !mNeg.includes(f)) mNeg.push(f);
          }
        }
      }
      if (hits === 0) return null;
      const maxS = Math.max(...scores);
      const exps = scores.map(s => Math.exp(Math.max(-50, s - maxS)));
      const sumE = exps.reduce((a, b) => a + b, 0) || 1;
      const probs = exps.map(e => e / sumE);
      let label = 'NEUTRAL';
      if (probs[2] >= probs[0] && probs[2] >= probs[1]) label = 'POSITIVE';
      else if (probs[0] >= probs[2] && probs[0] >= probs[1]) label = 'NEGATIVE';
      const pol = Math.round(Math.max(-1, Math.min(1, probs[2] - probs[0])) * 100) / 100;
      return {
        score: pol,
        label,
        positiveTokens: mPos.slice(0, 6),
        negativeTokens: mNeg.slice(0, 6),
        negated: false,
        method: 'ml',
        probabilities: {
          NEGATIVE: Math.round(probs[0] * 1000) / 1000,
          NEUTRAL: Math.round(probs[1] * 1000) / 1000,
          POSITIVE: Math.round(probs[2] * 1000) / 1000,
        }
      };
    }

    function analyzeSentiment(text, mode = 'hybrid') {
      if (!text || !text.trim()) {
        return { score: 0, label: 'NEUTRAL', positiveTokens: [], negativeTokens: [], negated: false, method: mode, probabilities: { NEGATIVE: 0, NEUTRAL: 1, POSITIVE: 0 } };
      }
      if (mode === 'ml') {
        const mlOnly = predictMlSentiment(text);
        if (mlOnly) return mlOnly;
      }

      const clean = normalize(text);
      const words = clean.split(/[\s,،!?;:.]+/).filter(Boolean);
      const lowerWords = words.map(w => w.toLowerCase());
      const negatorSet = new Set((LEXICON_DATA.negators || []).map(n => normalize(n).toLowerCase()));
      let total = 0, count = 0, hasNeg = false;
      const pos = [], neg = [];
      const covered = new Set();

      for (const win of [4, 3, 2]) {
        for (let i = 0; i <= lowerWords.length - win; i++) {
          let skip = false;
          for (let k = i; k < i + win; k++) if (covered.has(k)) { skip = true; break; }
          if (skip) continue;
          const phrase = lowerWords.slice(i, i + win).join(' ');
          let pScore = null;
          if (LEXICON_DATA.positive[phrase] !== undefined) pScore = LEXICON_DATA.positive[phrase];
          else if (LEXICON_DATA.negative[phrase] !== undefined) pScore = LEXICON_DATA.negative[phrase];
          if (pScore !== null) {
            const origPhrase = words.slice(i, i + win).join(' ');
            const prev = i > 0 ? lowerWords[i - 1] : null;
            if (prev && negatorSet.has(prev)) { pScore = -pScore * 0.8; hasNeg = true; }
            total += pScore; count++;
            if (pScore > 0) pos.push(origPhrase); else if (pScore < 0) neg.push(origPhrase);
            for (let k = i; k < i + win; k++) covered.add(k);
          }
        }
      }

      for (let i = 0; i < words.length; i++) {
        if (covered.has(i)) continue;
        const w = lowerWords[i];
        let score = null;
        if (LEXICON_DATA.positive[w] !== undefined) score = LEXICON_DATA.positive[w];
        else if (LEXICON_DATA.negative[w] !== undefined) score = LEXICON_DATA.negative[w];
        if (score === null) continue;

        const prev = i > 0 ? lowerWords[i - 1] : null;
        if (prev && negatorSet.has(prev)) {
          score = -score * 0.8;
          hasNeg = true;
        }
        if (prev && LEXICON_DATA.intensifiers[prev] && !negatorSet.has(prev)) {
          score *= LEXICON_DATA.intensifiers[prev];
        }
        total += score; count++;
        if (score > 0) pos.push(words[i]); else if (score < 0) neg.push(words[i]);
      }

      if (mode === 'hybrid' && count === 0) {
        const mlRes = predictMlSentiment(text);
        if (mlRes && mlRes.label !== 'NEUTRAL' && Math.abs(mlRes.score) >= 0.15) return mlRes;
      }

      const finalScore = count > 0 ? Math.max(-1, Math.min(1, total / count)) : 0;
      const rounded = Math.round(finalScore * 100) / 100;
      let label = 'NEUTRAL';
      if (pos.length > 0 && neg.length > 0) label = 'MIXED';
      else if (rounded > 0.05) label = 'POSITIVE';
      else if (rounded < -0.05) label = 'NEGATIVE';

      const mlBg = mode !== 'lexicon' ? predictMlSentiment(text) : null;
      const probs = mlBg ? mlBg.probabilities : (
        label === 'POSITIVE' ? { NEGATIVE: 0.05, NEUTRAL: 0.1, POSITIVE: 0.85 } :
        label === 'NEGATIVE' ? { NEGATIVE: 0.85, NEUTRAL: 0.1, POSITIVE: 0.05 } :
        { NEGATIVE: 0.05, NEUTRAL: 0.9, POSITIVE: 0.05 }
      );

      return { score: rounded, label, positiveTokens: pos, negativeTokens: neg, negated: hasNeg, method: mode, probabilities: probs };
    }

    function identifyIntent(text) {
      if (!text) return { intent: 'UNKNOWN', confidence: 0, matchedKeywords: [] };
      const lower = text.toLowerCase();
      const rules = [
        { intent: 'COMPLAINT', keywords: ['مكسرة', 'مكسر', 'ما وصلتش', 'ما لحقتش', 'روطار', 'سلعة عيانة', 'سلعة ميتة', 'حشيتوهالي', 'حشاوها لي', 'بدلوهالي', 'روتور', 'رجعولي دراهمي', 'ما رديتوش', 'حقار', 'سراقين', 'سرقة', 'فضيحة', 'سلعة مفاتشة', 'ناقصة', 'معطوبة', 'reclamation', 'retour', 'casse', 'mfetcha', 'retard', 'ma wesletch', '7chawhali', 'arnaque', 'ser9a', 'khorda'] },
        { intent: 'ORDER', keywords: ['كوموندي', 'نكوموندي', 'كومونديلي', 'باغي نشري', 'راني باغي', 'باغي', 'حاب نشري', 'حبيت نشري', 'راني حاب', 'حاب', 'حبيت', 'ابعثلي', 'ابعثهالي', 'احجزلي', 'احجز', 'نشريها', 'نشري', 'commander', 'ncommander', 'ncommandi', 'baghi nchri', 'rani baghi', 'baghi', 'hab nchri', '7ab nchri', 'rani hab', 'hab', '7ab', 'nchri', 'ab3atli', 'livrili', '7jezli', 'reserver'] },
        { intent: 'DELIVERY_INQUIRY', keywords: ['التوصيل', 'توصيل', 'شحال التوصيل', 'شحال لا ليفريزون', 'كاين توصيل', 'توصلو', 'وقتاش تلحق', 'وقتاش يوصل', 'livraison', 'frais de livraison', 'delai', 'touslou', 'chal livraison'] },
        { intent: 'PRICE_INQUIRY', keywords: ['السعر', 'السومة', 'بشحال', 'شحال', 'شحال يدير', 'بقداش', 'قداش', 'شحال السومة', 'سومة', 'prix', 'bchhal', 'chhal', 'ch7al', 'kadech', '9dach', 'combien'] },
        { intent: 'AVAILABILITY_INQUIRY', keywords: ['متوفر', 'متوفرة', 'كاين منها', 'مازال كاين', 'كاين ستوك', 'خلاصت', 'dispo', 'disponible', 'kayen', 'mazal'] },
        { intent: 'GREETING', keywords: ['سلام', 'السلام عليكم', 'صباح الخير', 'مساء الخير', 'صحا', 'صحيت', 'واش راك', 'salam', 'slm', 'bonjour', 'bonsoir', 'salut', 'wach'] }
      ];
      for (const rule of rules) {
        const matched = rule.keywords.filter(k => lower.includes(k.toLowerCase()));
        if (matched.length > 0) {
          return { intent: rule.intent, confidence: Math.min(0.99, Math.round((0.70 + matched.length * 0.1) * 100) / 100), matchedKeywords: matched };
        }
      }
      return { intent: 'UNKNOWN', confidence: 0, matchedKeywords: [] };
    }

    function detectEscalation(text) {
      if (!text) return { needsEscalation: false, urgency: 'NONE', reason: null, matchedTriggers: [], guideline: '' };
      const lower = text.toLowerCase();
      const legals = ['نشكي بيكم', 'لابوليس', 'حماية المستهلك', 'العدالة', 'نديرلكم شكوى', 'محكمة', 'la police', 'protection du consommateur', 'plainte', 'tribunal'];
      const mLegal = legals.filter(t => lower.includes(t.toLowerCase()));
      if (mLegal.length > 0) return { needsEscalation: true, urgency: 'CRITICAL', reason: 'LEGAL_THREAT', matchedTriggers: mLegal, guideline: 'الزبون يلوّح بمتابعة قانونية أو شكوى رسمية، حوّل المحادثة فوراً للمسؤول.' };

      const angry = ['حشيتوهالي', 'حشاوها لي', 'سراقين', 'سرقة عيني عينك', 'فضيحة', 'رجعولي دراهمي', 'وكيلكم ربي', 'حقارين', 'بهدلتو بينا', 'خردة', '7chawhali', 'ser9a', 'arnaqueurs', 'voleurs'];
      const mAngry = angry.filter(t => lower.includes(t.toLowerCase()));
      if (mAngry.length > 0) return { needsEscalation: true, urgency: 'HIGH', reason: 'ANGRY_CUSTOMER', matchedTriggers: mAngry, guideline: 'الزبون غاضب جداً ويشتكي من الغش أو الرداءة، تدخل عون بشري مطلوب فوراً.' };

      const human = ['احكي مع بنادم', 'مع انسان', 'مع بنادم', 'عطيني المدير', 'خدمة الزبائن', 'عيطلي', 'كلمني', 'appel moi', 'appelez moi', 'service client', 'humain'];
      const mHuman = human.filter(t => lower.includes(t.toLowerCase()));
      if (mHuman.length > 0) return { needsEscalation: true, urgency: 'HIGH', reason: 'HUMAN_REQUESTED', matchedTriggers: mHuman, guideline: 'الزبون طلب التحدث مع شخص حقيقي من خدمة الزبائن.' };

      return { needsEscalation: false, urgency: 'NONE', reason: null, matchedTriggers: [], guideline: '' };
    }

    function extractQuantities(text) {
      const results = [];
      const unitWords = { 'زوج': 2, 'تلات': 3, 'تلاتة': 3, 'ربع': 4, 'ربعة': 4, 'خمس': 5, 'خمسة': 5, 'zouj': 2, 'tlata': 3 };
      const dynReg = /(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:\.\d+)?|زوج|تلات|تلاتة|ربع|ربعة|خمس|خمسة|zouj|tlata)\s*(حبات|حبة|حبه|شكاير|شكارة|باكيات|باكية|كراتن|كراطن|كرطونة|hbat|7bat|chkayer|bakyat|boites|cartons)(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let m, masked = text;
      while ((m = dynReg.exec(text)) !== null) {
        const rawNum = m[1].toLowerCase(), rawUnit = m[2].toLowerCase();
        const val = unitWords[rawNum] !== undefined ? unitWords[rawNum] : (parseFloat(rawNum) || 1);
        let uNorm = rawUnit;
        if (['حبات', 'hbat', '7bat'].includes(rawUnit)) uNorm = 'حبة';
        else if (['شكاير', 'chkayer'].includes(rawUnit)) uNorm = 'شكارة';
        else if (['باكيات', 'bakyat', 'boites'].includes(rawUnit)) uNorm = 'باكية';
        else if (['كراتن', 'كراطن', 'cartons'].includes(rawUnit)) uNorm = 'كرطونة';
        results.push({ raw: m[0].trim(), value: val, unit: uNorm });
        masked = masked.slice(0, m.index) + ' '.repeat(m[0].length) + masked.slice(m.index + m[0].length);
      }
      const douz = masked.match(/(?:^|\s|[^\w\u0600-\u06FF])(دوزينة|دزينة|douzina|douzaine)(?=$|\s|[^\w\u0600-\u06FF])/i);
      if (douz) results.push({ raw: douz[0].trim(), value: 12, unit: 'دوزينة' });
      return results;
    }

    function extractProductAttributes(text) {
      const colors = [];
      const colorDefs = [
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(كحل|كحلة|noir|noire|k7al|k7la)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'كحل / noir' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بيض|بيضا|blanc|blanche|byad)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بيض / blanc' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(غوج|حمرا|rouge|7mar)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'غوج / rouge' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بلو|زرقة|bleu|bleue)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بلو / bleu' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(خضر|خضرا|vert|verte)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'خضر / vert' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(بيج|beige)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'بيج / beige' },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF]|و)(مارون|قهوي|marron)(?=$|\s|[^\w\u0600-\u06FF])/i, label: 'مارون / marron' },
      ];
      for (const c of colorDefs) if (c.reg.test(text) && !colors.includes(c.label)) colors.push(c.label);

      const sizes = [];
      const explicitSizeReg = /(?:taille|size|مقاس|طاي|لاطاي)\s*[:=]?\s*(xxxl|3xl|xxl|2xl|xl|xs|l|m|s)\b/gi;
      let esm;
      while ((esm = explicitSizeReg.exec(text)) !== null) {
        const sv = esm[1].toUpperCase();
        if (!sizes.includes(sv)) sizes.push(sv);
      }
      const multiCharSizes = /\b(xxxl|3xl|xxl|2xl|xl|xs)\b/gi;
      let mcs;
      while ((mcs = multiCharSizes.exec(text)) !== null) {
        const sv = mcs[1].toUpperCase();
        if (!sizes.includes(sv)) sizes.push(sv);
      }
      const shoeReg = /(?:pointure|taille|مقاس|بونتير|نمرة)\s*[:=]?\s*([3-4][0-9])\b/gi;
      let shm;
      while ((shm = shoeReg.exec(text)) !== null) {
        const num = parseInt(shm[1], 10);
        if (num >= 35 && num <= 48 && !sizes.includes(shm[1])) sizes.push(shm[1]);
      }
      return { colors, sizes };
    }

    function escapeRx(s) {
      return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    function extractEntities(text) {
      const wilayas = [];
      const lower = text.toLowerCase();
      const addedCodes = new Set();

      const codeRegex = /\b(?:wilaya|w|ولاية|ولايه|l)\s*([0-6]?[0-9])\b/gi;
      let cm;
      while ((cm = codeRegex.exec(text)) !== null) {
        const num = parseInt(cm[1], 10);
        if (num >= 1 && num <= 69 && !addedCodes.has(num)) {
          const w = WILAYAS_DATA.find(item => item.code === num);
          if (w) { addedCodes.add(num); wilayas.push({ ...w, matched: cm[0], commune: null }); }
        }
      }

      for (const w of WILAYAS_DATA) {
        if (addedCodes.has(w.code)) continue;
        const cands = [w.name_ar, w.name_fr, w.name_en, ...(w.aliases || [])];
        for (const alias of cands) {
          if (!alias || alias.length < 3) continue;
          const alLow = alias.toLowerCase();
          if (!lower.includes(alLow)) continue;
          const bRe = new RegExp(`(?:^|\\s|[^\\w\\u0600-\\u06FF])${escapeRx(alLow)}(?=$|\\s|[^\\w\\u0600-\\u06FF])`, 'i');
          if (bRe.test(lower)) {
            addedCodes.add(w.code);
            wilayas.push({ ...w, matched: alias, commune: null });
            break;
          }
        }
      }

      for (const w of WILAYAS_DATA) {
        if (addedCodes.has(w.code)) continue;
        const allComs = (w.communes_sample || []).concat(w.communes_fr_sample || []);
        for (const com of allComs) {
          if (!com || com.length < 3) continue;
          const comLow = com.toLowerCase();
          if (!lower.includes(comLow)) continue;
          const bRe = new RegExp(`(?:^|\\s|[^\\w\\u0600-\\u06FF])${escapeRx(comLow)}(?=$|\\s|[^\\w\\u0600-\\u06FF])`, 'i');
          if (bRe.test(lower)) {
            addedCodes.add(w.code);
            wilayas.push({ ...w, matched: com, commune: com });
            break;
          }
        }
      }

      const payments = [];
      const payPatterns = [
        { type: 'BARIDIMOB', label: 'BaridiMob (بريدي موب)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(baridimob|baridi\s*mob|بريدي\s*موب|بريديموب)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { type: 'EDAHABIA', label: 'Carte Edahabia (البطاقة الذهبية)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(edahabia|dahabia|الذهبية|البطاقة\s*الذهبية)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { type: 'CCP', label: 'CCP (الحساب البريدي الجاري)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(ccp|سي\s*سي\s*بي)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { type: 'COD', label: 'Paiement à la livraison (الدفع عند الاستلام)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(cod|كاش|الدفع\s*عند\s*الاستلام|كي\s*يوصلني|كي\s*تلحق|main\s*à\s*main)(?=$|\s|[^\w\u0600-\u06FF])/i },
      ];
      for (const p of payPatterns) if (p.reg.test(text)) payments.push({ type: p.type, label: p.label });

      const prices = [];
      let maskedText = text;
      const millionsMap = { 'زوج': 2, 'تلات': 3, 'تلاتة': 3, 'ربع': 4, 'ربعة': 4, 'خمس': 5, 'خمسة': 5, 'عشر': 10, 'عشرة': 10, 'zouj': 2, 'tlata': 3 };
      const thousandsMap = { 'مية': 100, 'ميتين': 200, 'تلمية': 300, 'ربعمية': 400, 'خمسمية': 500, 'ستين': 60, 'سبعين': 70, 'mya': 100, 'mitin': 200, 'khamsmya': 500 };
      const mStr = 'زوج|تلات|تلاتة|ربع|ربعة|خمس|خمسة|ست|ستة|سبع|سبعة|عشر|عشرة|zouj|zoudj|tlata|khamsa|3achra';
      const kStr = 'مية|ميتين|تلمية|ربعمية|خمسمية|mya|mitin|khamsmya|khamsin';

      const compReg = new RegExp(`(?:^|\\s|[^\\w\\u0600-\\u06FF])(\\d+(?:[.,]\\d+)?|${mStr})?\\s*(?:ملاين|ملايين|مليون|mlyon|melyon|melyoun|mlayen|mlayin)\\s*(?:و|\\+|et|w)\\s*(\\d+(?:[.,]\\d+)?|${kStr})?\\s*(?:الف|ألف|alf)(?=$|\\s|[^\\w\\u0600-\\u06FF])`, 'gi');
      let compM;
      while ((compM = compReg.exec(text)) !== null) {
        let mVal = 1, kVal = 0;
        if (compM[1]) { const k = compM[1].toLowerCase(); mVal = millionsMap[k] ?? (parseFloat(k.replace(',', '.')) || 1); }
        if (compM[2]) { const k = compM[2].toLowerCase(); kVal = thousandsMap[k] ?? (parseFloat(k.replace(',', '.')) || 0); }
        prices.push({ raw: compM[0].trim(), amount: (mVal * 10000) + (kVal * 10) });
        maskedText = maskedText.slice(0, compM.index) + ' '.repeat(compM[0].length) + maskedText.slice(compM.index + compM[0].length);
      }

      const priceNumReg = /(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(da|dzd|دج|دينار|الف|ألف|alf)(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let pm;
      while ((pm = priceNumReg.exec(maskedText)) !== null) {
        let val = parseFloat(pm[1].replace(',', '.'));
        if (['الف', 'ألف', 'alf'].includes(pm[2].toLowerCase())) val *= 1000;
        prices.push({ raw: pm[0].trim(), amount: val });
        maskedText = maskedText.slice(0, pm.index) + ' '.repeat(pm[0].length) + maskedText.slice(pm.index + pm[0].length);
      }

      const doroNumReg = /(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(?:دورو|doro|doros)(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let dmDoro;
      while ((dmDoro = doroNumReg.exec(maskedText)) !== null) {
        prices.push({ raw: dmDoro[0].trim(), amount: parseFloat(dmDoro[1].replace(',', '.')) * 5 });
        maskedText = maskedText.slice(0, dmDoro.index) + ' '.repeat(dmDoro[0].length) + maskedText.slice(dmDoro.index + dmDoro[0].length);
      }

      const dynMilReg = /(?:^|\s|[^\w\u0600-\u06FF])(\d+(?:[.,]\d+)?)\s*(?:ملاين|ملايين|مليون|mlyon|melyon|melyoun|mlayen|mlayin|mlayoun)(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let dmDyn;
      while ((dmDyn = dynMilReg.exec(maskedText)) !== null) {
        prices.push({ raw: dmDyn[0].trim(), amount: parseFloat(dmDyn[1].replace(',', '.')) * 10000 });
        maskedText = maskedText.slice(0, dmDyn.index) + ' '.repeat(dmDyn[0].length) + maskedText.slice(dmDyn.index + dmDyn[0].length);
      }

      const darjaAmounts = [
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(عشرين\s*دورو|20\s*doro)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 100 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(مية\s*دورو|100\s*doro)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 500 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(مية\s*الف|100\s*الف|myat\s*alf)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 1000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(ميتين\s*الف|200\s*الف|mitin\s*alf)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 2000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(خمسمية\s*الف|500\s*الف)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 5000 },
        { reg: /(?:^|\s|[^\w\u0600-\u06FF])(زوج\s*ملاين|زوج\s*ملايين|zoudj\s*mlayen|zouj\s*mlayen)(?=$|\s|[^\w\u0600-\u06FF])/i, val: 20000 },
      ];
      for (const item of darjaAmounts) {
        const dm = maskedText.match(item.reg);
        if (dm) { prices.push({ raw: dm[0].trim(), amount: item.val }); }
      }

      const deliveries = [];
      const deliveryPatterns = [
        { company: 'YALIDINE', label: 'Yalidine Express (ياليدين)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(yalidine|yalidin|ياليدين)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'ZR_EXPRESS', label: 'ZR Express (زد ار اكسبرس)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(zr\s*express|zr|زد\s*ار\s*اكسبرس|زد\s*ار)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'MAYSTRO', label: 'Maystro Delivery (مايسترو)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(maystro\s*delivery|maystro|مايسترو)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'PROCOLIS', label: 'Procolis (بروكولي)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(procolis|pro\s*colis|بروكولي)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'EMS', label: 'EMS Algérie Poste (البريد السريع)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(ems|ems\s*algerie|البريد\s*السريع)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'KAZITOUR', label: 'Kazitour Express (كازيتور)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(kazitour|kazi\s*tour|كازيتور)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { company: 'GUEPEX', label: 'Guepex Express (قيباكس)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(guepex|قيباكس)(?=$|\s|[^\w\u0600-\u06FF])/i },
      ];
      for (const d of deliveryPatterns) {
        const m = text.match(d.reg);
        if (m) deliveries.push({ company: d.company, label: d.label, matched: m[0].trim() });
      }

      let deliveryMode = null;
      const modePatterns = [
        { mode: 'STOP_DESK', label: 'Stop Desk (استلام من المكتب)', reg: /(?:^|\s|[^\w\u0600-\u06FF])(stop\s*desk|stopdesk|ستوب\s*ديسك|المكتب|فالبيرو|في\s*البيرو|agence)(?=$|\s|[^\w\u0600-\u06FF])/i },
        { mode: 'HOME_DELIVERY', label: 'Home Delivery (توصيل للمنزل)', reg: /(?:^|\s|[^\w\u0600-\u06FF])([aà]\s*domicile|للدار|لباب\s*الدار|توصيل\s*للمنزل|توصيل\s*للدار|فالدار)(?=$|\s|[^\w\u0600-\u06FF])/i },
      ];
      for (const dm of modePatterns) {
        if (dm.reg.test(text)) { deliveryMode = dm.label; break; }
      }

      const phones = [];
      const phoneReg = /(?:^|\s|[^\w\u0600-\u06FF])((?:\+213|00213|0)\s*(?:[5-7](?:[\s.-]?\d){8}|(?:2[0-9]|3[0-9]|4[0-9])(?:[\s.-]?\d){6}))(?=$|\s|[^\w\u0600-\u06FF])/gi;
      let phMatch;
      while ((phMatch = phoneReg.exec(text)) !== null) {
        const raw = phMatch[1].trim();
        let norm = raw.replace(/[\s.-]/g, '');
        if (norm.startsWith('00213')) norm = '0' + norm.slice(5);
        else if (norm.startsWith('+213')) norm = '0' + norm.slice(4);
        let op = null, opLabel = null, opClass = '';
        const pref = norm.slice(0, 2);
        if (pref === '06') { op = 'MOBILIS'; opLabel = 'Mobilis'; opClass = 'op-mobilis'; }
        else if (pref === '07') { op = 'DJEZZY'; opLabel = 'Djezzy'; opClass = 'op-djezzy'; }
        else if (pref === '05') { op = 'OOREDOO'; opLabel = 'Ooredoo'; opClass = 'op-ooredoo'; }
        else if (['02', '03', '04'].includes(pref)) { op = 'ALGERIE_TELECOM'; opLabel = 'Fixe'; opClass = 'op-landline'; }
        const waUrl = (norm.length === 10 && ['05', '06', '07'].includes(pref)) ? `https://wa.me/213${norm.slice(1)}` : null;
        phones.push({ raw, normalized: norm, operator: op, operatorLabel: opLabel, opClass, waUrl });
      }
      return { wilayas, payments, prices, deliveries, deliveryMode, phones };
    }

    function detectDialect(text) {
      if (!text) return { region: 'GENERAL_DARJA', confidence: 0, detectedMarkers: [] };
      const baseMarkers = {
        WEST: ['شوالا', 'شاكاين', 'شا', 'غايا', 'باغي', 'حرز', 'راك عاقل', 'شراكم', 'كيراك', 'كيراكم', 'درك', 'صايي', 'غادي', 'chwala', 'chakayn', 'ghaya', 'baghi', 'kirak', 'drk', 'sayi', 'ghadi'],
        EAST: ['واشنهي', 'قداش', 'ياسر', 'ضرك', 'زي', 'باهي', 'علاشنهي', 'واشبيك', 'كفاه', 'ضروك', 'سيرتا', 'بونة', 'عيشك', 'يعيشك', '9dach', 'yaser', 'bahi', '3aychek'],
        CENTER: ['واشنو', 'حكاية', 'دروك', 'هكدا', 'هكداك', 'حوايج', 'البهجة', 'العاصمة', 'دزاير', 'مريڤل', 'حطة', 'wachnou', 'hakda', 'hakdak', 'mrigel', 'hbal'],
        SOUTH: ['واه', 'لاه', 'حتة', 'سوف', 'ميزاب', 'غرداية', 'ادرار', 'بسكرة', 'ورقلة', 'wah', 'lah', '7ata', 'zin'],
      };
      const merged = {};
      for (const reg of ['WEST', 'EAST', 'CENTER', 'SOUTH']) {
        const extra = (DIALECTS_DATA && DIALECTS_DATA.regions && DIALECTS_DATA.regions[reg] && DIALECTS_DATA.regions[reg].markers) || [];
        merged[reg] = Array.from(new Set([...baseMarkers[reg], ...extra]));
      }
      const { tokens } = tokenize(text);
      const lowerTokens = tokens.map(t => t.toLowerCase());
      const tokenSet = new Set(lowerTokens);
      const padded = ` ${lowerTokens.join(' ')} `;
      const scores = { WEST: [], EAST: [], CENTER: [], SOUTH: [] };

      for (const [reg, words] of Object.entries(merged)) {
        for (const w of words) {
          const lw = String(w).toLowerCase().trim();
          if (!lw) continue;
          if (lw.includes(' ')) {
            if (padded.includes(` ${lw} `) && !scores[reg].includes(w)) scores[reg].push(w);
          } else if (tokenSet.has(lw) && !scores[reg].includes(w)) {
            scores[reg].push(w);
          }
        }
      }

      let top = 'GENERAL_DARJA', max = 0, detected = [];
      for (const [r, list] of Object.entries(scores)) {
        if (list.length > max) { max = list.length; top = r; detected = list; }
      }
      return {
        region: top,
        confidence: max > 0 ? Math.min(0.99, Math.round((0.6 + max * 0.15) * 100) / 100) : 0.5,
        detectedMarkers: detected
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
          if (p.startsWith('ال') && p.length > 3) res.add(p.slice(2));
          else if (!p.startsWith('ال')) res.add('ال' + p);
        }
      }
      return Array.from(res).filter(x => x.length > 2 && !GENERIC_CULTURE_STOP.has(x));
    }

    function detectCulturalReferences(text) {
      if (!text || !text.trim()) {
        return { hasCulturalReference: false, proverbs: [], memesAndTrends: [], viralMemes: [], francoDarja: [], landmarks: [], gastronomy: [], slangExpressions: [], allMatches: [], culturalSummary: 'لا توجد إشارات ثقافية خاصة.' };
      }
      const lowerText = text.toLowerCase();
      const { tokens } = tokenize(text);
      const tokenSet = new Set(tokens.map(t => t.toLowerCase()));
      const cultureDb = CULTURE_DATA || { proverbs: [], memes_and_trends: [], landmarks: [], gastronomy: [] };
      const slangDb = SLANG_DATA || { expressions: [] };

      const matchedProverbs = [], matchedTrends = [], matchedLandmarks = [], matchedGastronomy = [], matchedSlang = [], matchedMemes = [], matchedFranco = [];

      for (const p of cultureDb.proverbs || []) {
        if ((p.text && text.includes(p.text)) || (p.arabizi && lowerText.includes(p.arabizi.toLowerCase()))) {
          matchedProverbs.push({ category: 'proverb', canonicalName: p.text, meaning: p.meaning || '' });
        }
      }
      for (const m of cultureDb.memes_and_trends || []) {
        if ((m.phrase && text.includes(m.phrase)) || (m.arabizi && lowerText.includes(m.arabizi.toLowerCase()))) {
          matchedTrends.push({ category: 'meme_trend', canonicalName: m.phrase, meaning: m.meaning || '' });
        }
      }
      for (const vm of (MEMES_DATA && MEMES_DATA.memes) || []) {
        if ((vm.phrase && text.includes(vm.phrase)) || (vm.arabizi && lowerText.includes(vm.arabizi.toLowerCase()))) {
          matchedMemes.push({ category: 'viral_meme', canonicalName: vm.phrase, meaning: (vm.meaning || '') + (vm.origin ? ` [${vm.origin}]` : '') });
        }
      }
      for (const fd of (FRANCO_DATA && FRANCO_DATA.words) || []) {
        const arW = (fd.darja_ar || '').toLowerCase();
        const azW = (fd.arabizi || '').toLowerCase();
        if ((arW && (tokenSet.has(arW) || text.includes(fd.darja_ar))) || (azW && (tokenSet.has(azW) || lowerText.includes(azW)))) {
          matchedFranco.push({ category: 'franco_darja', canonicalName: `${fd.darja_ar} (${fd.arabizi})`, meaning: `${fd.meaning_ar || ''} — الأصل الفرنسي: ${fd.fr_origin}` });
        }
      }
      for (const lmk of cultureDb.landmarks || []) {
        for (const kw of extractKeywords(lmk.name || '')) {
          if (kw && text.includes(kw)) { matchedLandmarks.push({ category: 'landmark', canonicalName: lmk.name, meaning: lmk.description || '' }); break; }
        }
      }
      for (const f of cultureDb.gastronomy || []) {
        let hit = false;
        for (const kw of extractKeywords(f.name || '')) {
          if (kw && text.includes(kw)) { matchedGastronomy.push({ category: 'gastronomy', canonicalName: f.name, meaning: f.description || '' }); hit = true; break; }
        }
        if (!hit && f.arabizi) {
          for (const part of f.arabizi.split('/')) {
            if (part.trim() && lowerText.includes(part.trim().toLowerCase())) { matchedGastronomy.push({ category: 'gastronomy', canonicalName: f.name, meaning: f.description || '' }); break; }
          }
        }
      }
      for (const s of slangDb.expressions || []) {
        let hit = false;
        for (const kw of extractKeywords(s.term || '')) {
          if (kw && text.includes(kw)) { matchedSlang.push({ category: 'slang', canonicalName: s.term, meaning: s.meaning || '' }); hit = true; break; }
        }
        if (!hit && s.arabizi && lowerText.includes(s.arabizi.toLowerCase())) {
          matchedSlang.push({ category: 'slang', canonicalName: s.term, meaning: s.meaning || '' });
        }
      }

      const allMatches = [...matchedProverbs, ...matchedTrends, ...matchedMemes, ...matchedFranco, ...matchedLandmarks, ...matchedGastronomy, ...matchedSlang];
      return { hasCulturalReference: allMatches.length > 0, proverbs: matchedProverbs, memesAndTrends: matchedTrends, viralMemes: matchedMemes, francoDarja: matchedFranco, landmarks: matchedLandmarks, gastronomy: matchedGastronomy, slangExpressions: matchedSlang, allMatches };
    }

    function detectScript(text) {
      const latin = (text.match(/[a-zA-Z]/g) || []).length;
      const arabic = (text.match(/[\u0600-\u06FF]/g) || []).length;
      return arabic > latin ? 'arabic' : 'arabizi';
    }

    function kbTokenize(text) {
      const stop = new Set(['el','al','la','le','de','du','wa','w','f','fi','fel','l','li','ta3','men','mn','b','ala','3la','ya','في','من','على','الى','عن','مع','و','او','ال','لي','تاع','نتاع','وش','واش']);
      const clean = text.toLowerCase().replace(/[!?.,;:\-_/\\]+/g, ' ').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي');
      return (clean.match(/[a-z0-9\u0600-\u06FF']+/g) || []).filter(t => t.length >= 2 && !stop.has(t));
    }

    function respondToDarja(text, persona = 'merchant', forcedScript = 'auto') {
      if (!text || !text.trim()) {
        return { reply: 'مرحباً بيك خويا، كاش ما نسحقو نخدموك؟', intent: 'EMPTY', script: 'arabic', confidence: 1, source: 'default' };
      }
      const resolvedScript = forcedScript === 'auto' ? detectScript(text) : forcedScript;
      const normInput = text.toLowerCase().replace(/[!?.,;:\-_/\\]+/g, ' ').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/(.)\1{2,}/g, '$1').replace(/\s+/g, ' ').trim();
      const rules = (DIALOGUE_RULES_DATA && DIALOGUE_RULES_DATA.rules) || [];

      let bestRule = null;
      for (const rule of rules) {
        const patterns = resolvedScript === 'arabizi' ? rule.patterns_arabizi : rule.patterns_arabic;
        const altPatterns = resolvedScript === 'arabizi' ? rule.patterns_arabic : rule.patterns_arabizi;
        for (const p of (patterns || [])) {
          const normP = p.toLowerCase().trim();
          let score = 0;
          if (normInput === normP) score = normP.length + 200;
          else if (normInput.includes(normP)) score = normP.length + 25;
          else if (normInput.length >= 4 && normP.includes(normInput)) score = normInput.length + 5;
          if (score > 0 && (!bestRule || score > bestRule.score)) bestRule = { score, rule };
        }
        for (const p of (altPatterns || [])) {
          const normP = p.toLowerCase().trim();
          if (normInput.includes(normP)) {
            const score = normP.length + 10;
            if (!bestRule || score > bestRule.score) bestRule = { score, rule };
          }
        }
      }

      if (bestRule) {
        const rule = bestRule.rule;
        const responses = resolvedScript === 'arabizi' ? rule.responses_arabizi : rule.responses_arabic;
        let chosen = (responses && responses[0]) || '';
        if (persona === 'merchant' && rule.intent === 'WELLBEING_INQUIRY') {
          chosen = resolvedScript === 'arabizi' ? 'We cv hamdoulah kho! Marhba bik f la boutique ta3na, kash ma khasek sel3a?' : 'لاباس الحمد لله ربي يحفظك خويا! مرحباً بيك في متجرنا، كاش ما راك تحوس سلعة؟';
        } else if (persona === 'assistant' && rule.intent === 'WELLBEING_INQUIRY') {
          chosen = resolvedScript === 'arabizi' ? 'Hamdoulah! Marhba bik, kifach naqder n3awnek lyoum?' : 'الحمد لله! أهلاً بك، كيف يمكنني مساعدتك اليوم؟';
        }
        return { reply: chosen, intent: rule.intent, script: resolvedScript, confidence: 0.95, source: 'rule' };
      }

      const entries = (DIALOGUE_KB_DATA && DIALOGUE_KB_DATA.entries) || [];
      const qToks = new Set(kbTokenize(text));
      if (qToks.size >= 2 && entries.length > 0) {
        let bestKb = null, bestSim = 0;
        for (const entry of entries) {
          const dToks = new Set(kbTokenize(entry.prompt || ''));
          if (dToks.size === 0) continue;
          let inter = 0;
          for (const t of qToks) if (dToks.has(t)) inter++;
          if (inter === 0) continue;
          let sim = inter / Math.sqrt(qToks.size * dToks.size);
          if (entry.script === resolvedScript) sim += 0.06;
          if (sim > bestSim) { bestSim = sim; bestKb = entry; }
        }
        if (bestKb && bestSim >= 0.34) {
          return { reply: bestKb.reply, intent: bestKb.intent || 'CONVERSATION', script: bestKb.script, confidence: Math.min(0.92, Math.round(bestSim * 100) / 100), source: 'kb_retrieval' };
        }
      }

      return {
        reply: resolvedScript === 'arabizi' ? 'We cv hamdoulah w nta kho? Marhba bik!' : 'مرحباً بيك خويا العزيز! واش راك وكاش ما نسحقو نخدموك؟',
        intent: 'CASUAL_CHAT',
        script: resolvedScript,
        confidence: 0.65,
        source: 'default'
      };
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
          const pattern = new RegExp(`(?<![\\w\\u0600-\\u06FF])${escapeRx(v)}(?![\\w\\u0600-\\u06FF])`, 'gi');
          let m;
          while ((m = pattern.exec(normText)) !== null) {
            const start = m.index, end = start + m[0].length;
            matches.push({ term: item.term || v, category: item.category, severity: item.severity, matchedText: text.slice(start, end) });
            if (severityOrder[item.severity] > severityOrder[highestSeverity]) highestSeverity = item.severity;
            for (let i = start; i < Math.min(end, censoredChars.length); i++) censoredChars[i] = '*';
          }
        }
      }
      const isProfane = matches.length > 0;
      return { isProfane, severity: isProfane ? highestSeverity : 'none', matches, censoredText: censoredChars.join('').replace(/\*+/g, '***') };
    }

    // Tab Navigation
    function switchTab(tabId) {
      document.querySelectorAll('.nav-tab').forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tabId));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.toggle('active', p.id === 'tab-' + tabId));
    }

    function setSentimentMode(mode) {
      sentimentMode = mode;
      document.querySelectorAll('#sentimentModeGroup .seg-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
      processText();
    }

    function setPersona(p) {
      currentPersona = p;
      document.querySelectorAll('#personaGroup .seg-btn').forEach(b => b.classList.toggle('active', b.dataset.persona === p));
      processText();
    }

    function switchDevTab(tab) {
      currentDevTab = tab;
      document.querySelectorAll('[data-devtab]').forEach(b => b.classList.toggle('active', b.dataset.devtab === tab));
      ['json', 'code', 'agent'].forEach(t => {
        document.getElementById('devTab-' + t).style.display = t === tab ? 'block' : 'none';
      });
    }

    async function copyDevOutput() {
      let textToCopy = '';
      if (currentDevTab === 'json') textToCopy = document.getElementById('jsonReportPre').textContent;
      else if (currentDevTab === 'code') textToCopy = document.getElementById('codeSnippetPre').textContent;
      else textToCopy = document.getElementById('agentPromptBox').textContent;
      try {
        await navigator.clipboard.writeText(textToCopy);
        const btn = document.getElementById('copyDevBtn');
        btn.textContent = 'تم النسخ';
        setTimeout(() => { btn.textContent = 'نسخ'; }, 1400);
      } catch {}
    }

    // Analyzer Controller
    const inputArea = document.getElementById('textInput');
    const charCount = document.getElementById('charCount');

    const SAMPLES = [
      "hab nchri 2 hbat XL noir b 500 doro aflou yalidine baridimob 0661234567",
      "بشحال هاذي خاوة السومة تاعها قداش؟ كاش جديد متوفر منها ولا خلاصت؟",
      "السلعة هاااااايلة بزاااااف و الخدمة فور، يعطيك الصحة! توصيل للعلمة سطيف رقمي 0770112233 و نخلصك بـ baridimob",
      "سراقين حشيتوهالي رجعولي دراهمي سلعة خردة وما رديتوش عليا ونشكي بيكم للعدالة ولابوليس!",
      "شوالا راك باغي خوية غايا درك؟ حاب دوزينة مقاس 42 لعين الترك ولاية 31 بـ zr express للدار و نخلصك كاش",
      "طاح الحك وصاب غطاه، ابعثلي رشتة عاصمية لباب الواد و نخلصك كاش",
      "rabi yhfdk hab ncommandi sabat caba mrigel l wahran",
      "wach ya khoy",
      "يا حمار ما تبعثليش سلعة خردة وناقصة",
      "قالو فاك يا حشيشة و زوخ وطير و وان تو ثري فيفا لالجيري",
      "Khoya, had sabat chhal mellekher? Ghali chwiya.",
      "Thbliiii bravo souade"
    ];

    function loadSample(idx) {
      inputArea.value = SAMPLES[idx];
      processText();
    }

    function processText() {
      const text = inputArea.value;
      charCount.textContent = `${text.length} chars`;

      const esc = detectEscalation(text);
      const escBox = document.getElementById('escalationStatusBox');
      if (esc.needsEscalation) {
        escBox.innerHTML = `<div class="escalation-alert"><div><div style="font-weight:800; font-size:15px; color:#f87171;">تنبيه تصعيد بشري عاجل (${escapeHtml(esc.urgency)})</div><div style="font-size:13px; margin-top:2px;">السبب: <strong>${escapeHtml(esc.reason)}</strong> — ${escapeHtml(esc.guideline)}</div><div style="font-size:11px; color:#fca5a5; margin-top:4px;">الكلمات المرصودة: ${esc.matchedTriggers.map(escapeHtml).join('، ')}</div></div></div>`;
      } else {
        escBox.innerHTML = `<div class="escalation-healthy"><svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg><span>محادثة آمنة وطبيعية: لا تتطلب تصعيداً بشرياً ويمكن للوكيل الآلي معالجتها مباشرة.</span></div>`;
      }

      const intentRes = identifyIntent(text);
      const intentMap = {
        ORDER: { label: 'طلب شراء (ORDER)', cls: 'intent-order' },
        PRICE_INQUIRY: { label: 'استفسار عن السعر (PRICE_INQUIRY)', cls: 'intent-price' },
        DELIVERY_INQUIRY: { label: 'استفسار عن التوصيل (DELIVERY_INQUIRY)', cls: 'intent-delivery' },
        AVAILABILITY_INQUIRY: { label: 'توفر السلعة (AVAILABILITY_INQUIRY)', cls: 'intent-availability' },
        COMPLAINT: { label: 'شكوى / مشكلة (COMPLAINT)', cls: 'intent-complaint' },
        GREETING: { label: 'تحية وتواصل (GREETING)', cls: 'intent-greeting' },
        UNKNOWN: { label: 'غير محدد (UNKNOWN)', cls: 'intent-unknown' }
      };
      const iInfo = intentMap[intentRes.intent] || intentMap.UNKNOWN;
      const iBadge = document.getElementById('intentBadge');
      iBadge.className = 'intent-badge ' + iInfo.cls;
      iBadge.textContent = iInfo.label;
      document.getElementById('intentConfidence').textContent = intentRes.confidence > 0 ? `ثقة ${(intentRes.confidence * 100).toFixed(0)}%` : '-';
      document.getElementById('intentKeywords').innerHTML = intentRes.matchedKeywords.length
        ? intentRes.matchedKeywords.map(k => `<span class="token-pill token-info">${escapeHtml(k)}</span>`).join('')
        : '<span class="empty-state">لا توجد مفاتيح نية صريحة</span>';

      const sent = analyzeSentiment(text, sentimentMode);
      const sBadge = document.getElementById('sentimentBadge');
      document.getElementById('sentimentScore').textContent = (sent.score >= 0 ? '+' : '') + sent.score.toFixed(2);
      document.getElementById('sentimentMethodBadge').textContent = sent.method;
      sBadge.className = 'sentiment-badge ' + (sent.label === 'POSITIVE' ? 'badge-positive' : sent.label === 'NEGATIVE' ? 'badge-negative' : sent.label === 'MIXED' ? 'badge-mixed' : 'badge-neutral');
      sBadge.textContent = { POSITIVE: 'إيجابي (POSITIVE)', NEGATIVE: 'سلبي (NEGATIVE)', MIXED: 'مختلط (MIXED)', NEUTRAL: 'محايد (NEUTRAL)' }[sent.label] || sent.label;

      const pPos = Math.round((sent.probabilities?.POSITIVE || 0) * 100);
      const pNeu = Math.round((sent.probabilities?.NEUTRAL || 0) * 100);
      const pNeg = Math.max(0, 100 - pPos - pNeu);
      document.getElementById('probBarPos').style.width = pPos + '%';
      document.getElementById('probBarNeu').style.width = pNeu + '%';
      document.getElementById('probBarNeg').style.width = pNeg + '%';
      document.getElementById('probLegend').textContent = `POS ${pPos}%  |  NEU ${pNeu}%  |  NEG ${pNeg}%`;

      const tPills = [
        ...sent.positiveTokens.map(t => `<span class="token-pill token-pos">+ ${escapeHtml(t)}</span>`),
        ...sent.negativeTokens.map(t => `<span class="token-pill token-neg">- ${escapeHtml(t)}</span>`)
      ];
      document.getElementById('tokensBox').innerHTML = tPills.length ? tPills.join('') : '<span class="empty-state">لا توجد كلمات مشاعر مباشرة</span>';
      document.getElementById('negationFlag').style.display = sent.negated ? 'block' : 'none';

      const entities = extractEntities(text);
      document.getElementById('wilayasBox').innerHTML = entities.wilayas.length
        ? entities.wilayas.map(w => `<div class="entity-tag"><span class="entity-code">${escapeHtml(w.code_str || w.code)}</span><strong>${escapeHtml(w.name_ar)}</strong><span style="color:var(--text-muted); font-size:11px;">(${escapeHtml(w.name_fr)})</span>${w.era === 69 ? '<span class="era69-badge">جديدة 59-69</span>' : ''}${w.commune ? `<span class="commune-badge">بلدية ${escapeHtml(w.commune)}</span>` : ''}</div>`).join('')
        : '<span class="empty-state">لم يتم رصد ولايات أو بلديات في النص</span>';

      const quantities = extractQuantities(text);
      const attrs = extractProductAttributes(text);
      document.getElementById('quantitiesBox').innerHTML = quantities.length
        ? quantities.map(q => `<span class="qty-tag">${escapeHtml(q.value)} ${escapeHtml(q.unit)} (${escapeHtml(q.raw)})</span>`).join('')
        : '<span class="empty-state">لم ترصد كميات محددة</span>';
      document.getElementById('attributesBox').innerHTML = (attrs.colors.length || attrs.sizes.length)
        ? [...attrs.colors.map(c => `<span class="attr-tag">${escapeHtml(c)}</span>`), ...attrs.sizes.map(s => `<span class="attr-tag">مقاس ${escapeHtml(s)}</span>`)].join('')
        : '<span class="empty-state">لا توجد ألوان أو مقاسات مرصودة</span>';

      document.getElementById('paymentsBox').innerHTML = entities.payments.length
        ? entities.payments.map(p => `<span class="payment-tag">${escapeHtml(p.label)}</span>`).join('')
        : '<span class="empty-state">لم تحدد وسيلة دفع</span>';
      document.getElementById('pricesBox').innerHTML = entities.prices.length
        ? entities.prices.map(pr => `<span class="price-tag">${escapeHtml(pr.raw)} &rarr; ${pr.amount.toLocaleString()} دج</span>`).join('')
        : '<span class="empty-state">لا توجد أسعار مرصودة</span>';

      const delHtml = [
        ...(entities.deliveries || []).map(d => `<span class="carrier-tag">${escapeHtml(d.label)}</span>`),
        entities.deliveryMode ? `<span class="mode-tag">${escapeHtml(entities.deliveryMode)}</span>` : ''
      ].filter(Boolean);
      document.getElementById('deliveriesBox').innerHTML = delHtml.length ? delHtml.join('') : '<span class="empty-state">لم تحدد شركة توصيل</span>';

      document.getElementById('phonesBox').innerHTML = (entities.phones && entities.phones.length)
        ? entities.phones.map(ph => `<div class="phone-tag"><span class="mono">${escapeHtml(ph.normalized)}</span>${ph.operatorLabel ? `<span class="operator-tag ${ph.opClass}">${escapeHtml(ph.operatorLabel)}</span>` : ''}${ph.waUrl ? `<a href="${escapeHtml(ph.waUrl)}" target="_blank" rel="noopener" class="wa-btn">WhatsApp</a>` : ''}</div>`).join('')
        : '<span class="empty-state">لا توجد أرقام هواتف</span>';

      const dialect = detectDialect(text);
      const regNames = { WEST: 'الغرب الجزائري (WEST)', EAST: 'الشرق الجزائري (EAST)', CENTER: 'الوسط الجزائري (CENTER)', SOUTH: 'الجنوب الجزائري (SOUTH)', GENERAL_DARJA: 'دارجة جزائرية عامة (GENERAL)' };
      document.getElementById('dialectBadge').textContent = regNames[dialect.region] || dialect.region;
      document.getElementById('dialectConfidence').textContent = `ثقة ${(dialect.confidence * 100).toFixed(0)}%`;
      document.getElementById('dialectMarkers').innerHTML = dialect.detectedMarkers.length
        ? dialect.detectedMarkers.map(m => `<span class="token-pill token-info">${escapeHtml(m)}</span>`).join('')
        : '<span class="empty-state">لا توجد مؤشرات جهوية حصرية</span>';

      const cultural = detectCulturalReferences(text);
      const catMeta = {
        proverb: { title: 'مثل شعبي', style: 'background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.45); color:#fcd34d;' },
        meme_trend: { title: 'ترند شائع', style: 'background:rgba(236,72,153,0.12); border:1px solid rgba(236,72,153,0.45); color:#f9a8d4;' },
        viral_meme: { title: 'ميم جزائري', style: 'background:rgba(244,63,94,0.12); border:1px solid rgba(244,63,94,0.45); color:#fda4af;' },
        franco_darja: { title: 'فرانكو-دارجة', style: 'background:rgba(6,182,212,0.12); border:1px solid rgba(6,182,212,0.45); color:#67e8f9;' },
        landmark: { title: 'معلم / سوق', style: 'background:rgba(59,130,246,0.12); border:1px solid rgba(59,130,246,0.45); color:#93c5fd;' },
        gastronomy: { title: 'مأكولات تقليدية', style: 'background:rgba(16,185,129,0.12); border:1px solid rgba(16,185,129,0.45); color:#6ee7b7;' },
        slang: { title: 'لغة الشارع والتجارة', style: 'background:rgba(168,85,247,0.12); border:1px solid rgba(168,85,247,0.45); color:#d8b4fe;' }
      };
      document.getElementById('culturalBox').innerHTML = cultural.allMatches.length
        ? cultural.allMatches.map(m => {
            const c = catMeta[m.category] || catMeta.slang;
            return `<div style="${c.style} border-radius:9px; padding:7px 11px; font-size:12px;"><strong>${c.title}: ${escapeHtml(m.canonicalName)}</strong> <span style="opacity:0.88;">— ${escapeHtml(m.meaning)}</span></div>`;
          }).join('')
        : '<span class="empty-state">لا توجد إشارات ثقافية أو ميمز أو فرانكو-دارجة في هذا النص</span>';

      const arabiziClean = arabiziToArabic(text);
      document.getElementById('arabiziBox').textContent = arabiziClean || '-';
      const profRes = detectProfanity(text);
      document.getElementById('profanityStatusBox').innerHTML = profRes.isProfane
        ? `<div style="background:var(--crimson-soft); border:1px solid var(--crimson); color:#fca5a5; border-radius:8px; padding:7px 12px; font-size:12px; font-weight:700;">رصد محتوى غير لائق (الخطورة: ${escapeHtml(profRes.severity.toUpperCase())}) — ${profRes.matches.length} كلمة</div>`
        : `<div style="background:var(--primary-soft); border:1px solid rgba(16,185,129,0.4); color:#6ee7b7; border-radius:8px; padding:7px 12px; font-size:12px; font-weight:700;">النص آمن ونظيف (Clean &amp; Safe)</div>`;
      document.getElementById('censoredTextBox').textContent = profRes.censoredText || '-';

      const chatRes = respondToDarja(text, currentPersona);
      document.getElementById('dialogueReplyBox').textContent = chatRes.reply;
      document.getElementById('dialogueScriptBadge').textContent = chatRes.script === 'arabizi' ? 'Script: Arabizi' : 'Script: Arabic';
      document.getElementById('dialogueSourceBadge').textContent = chatRes.source === 'kb_retrieval' ? `DziriAlign/KB (${Math.round(chatRes.confidence * 100)}%)` : `Engine: ${chatRes.source}`;
      document.getElementById('dialogueIntentBadge').textContent = chatRes.intent;

      lastAnalyzeReport = {
        intent: intentRes,
        sentiment: sent,
        dialect,
        entities: {
          wilayas: entities.wilayas.map(w => ({ code: w.code, name_ar: w.name_ar, name_fr: w.name_fr, commune: w.commune })),
          payments: entities.payments.map(p => p.type),
          prices_dzd: entities.prices,
          deliveries: entities.deliveries.map(d => d.company),
          delivery_mode: entities.deliveryMode,
          phones: entities.phones.map(p => ({ normalized: p.normalized, operator: p.operator, whatsapp_url: p.waUrl })),
          quantities,
          attributes: attrs
        },
        escalation: esc,
        profanity: { is_profane: profRes.isProfane, severity: profRes.severity, censored_text: profRes.censoredText },
        cultural_matches: cultural.allMatches.length,
        reply: chatRes
      };

      document.getElementById('jsonReportPre').textContent = JSON.stringify(lastAnalyzeReport, null, 2);
      const safeStr = JSON.stringify(text);
      document.getElementById('codeSnippetPre').textContent =
`# Python (Zero-Dependency)
from darja_nlp import DarjaPipeline, analyze
report = analyze(${safeStr}, sentiment_mode="${sentimentMode}")
print(report.intent.intent, report.entities.wilayas, report.reply.reply)

// TypeScript / Node.js (Zero-Dependency)
import { analyze } from '@dz-open-suite/darja-nlp-kit';
const report = analyze(${safeStr}, { sentimentMode: '${sentimentMode}', persona: '${currentPersona}' });
console.log(report.intent?.intent, report.entities?.wilayas, report.reply?.reply);`;

      const wilayaName = entities.wilayas.length ? `${entities.wilayas[0].name_ar} (${entities.wilayas[0].code})` : 'غير محددة';
      const priceText = entities.prices.length ? `${entities.prices[0].amount.toLocaleString()} دج` : 'غير محدد';
      document.getElementById('agentPromptBox').textContent =
`[سياق الزبون المستخرج عبر darja-nlp-kit]:
- الرسالة: ${text}
- النية: ${intentRes.intent} | اللهجة: ${dialect.region} | المشاعر: ${sent.label} (${sent.score.toFixed(2)})
- الولاية: ${wilayaName} | السعر: ${priceText}
- التصعيد البشري: ${esc.needsEscalation ? esc.urgency + ' (' + esc.reason + ')' : 'لا'}
[التعليمات]: التزم بهذه الحقائق وأجب بدارجة جزائرية عفوية دون هلوسة.`;

      let agentReply = chatRes.reply;
      if (esc.needsEscalation) agentReply = `تم إيقاف الرد الآلي وتحويل المحادثة للمشرف البشري بسبب (${esc.reason}).`;
      else if (entities.wilayas.length && entities.prices.length) agentReply = `مرحباً خويا، الطلبية مسجلة لـ ${wilayaName} بقيمة ${priceText}. ${chatRes.reply}`;
      document.getElementById('agentReplyBox').textContent = agentReply;

      const matchedDialogue = (DIALOGUES_DATA || []).find(d => d.region === dialect.region && d.intent === intentRes.intent) || (DIALOGUES_DATA || [])[0];
      if (matchedDialogue) {
        document.getElementById('matchingDialogueBox').innerHTML = `<div style="margin-bottom:4px;"><strong>[${escapeHtml(matchedDialogue.region)}] الزبون:</strong> "${escapeHtml(matchedDialogue.customer_message)}"</div><div><strong>رد التاجر:</strong> "${escapeHtml(matchedDialogue.merchant_response)}"</div>`;
      }
    }

    // DarjaChat Multi-Turn Engine
    const chatState = {
      history: [],
      dialect: 'GENERAL_DARJA',
      preferredScript: null,
      activeIntent: 'UNKNOWN',
      slots: { wilayas: [], phones: [], deliveries: [], delivery_mode: null, payments: [], prices_dzd: [], quantities: [], colors: [], sizes: [] }
    };

    function resetChatSession() {
      chatState.history = [];
      chatState.dialect = 'GENERAL_DARJA';
      chatState.preferredScript = null;
      chatState.activeIntent = 'UNKNOWN';
      chatState.slots = { wilayas: [], phones: [], deliveries: [], delivery_mode: null, payments: [], prices_dzd: [], quantities: [], colors: [], sizes: [] };
      renderChatUI();
    }

    function sendQuickChat(msg) {
      document.getElementById('chatInput').value = msg;
      sendChatTurn();
    }

    function runChatAutoDemo() {
      resetChatSession();
      ['wach ya khoy', 'hab nchri 2 hbat noir XL', 'l aflou b yalidine 0661234567'].forEach(m => {
        document.getElementById('chatInput').value = m;
        sendChatTurn();
      });
    }

    function sendChatTurn() {
      const inp = document.getElementById('chatInput');
      const msg = inp.value.trim();
      if (!msg) return;
      inp.value = '';

      const turnScript = detectScript(msg);
      chatState.preferredScript = turnScript;
      const esc = detectEscalation(msg);
      const dia = detectDialect(msg);
      if (dia.region !== 'GENERAL_DARJA') chatState.dialect = dia.region;
      const intentRes = identifyIntent(msg);
      if (intentRes.intent !== 'UNKNOWN') chatState.activeIntent = intentRes.intent;

      const ent = extractEntities(msg);
      const qts = extractQuantities(msg);
      const attrs = extractProductAttributes(msg);
      let newlyCaptured = 0;

      for (const w of ent.wilayas) if (!chatState.slots.wilayas.some(x => x.code === w.code)) { chatState.slots.wilayas.push(w); newlyCaptured++; }
      for (const p of ent.phones) if (!chatState.slots.phones.some(x => x.normalized === p.normalized)) { chatState.slots.phones.push(p); newlyCaptured++; }
      for (const d of ent.deliveries) if (!chatState.slots.deliveries.includes(d.label)) chatState.slots.deliveries.push(d.label);
      if (ent.deliveryMode && !chatState.slots.delivery_mode) chatState.slots.delivery_mode = ent.deliveryMode;
      for (const py of ent.payments) if (!chatState.slots.payments.includes(py.label)) chatState.slots.payments.push(py.label);
      for (const pr of ent.prices) if (!chatState.slots.prices_dzd.includes(pr.amount)) chatState.slots.prices_dzd.push(pr.amount);
      for (const q of qts) { chatState.slots.quantities.push(q); newlyCaptured++; }
      for (const c of attrs.colors) if (!chatState.slots.colors.includes(c)) chatState.slots.colors.push(c);
      for (const s of attrs.sizes) if (!chatState.slots.sizes.includes(s)) chatState.slots.sizes.push(s);

      chatState.history.push({ role: 'user', text: msg, intent: intentRes.intent });

      const missing = [];
      if (chatState.slots.wilayas.length === 0) missing.push('wilaya');
      if (chatState.slots.phones.length === 0) missing.push('phone');
      const ready = missing.length === 0;
      const isOrderFlow = chatState.activeIntent === 'ORDER' || chatState.activeIntent === 'DELIVERY_INQUIRY' || newlyCaptured > 0;

      let reply = '', tIntent = '';
      if (esc.needsEscalation) {
        reply = turnScript === 'arabizi'
          ? "Smahlna bzaf kho! Rani n7awel had l'message drk l'responsable bach yreglihleek koulchi."
          : 'نعتذرو منك بزاف خويا! راني نحول رسالتك فوراً للمسؤول باش يتواصل معاك ويريڤليلك الإشكال.';
        tIntent = `ESCALATION_${esc.reason}`;
      } else if (isOrderFlow && ready && newlyCaptured > 0) {
        const w = chatState.slots.wilayas[chatState.slots.wilayas.length - 1];
        const ph = chatState.slots.phones[chatState.slots.phones.length - 1].normalized;
        reply = turnScript === 'arabizi'
          ? `Sahit kho! La commande ta3ek mrigla w confirmée: wilaya ${w.name_fr} (${w.code}), téléphone ${ph}. Livraison f 24-48h!`
          : `صحيت خويا! طلبيتك مؤكدة ومسجلة: ولاية ${w.name_ar} (${w.code})، الهاتف ${ph}. التوصيل خلال 24-48 ساعة!`;
        tIntent = 'ORDER_CONFIRMED';
      } else if (chatState.activeIntent === 'ORDER' && !ready && (newlyCaptured > 0 || intentRes.intent === 'ORDER')) {
        if (missing.includes('wilaya') && missing.includes('phone')) {
          reply = turnScript === 'arabizi'
            ? 'Marhba bik kho! Ab3atli bark lwilaya w numéro de téléphone bach nconfirmiwlek la commande.'
            : 'مرحباً بيك خويا! ابعثلي برك الولاية ورقم الهاتف باش نكونفيرميولك الطلبية.';
        } else if (missing.includes('phone')) {
          const w = chatState.slots.wilayas[chatState.slots.wilayas.length - 1];
          reply = turnScript === 'arabizi'
            ? `C'est bon lwilaya ${w.name_fr} msajla! Ba9i ghi numéro de téléphone kho.`
            : `ممتاز، ولاية ${w.name_ar} مسجلة! بقالنا برك رقم الهاتف خويا باش نكملو الطلب.`;
        } else {
          const ph = chatState.slots.phones[chatState.slots.phones.length - 1].normalized;
          reply = turnScript === 'arabizi'
            ? `Numéro ${ph} msajel kho! 9olli bark chmen wilaya w nwalou f lwa9t.`
            : `رقم الهاتف ${ph} مسجل! قولي برك واش من ولاية باش نكونفيرميو الطلب.`;
        }
        tIntent = 'ORDER_SLOT_FILLING';
      } else {
        const dRes = respondToDarja(msg, currentPersona, turnScript);
        reply = dRes.reply;
        tIntent = dRes.intent;
      }

      chatState.history.push({ role: 'assistant', text: reply, intent: tIntent });
      renderChatUI();
    }

    function renderChatUI() {
      const box = document.getElementById('chatMessages');
      if (chatState.history.length === 0) {
        box.innerHTML = '<div style="margin:auto; text-align:center; color:var(--text-muted); font-size:13px;">ابدأ بإرسال رسالة من الأسفل أو اضغط "تشغيل سيناريو طلبية كامل"</div>';
      } else {
        box.innerHTML = chatState.history.map(m => `<div class="msg-row ${m.role}"><div class="msg-bubble" dir="auto">${escapeHtml(m.text)}</div><div class="msg-meta" dir="ltr">${m.role === 'user' ? 'User' : 'Bot'} · ${escapeHtml(m.intent)}</div></div>`).join('');
        box.scrollTop = box.scrollHeight;
      }

      const s = chatState.slots;
      const ready = s.wilayas.length > 0 && s.phones.length > 0;
      const rBadge = document.getElementById('chatReadyBadge');
      rBadge.textContent = ready ? 'الطلبية جاهزة للتأكيد' : 'بانتظار إكمال البيانات';
      rBadge.className = 'token-pill ' + (ready ? 'token-pos' : 'token-info');

      const items = [
        ['الولاية (مطلوب)', s.wilayas.length ? s.wilayas.map(w => `${w.code} - ${w.name_ar}`).join('، ') : 'ناقصة'],
        ['الهاتف (مطلوب)', s.phones.length ? s.phones.map(p => `${p.normalized} (${p.operatorLabel || '-'})`).join('، ') : 'ناقص'],
        ['الكمية', s.quantities.length ? s.quantities.map(q => `${q.value} ${q.unit}`).join('، ') : '-'],
        ['الألوان والمقاسات', [...s.colors, ...s.sizes].join(' | ') || '-'],
        ['شركة التوصيل', s.deliveries.join('، ') || '-'],
        ['وسيلة الدفع', s.payments.join('، ') || '-'],
        ['السعر المحسوب', s.prices_dzd.length ? s.prices_dzd.map(p => p.toLocaleString() + ' دج').join('، ') : '-'],
        ['اللهجة المرصودة', chatState.dialect]
      ];
      document.getElementById('chatSlotsPanel').innerHTML = items.map(([k, v]) => `<div class="slot-item"><span class="slot-label">${escapeHtml(k)}</span><span class="slot-value">${escapeHtml(v)}</span></div>`).join('');
    }

    // DarjaClassifier Studio (100% JSON compatible with Python & TS)
    class BrowserClassifier {
      constructor(alpha = 1.0) {
        this.alpha = alpha;
        this.classCounts = {};
        this.tokenCounts = {};
        this.classTotals = {};
        this.vocab = new Set();
      }
      extractFeatures(text) {
        const normed = normalize((text || '').toLowerCase());
        const toks = normed.match(/[a-zA-Z0-9\u0621-\u064A\u0671-\u06D3]+/g) || [];
        const feats = [...toks];
        for (let i = 0; i < toks.length - 1; i++) feats.push(toks[i] + '_' + toks[i + 1]);
        for (const w of toks) {
          if (w.length >= 5 && /^[a-zA-Z\u0621-\u064A\u0671-\u06D3]+$/.test(w)) {
            feats.push('p3:' + w.slice(0, 3));
            feats.push('s3:' + w.slice(-3));
          }
        }
        return feats;
      }
      fit(pairs) {
        this.classCounts = {}; this.tokenCounts = {}; this.classTotals = {}; this.vocab = new Set();
        for (const [text, lbl] of pairs) {
          if (this.classCounts[lbl] === undefined) { this.classCounts[lbl] = 0; this.tokenCounts[lbl] = {}; this.classTotals[lbl] = 0; }
          this.classCounts[lbl]++;
          for (const f of this.extractFeatures(text)) {
            this.tokenCounts[lbl][f] = (this.tokenCounts[lbl][f] || 0) + 1;
            this.classTotals[lbl]++;
            this.vocab.add(f);
          }
        }
        return this;
      }
      predict(text) {
        const labels = Object.keys(this.classCounts).sort();
        if (!labels.length) return { label: 'N/A', confidence: 0, probabilities: {} };
        const totalDocs = Object.values(this.classCounts).reduce((a, b) => a + b, 0);
        const vSize = Math.max(1, this.vocab.size);
        const feats = this.extractFeatures(text);
        const logs = {};
        for (const lbl of labels) {
          let sc = Math.log(this.classCounts[lbl] / totalDocs);
          const denom = this.classTotals[lbl] + this.alpha * vSize;
          for (const f of feats) if (this.vocab.has(f)) sc += Math.log(((this.tokenCounts[lbl][f] || 0) + this.alpha) / denom);
          logs[lbl] = sc;
        }
        const maxS = Math.max(...Object.values(logs));
        const exps = {}; let sumE = 0;
        for (const lbl of labels) { exps[lbl] = Math.exp(Math.max(-50, logs[lbl] - maxS)); sumE += exps[lbl]; }
        const probabilities = {}; let best = labels[0];
        for (const lbl of labels) {
          probabilities[lbl] = Math.round((exps[lbl] / (sumE || 1)) * 10000) / 10000;
          if (probabilities[lbl] > probabilities[best]) best = lbl;
        }
        return { label: best, confidence: probabilities[best], probabilities };
      }
      toJSON() {
        return { version: '1.0', alpha: this.alpha, use_bigrams: true, use_subwords: true, class_counts: this.classCounts, class_totals: this.classTotals, token_counts: this.tokenCounts };
      }
    }

    const browserClf = new BrowserClassifier();
    const CLF_PRESETS = {
      commerce: `سلام حاب نكوموندي زوج حبات لوهران | ORDER
راني باغي نشري واحدة لسطيف | ORDER
ابعثلي حبة للجزائر 0661234567 | ORDER
شحال السومة تاعها خويا | PRICE
بشحال يدير هذا الكولي | PRICE
شحال السعر تاع السبردينة لسطيف | PRICE
سلعة مكسرة رجعولي دراهمي | COMPLAINT
خردة وحشيتوهالي روتور | COMPLAINT
ما وصلتنيش الأمانة روطار | COMPLAINT
شحال التوصيل لياليدين للدار | DELIVERY
توصلو لولاية أفلو ولا لا | DELIVERY
وقتاش تلحقني الكولي لورقلة | DELIVERY`,
      dialect: `شوالا راك باغي خويا غايا درك | WEST
صايي مريڤل راني نوليلك غادي | WEST
واشنهي هادا قداش يدير ياسر باهي | EAST
عيشك خويا ضرك نشوفولك قندورة في بونة | EAST
واشنو هكداك حوايج البهجة العاصمة دروك | CENTER
رانا هنا في دزاير صحيت خويا | CENTER
واه مرحب بيك في غرداية وبسكرة وورقلة | SOUTH
على الراس والعين في ادرار سومة زينة | SOUTH`
    };

    function loadClfPreset(key) {
      document.getElementById('clfTrainData').value = CLF_PRESETS[key];
      if (key === 'dialect') document.getElementById('clfTestInput').value = 'شوالا خويا غايا راك باغي واحدة لوهران';
      else document.getElementById('clfTestInput').value = 'شحال السومة تاع السبردينة لسطيف؟';
      trainBrowserClassifier();
    }

    function trainBrowserClassifier() {
      const raw = document.getElementById('clfTrainData').value.split('\n');
      const pairs = raw.map(l => l.trim()).filter(Boolean).map(l => {
        const idx = l.lastIndexOf('|');
        return idx > 0 ? [l.slice(0, idx).trim(), l.slice(idx + 1).trim()] : null;
      }).filter(Boolean);
      if (!pairs.length) return;
      browserClf.fit(pairs);
      let correct = 0;
      const classes = Object.keys(browserClf.classCounts);
      const stats = Object.fromEntries(classes.map(c => [c, { tp: 0, fp: 0, fn: 0 }]));
      for (const [t, y] of pairs) {
        const pred = browserClf.predict(t).label;
        if (pred === y) { correct++; stats[y].tp++; }
        else { stats[pred].fp++; stats[y].fn++; }
      }
      const acc = Math.round((correct / pairs.length) * 1000) / 10;
      const f1s = classes.map(c => {
        const { tp, fp, fn } = stats[c];
        const p = tp + fp ? tp / (tp + fp) : 0;
        const r = tp + fn ? tp / (tp + fn) : 0;
        return p + r ? (2 * p * r) / (p + r) : 0;
      });
      const macroF1 = Math.round((f1s.reduce((a, b) => a + b, 0) / f1s.length) * 1000) / 10;
      document.getElementById('clfAccVal').textContent = acc + '%';
      document.getElementById('clfF1Val').textContent = macroF1 + '%';
      document.getElementById('clfVocabVal').textContent = browserClf.vocab.size;
      predictWithBrowserClf();
    }

    function predictWithBrowserClf() {
      const txt = document.getElementById('clfTestInput').value;
      const res = browserClf.predict(txt);
      const bars = Object.entries(res.probabilities).sort((a, b) => b[1] - a[1]).map(([lbl, pr]) => {
        const pct = Math.round(pr * 1000) / 10;
        return `<div style="margin-bottom:8px;"><div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:3px;"><strong class="mono">${escapeHtml(lbl)}</strong><span class="mono">${pct}%</span></div><div style="background:#1e293b; height:7px; border-radius:999px; overflow:hidden;"><div style="background:var(--primary); width:${pct}%; height:100%;"></div></div></div>`;
      }).join('');
      document.getElementById('clfPredBox').innerHTML = `<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;"><span style="font-size:13px; color:var(--text-muted);">التصنيف المتوقع:</span><span class="intent-badge intent-order mono">${escapeHtml(res.label)} (${Math.round(res.confidence * 100)}%)</span></div>${bars}`;
    }

    function downloadClassifierModel() {
      const blob = new Blob([JSON.stringify(browserClf.toJSON(), null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'classifier_model.json';
      a.click();
      URL.revokeObjectURL(url);
    }

    // 69 Wilayas Explorer
    function setWilayaFilter(f) {
      currentWilayaFilter = f;
      document.querySelectorAll('[data-wfilter]').forEach(b => b.classList.toggle('active', b.dataset.wfilter === f));
      renderWilayasExplorer();
    }

    function renderWilayasExplorer() {
      const q = (document.getElementById('wilayaSearchInput').value || '').trim().toLowerCase();
      const filtered = WILAYAS_DATA.filter(w => {
        if (currentWilayaFilter === 'era69' && w.era !== 69) return false;
        if (!q) return true;
        const coms = [...(w.communes_sample || []), ...(w.communes_fr_sample || [])].join(' ').toLowerCase();
        return String(w.code).includes(q) || String(w.code_str).includes(q) || (w.name_ar || '').toLowerCase().includes(q) || (w.name_fr || '').toLowerCase().includes(q) || coms.includes(q);
      });
      document.getElementById('wilayaCountInfo').textContent = `عرض ${filtered.length} ولاية من أصل ${WILAYAS_DATA.length} ولاية رسمية`;
      document.getElementById('wilayaExplorerGrid').innerHTML = filtered.map(w => {
        const sampleComs = (w.communes_sample || []).slice(0, 5).map(escapeHtml).join('، ');
        return `<div class="wilaya-card"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;"><span class="entity-code">${escapeHtml(w.code_str || w.code)}</span>${w.era === 69 ? '<span class="era69-badge">ولاية جديدة</span>' : `<span class="mono" style="font-size:11px; color:var(--text-muted);">هاتف ${escapeHtml(w.phone_code || '-')}</span>`}</div><div style="font-weight:800; font-size:15px;">${escapeHtml(w.name_ar)} <span style="font-weight:400; color:var(--text-muted); font-size:12px;">(${escapeHtml(w.name_fr)})</span></div><div style="font-size:11px; color:var(--text-muted); margin-top:6px;">البلديات: ${sampleComs || '-'}</div></div>`;
      }).join('');
    }

    // Initialize Everything
    inputArea.addEventListener('input', processText);
    processText();
    renderChatUI();
    loadClfPreset('commerce');
    renderWilayasExplorer();
  </script>
</body>
</html>
"""

    html_content = (
        template.replace('__STOPWORDS_DATA__', json.dumps(stopwords_data, ensure_ascii=False))
        .replace('__LEXICON_DATA__', json.dumps(lexicon_data, ensure_ascii=False))
        .replace('__ARABIZI_RULES__', json.dumps(arabizi_rules, ensure_ascii=False))
        .replace('__WILAYAS_DATA__', json.dumps(wilayas_data, ensure_ascii=False))
        .replace('__DIALECTS_DATA__', json.dumps(dialects_data, ensure_ascii=False))
        .replace('__DIALOGUES_DATA__', json.dumps(dialogues_data, ensure_ascii=False))
        .replace('__CULTURE_DATA__', json.dumps(culture_data, ensure_ascii=False))
        .replace('__SLANG_DATA__', json.dumps(slang_data, ensure_ascii=False))
        .replace('__PROFANITY_DATA__', json.dumps(profanity_data, ensure_ascii=False))
        .replace('__DIALOGUE_RULES_DATA__', json.dumps(dialogue_rules_data, ensure_ascii=False))
        .replace('__MEMES_DATA__', json.dumps(memes_data, ensure_ascii=False))
        .replace('__FRANCO_DATA__', json.dumps(franco_data, ensure_ascii=False))
        .replace('__SENTIMENT_MODEL__', json.dumps(sentiment_model_data, ensure_ascii=False, separators=(',', ':')))
        .replace('__DIALOGUE_KB_DATA__', json.dumps(dialogue_kb_data, ensure_ascii=False, separators=(',', ':')))
    )

    out_file = docs_dir / 'index.html'
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f'[OK] Standalone web playground studio generated at: {out_file} ({len(html_content):,} bytes)')


if __name__ == '__main__':
    main()
