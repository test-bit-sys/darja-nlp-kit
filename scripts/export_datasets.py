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
    export_dir = root / "data" / "fine_tuning"
    export_dir.mkdir(parents=True, exist_ok=True)

    with open(dialogues_path, "r", encoding="utf-8") as f:
        dialogues = json.load(f)

    # 1. Alpaca Format
    alpaca_records = []
    for d in dialogues:
        alpaca_records.append({
            "instruction": f"أنت تاجر وممثل خدمة عملاء جزائري محترف. رد على رسالة الزبون بدارجة جزائرية واقعية وطبيعية 100% تطابق لهجة منطقته ({d['region']}) ونبرة المتجر الودية.",
            "input": d["customer_message"],
            "output": d["merchant_response"],
            "region": d["region"],
            "intent": d["intent"]
        })

    with open(export_dir / "alpaca_darja.json", "w", encoding="utf-8") as f:
        json.dump(alpaca_records, f, ensure_ascii=False, indent=2)

    # 2. ShareGPT Format
    sharegpt_records = []
    for d in dialogues:
        system_content = f"أنت تاجر ومساعد متجر إلكتروني جزائري. تحدث بدارجة جزائرية أصيلة تناسب لهجة الزبون ({d['region']})."
        sharegpt_records.append({
            "id": d["id"],
            "conversations": [
                {"from": "system", "value": system_content},
                {"from": "human", "value": d["customer_message"]},
                {"from": "gpt", "value": d["merchant_response"]}
            ]
        })

    with open(export_dir / "sharegpt_darja.json", "w", encoding="utf-8") as f:
        json.dump(sharegpt_records, f, ensure_ascii=False, indent=2)

    # 3. OpenAI Chat JSONL
    openai_path = export_dir / "openai_finetune_darja.jsonl"
    with open(openai_path, "w", encoding="utf-8") as f:
        for d in dialogues:
            line = {
                "messages": [
                    {
                        "role": "system",
                        "content": f"أنت مساعد خدمة عملاء ذكي وبشري لمتجر إلكتروني جزائري. تحدث بدارجة جزائرية عفوية وطبيعية ({d['region']})."
                    },
                    {
                        "role": "user",
                        "content": d["customer_message"]
                    },
                    {
                        "role": "assistant",
                        "content": d["merchant_response"]
                    }
                ]
            }
            f.write(json.dumps(line, ensure_ascii=False) + "\n")

    print(f"[EXPORT] Successfully generated fine-tuning datasets in {export_dir.relative_to(root)}:")
    print(f"  - alpaca_darja.json ({len(alpaca_records)} samples)")
    print(f"  - sharegpt_darja.json ({len(sharegpt_records)} samples)")
    print(f"  - openai_finetune_darja.jsonl ({len(dialogues)} lines)")


if __name__ == "__main__":
    main()
