from crawl4ai import AsyncWebCrawler
import asyncio
import json
from datetime import datetime

START_URL = "https://govt.westlaw.com/calregs"
OUTPUT_FILE = "data/discovered_urls.jsonl"

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(START_URL)
        page = result[0]

        links = page.links or []

        print(f"Discovered {len(links)} links")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for link in links:
                record = {
                    "url": link,
                    "discovered_at": datetime.utcnow().isoformat(),
                    "source_url": START_URL
                }
                f.write(json.dumps(record) + "\n")


        print(f"Saved links to {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
