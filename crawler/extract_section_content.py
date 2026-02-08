import json
import re
from pathlib import Path
from datetime import datetime

from crawl4ai import AsyncWebCrawler
import asyncio

INPUT_FILE = Path("data/section_urls.txt")
OUTPUT_FILE = Path("data/sections_content.jsonl")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def extract_section_data(markdown: str):
    title_match = re.search(r"#\s*(Section\s+\d+[\w\.\-]*)", markdown, re.IGNORECASE)
    section_title = title_match.group(1) if title_match else "Unknown Section"

    # remove nav junk
    text_lines = [
        line.strip()
        for line in markdown.splitlines()
        if len(line.strip()) > 40
    ]

    section_text = "\n".join(text_lines)

    return section_title, section_text


async def main():
    urls = INPUT_FILE.read_text().splitlines()

    async with AsyncWebCrawler(verbose=False) as crawler:
        for url in urls:
            print(f"Extracting: {url}")

            result = await crawler.arun(url=url)

            title, content = extract_section_data(result.markdown or "")

            record = {
                "url": url,
                "section_title": title,
                "content": content,
                "extracted_at": datetime.utcnow().isoformat()
            }

            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
