import json
import re
from pathlib import Path

INPUT_FILE = "data/all_discovered_urls.jsonl"
OUTPUT_FILE = "data/ccr_sections_structured.jsonl"

def extract_section_info(markdown: str):
    section = "Unknown"
    section_name = "Unknown"

    # Try to find section number like §12345
    match = re.search(r"§\s*\d+[.\d]*", markdown)
    if match:
        section = match.group().strip()

    # Try to find a heading line
    lines = markdown.splitlines()
    for line in lines[:10]:
        if section in line:
            section_name = line.strip()
            break

    return section, section_name


def main():
    input_path = Path(INPUT_FILE)
    output_path = Path(OUTPUT_FILE)

    if not input_path.exists():
        print("❌ Input file not found:", INPUT_FILE)
        return

    count = 0

    with input_path.open("r", encoding="utf-8") as infile, \
         output_path.open("w", encoding="utf-8") as outfile:

        for line in infile:
            record = json.loads(line)

            markdown = record.get("markdown", "")
            url = record.get("url", "")

            if not markdown:
                continue

            section, section_name = extract_section_info(markdown)

            structured = {
                "title": "Unknown",
                "division": "Unknown",
                "chapter": "Unknown",
                "section": section,
                "section_name": section_name,
                "url": url,
                "markdown": markdown
            }

            outfile.write(json.dumps(structured, ensure_ascii=False) + "\n")
            count += 1

    print(f"✅ Structured CCR sections saved: {count}")


if __name__ == "__main__":
    main()
