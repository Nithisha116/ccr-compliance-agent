import json
import re
import asyncio
from pathlib import Path
from crawl4ai import AsyncWebCrawler

INPUT_FILE = "data/all_discovered_urls.jsonl"
OUTPUT_FILE = "data/section_page_urls.txt"

SECTION_URL_PATTERN = re.compile(r"/calregs/Document/")

async def main():
    urls = set()

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            url = record.get("url", "")
            if SECTION_URL_PATTERN.search(url):
                urls.add(url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for u in sorted(urls):
            f.write(u + "\n")

    print(f"✅ Extracted {len(urls)} section page URLs")

if __name__ == "__main__":
    asyncio.run(main())
