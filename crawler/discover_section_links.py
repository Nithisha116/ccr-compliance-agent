import asyncio
import re
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from bs4 import BeautifulSoup

START_URL = "https://govt.westlaw.com/calregs/Browse/Home/California/CaliforniaCodeofRegulations"
OUTPUT_FILE = Path("data/section_urls.txt")
MAX_SECTIONS = 200

SECTION_PATTERN = re.compile(r"/calregs/Document/")

async def main():
    crawler = AsyncWebCrawler()
    config = CrawlerRunConfig(
        wait_until="networkidle",
        page_timeout=30000
    )
                                                                                                                                      
    discovered = set()
    visited = set()
    to_visit = [START_URL]

    while to_visit and len(discovered) < MAX_SECTIONS:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            result = await crawler.arun(url, config=config)
        except Exception as e:
            print(f"❌ Failed: {url} → {e}")
            continue

        if not result or not result.html:
            continue

        soup = BeautifulSoup(result.html, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]

            # Normalize relative URLs
            if href.startswith("/"):
                href = "https://govt.westlaw.com" + href

            # Section pages
            if SECTION_PATTERN.search(href):
                discovered.add(href)
                if len(discovered) >= MAX_SECTIONS:
                    break

            # Browse deeper
            if "/Browse/" in href and href not in visited:
                to_visit.append(href)

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for url in sorted(discovered):
            f.write(url + "\n")

    print(f"✅ Discovered {len(discovered)} CCR section URLs")

if __name__ == "__main__":
    asyncio.run(main())
