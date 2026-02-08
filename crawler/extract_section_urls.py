import json
import re

INPUT_FILE = "data/all_discovered_urls.jsonl"
OUTPUT_FILE = "data/section_urls.txt"

section_urls = set()

# regex for Westlaw CCR document pages
DOC_PATTERN = re.compile(r"https://govt\.westlaw\.com/calregs/Document/[A-Z0-9]+")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        # 1️⃣ direct URL
        url = record.get("url", "")
        if "/calregs/Document/" in url:
            section_urls.add(url)

        # 2️⃣ markdown content
        markdown = record.get("markdown", "")
        if markdown:
            matches = DOC_PATTERN.findall(markdown)
            section_urls.update(matches)

        # 3️⃣ cleaned HTML
        html = record.get("cleaned_html", "")
        if html:
            matches = DOC_PATTERN.findall(html)
            section_urls.update(matches)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for url in sorted(section_urls):
        f.write(url + "\n")

print(f"Extracted {len(section_urls)} section URLs")
print(f"Saved to {OUTPUT_FILE}")
