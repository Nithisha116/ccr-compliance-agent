import json
import re
from pathlib import Path
from datetime import datetime

INPUT_FILE = Path("data/sections_content.jsonl")
OUTPUT_FILE = Path("data/ccr_sections_clean.jsonl")

SECTION_REGEX = re.compile(
    r"§\s*(\d+(?:\.\d+)*)\.?\s*([A-Z][^\n]+)",
    re.IGNORECASE
)

TITLE_REGEX = re.compile(
    r"Title\s+(\d+)\.\s*([A-Za-z &]+)"
)

def extract_section(markdown: str):
    """
    Extract section number and name from markdown.
    """
    match = SECTION_REGEX.search(markdown)
    if match:
        return match.group(1), match.group(2).strip()
    return None, None

def extract_title(markdown: str):
    match = TITLE_REGEX.search(markdown)
    if match:
        return match.group(1), match.group(2).strip()
    return None, None

def main():
    count = 0

    with open(INPUT_FILE, encoding="utf-8", errors="ignore") as f_in, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:

        for line in f_in:
            raw = json.loads(line)
            markdown = raw.get("markdown", "")

            title_number, title_name = extract_title(markdown)
            section_number, section_name = extract_section(markdown)

            record = {
                "title_number": title_number,
                "title_name": title_name,
                "division": None,
                "chapter": None,
                "article": None,
                "section_number": section_number,
                "section_name": section_name,
                "source_url": raw.get("url"),
                "content_markdown": markdown,
                "retrieved_at": datetime.utcnow().isoformat()
            }

            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    print(f"✅ Canonical CCR sections saved ({count})")

if __name__ == "__main__":
    main()
