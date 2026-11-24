"""
Export Algerian Darja dataset into standard AI fine-tuning formats:
- Alpaca format (alpaca_darja.json)
- ShareGPT format (sharegpt_darja.json)
- OpenAI fine-tuning JSONL (openai_finetune_darja.jsonl)
"""
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent.parent
    dialogues_path = root / "data" / "dialogues.json"
    culture_path = root / "data" / "culture.json"
    slang_path = root / "data" / "slang.json"
    export_dir = root / "data" / "fine_tuning"
    export_dir.mkdir(parents=True, exist_ok=True)

    with open(dialogues_path, "r", encoding="utf-8") as f:
        dialogues = json.load(f)

    culture_data = {}
    if culture_path.exists():
        with open(culture_path, "r", encoding="utf-8") as f:
            culture_data = json.load(f)

    slang_data = {}
    if slang_path.exists():
        with open(slang_path, "r", encoding="utf-8") as f:
            slang_data = json.load(f)

    # 1. Alpaca Format
    alpaca_records = []
    # Dialogues
    for d in dialogues:
        alpaca_records.append({
            "instruction": f"أنت تاجر وممثل خدمة عملاء جزائري محترف. رد على رسالة الزبون بدارجة جزائرية واقعية وطبيعية 100% تطابق لهجة منطقته ({d['region']}) ونبرة المتجر الودية.",
            "input": d["customer_message"],
            "output": d["merchant_response"],
            "region": d["region"],
            "intent": d["intent"]
        })

    # Cultural Proverbs
    for p in culture_data.get("proverbs", []):
        alpaca_records.append({
            "instruction": "اشرح معنى المثل الشعبي الجزائري التالي ومناسبته ودلالته الاجتماعية بالدارجة الجزائرية:",
            "input": f"المثل: {p['text']}",
            "output": f"المعنى الشعبي للمثل: {p['meaning']} (المجال: {p['category']})",
            "region": p.get("region", "GENERAL"),
            "intent": "CULTURAL_WISDOM"
        })

    # Gastronomy
    for f_item in culture_data.get("gastronomy", []):
        alpaca_records.append({
            "instruction": "عرف بهذا الطبق أو الحلوى الجزائرية التقليدية مع ذكر أصلها ومناسبتها:",
            "input": f"الأكلة: {f_item['name']}",
            "output": f"{f_item['name']} طبق أصيل من منطقة ({f_item['origin']}). الوصف: {f_item['description']}",
            "region": f_item.get("origin", "GENERAL"),
            "intent": "CULTURAL_FOOD"
        })

    # Landmarks
    for lmk in culture_data.get("landmarks", []):
        alpaca_records.append({
            "instruction": "قدم نبذة سياحية وتاريخية مختصرة عن هذا المعلم أو السوق الجزائري الشهير:",
            "input": f"المعلم: {lmk['name']} ({lmk['city']})",
            "output": f"{lmk['name']} يقع في {lmk['city']} (ولاية {lmk['wilaya_code']}). {lmk['description']}",
            "region": "GENERAL",
            "intent": "CULTURAL_LANDMARK"
        })

    # Memes & Slang
    for m in culture_data.get("memes_and_trends", []):
        alpaca_records.append({
            "instruction": "اشرح هذا الميم أو التريند المتداول في الجزائر بالدارجة:",
            "input": f"العبارة: '{m['phrase']}'",
            "output": f"المعنى: {m['meaning']} | السياق الشعبي: {m['context']}",
            "region": "GENERAL",
            "intent": "CULTURAL_MEME"
        })

    with open(export_dir / "alpaca_darja.json", "w", encoding="utf-8") as f:
        json.dump(alpaca_records, f, ensure_ascii=False, indent=2)

    # 2. ShareGPT Format
    sharegpt_records = []
    idx = 1
    for rec in alpaca_records:
        system_content = "أنت مساعد ذكاء اصطناعي جزائري خبير بالدارجة وثقافة وتجارة الجزائر 100%."
        sharegpt_records.append({
            "id": f"dz_train_{idx:04d}",
            "conversations": [
                {"from": "system", "value": system_content},
                {"from": "human", "value": f"{rec['instruction']}\n\n{rec['input']}" if rec['input'] else rec['instruction']},
                {"from": "gpt", "value": rec["output"]}
            ]
        })
        idx += 1

    with open(export_dir / "sharegpt_darja.json", "w", encoding="utf-8") as f:
        json.dump(sharegpt_records, f, ensure_ascii=False, indent=2)

    # 3. OpenAI Chat JSONL
    openai_path = export_dir / "openai_finetune_darja.jsonl"
    with open(openai_path, "w", encoding="utf-8") as f:
        for rec in sharegpt_records:
            convs = rec["conversations"]
            line = {
                "messages": [
                    {"role": convs[0]["from"], "content": convs[0]["value"]},
                    {"role": "user" if convs[1]["from"] == "human" else convs[1]["from"], "content": convs[1]["value"]},
                    {"role": "assistant" if convs[2]["from"] == "gpt" else convs[2]["from"], "content": convs[2]["value"]}
                ]
            }
            f.write(json.dumps(line, ensure_ascii=False) + "\n")

    print(f"[EXPORT] Successfully generated fine-tuning datasets in {export_dir.relative_to(root)}:")
    print(f"  - alpaca_darja.json ({len(alpaca_records)} samples)")
    print(f"  - sharegpt_darja.json ({len(sharegpt_records)} samples)")
    print(f"  - openai_finetune_darja.jsonl ({len(sharegpt_records)} lines)")


if __name__ == "__main__":
    main()
