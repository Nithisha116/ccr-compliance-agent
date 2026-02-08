from bs4 import BeautifulSoup
import json

INPUT_FILE = "data/all_discovered_urls.jsonl"
OUTPUT_FILE = "data/section_references.jsonl"


def extract_section_refs_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    sections = []

    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        if text.startswith("§"):
            sections.append(text)

    return sections


def main():
    count = 0

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:

        for line in infile:
            record = json.loads(line)
            url = record["url"]

            # Only Article / Chapter pages contain section lists
            if record["type"] in ("article", "chapter"):
                html = record.get("html", "")
                if not html:
                    continue

                sections = extract_section_refs_from_html(html)
                for sec in sections:
                    outfile.write(json.dumps({
                        "parent_url": url,
                        "section_ref": sec
                    }) + "\n")
                    count += 1

    print(f"Extracted {count} section references")


if __name__ == "__main__":
    main()
