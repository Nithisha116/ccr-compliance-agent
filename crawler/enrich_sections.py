import json
from pathlib import Path
from datetime import datetime

INPUT_FILE = Path("data/ccr_sections_clean.jsonl")
OUTPUT_FILE = Path("data/ccr_sections_enriched.jsonl")

def build_citation(record):
    title = record.get("title_number") or "Unknown"
    section = record.get("section_number") or "Unknown"
    return f"{title} CCR § {section}"

def build_breadcrumb(record):
    parts = []

    if record.get("title_number"):
        title_name = record.get("title_name") or ""
        parts.append(f"Title {record['title_number']} {f'({title_name})' if title_name else ''}")

    if record.get("division"):
        parts.append(f"Division {record['division']}")

    if record.get("chapter"):
        parts.append(f"Chapter {record['chapter']}")

    if record.get("article"):
        parts.append(f"Article {record['article']}")

    if record.get("section_number"):
        section_name = record.get("section_name") or ""
        parts.append(f"Section {record['section_number']} {f'– {section_name}' if section_name else ''}")
    else:
        parts.append("Section Unknown")

    return " → ".join(parts)

def main():
    enriched_count = 0

    with INPUT_FILE.open("r", encoding="utf-8") as infile, \
         OUTPUT_FILE.open("w", encoding="utf-8") as outfile:

        for line in infile:
            record = json.loads(line)

            record["citation"] = build_citation(record)
            record["breadcrumb_path"] = build_breadcrumb(record)
            record["retrieved_at"] = datetime.utcnow().isoformat() + "Z"

            outfile.write(json.dumps(record, ensure_ascii=False) + "\n")
            enriched_count += 1

    print(f"✅ Enriched {enriched_count} CCR sections")
    print(f"📁 Output saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
