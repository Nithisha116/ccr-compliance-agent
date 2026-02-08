import asyncio
import json
from datetime import datetime
from pathlib import Path

from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup

START_URLS = [
    "https://govt.westlaw.com/calregs"
]

OUTPUT_FILE = Path("data/all_discovered_urls.jsonl")
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

visited = set()
MAX_PAGES = 50   # keep reasonable for internship


def extract_links(html: str):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # only CCR links
        if href.startswith("/calregs"):
            links.add("https://govt.westlaw.com" + href)

    return links


async def main():
    async with AsyncWebCrawler(verbose=True) as crawler:
        queue = list(START_URLS)

        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue

            print(f"\nCrawling: {url}")
            visited.add(url)

            try:
                result = await crawler.arun(url=url)
            except Exception as e:
                print(f"❌ Failed: {e}")
                continue

            record = {
                "url": url,
                "crawled_at": datetime.utcnow().isoformat(),
                "html": result.html or "",
                "markdown": result.markdown or "",
            }

            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")

            # 🔥 MANUAL LINK EXTRACTION
            new_links = extract_links(record["html"])
            for link in new_links:
                if link not in visited:
                    queue.append(link)

        print("\nCrawl finished")
        print(f"Visited {len(visited)} pages")


if __name__ == "__main__":
    asyncio.run(main())
