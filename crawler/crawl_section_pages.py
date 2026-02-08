import asyncio
import json
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

SECTION_URLS_FILE = "data/section_urls.txt"
OUTPUT_FILE = "data/sections_content.jsonl"

def load_valid_urls(path):
    urls = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("http"):
            urls.append(line)
    return urls

async def main():
    urls = load_valid_urls(SECTION_URLS_FILE)
    print(f"🔍 Valid section URLs: {len(urls)}")
    print("First 5 URLs:")
    for u in urls[:5]:
        print(" -", u)

    crawler = AsyncWebCrawler(max_concurrency=1)
    config = CrawlerRunConfig(wait_until="networkidle")

    success = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for url in urls:
            try:
                results = await crawler.arun(url, config=config)
                page = results[0]

                if not page.success:
                    print(f"⚠️ Failed: {url}")
                    continue

                record = {
                    "url": page.url,
                    "html": page.html,
                    "markdown": page.markdown
                }

                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                success += 1
                print(f"✅ Crawled: {url}")

            except Exception as e:
                print(f"❌ Error crawling {url}: {e}")

    print(f"\n🎉 Finished. Successfully crawled {success} section pages.")
if __name__ == "__main__":
    asyncio.run(main())
