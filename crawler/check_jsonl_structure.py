import json
from pathlib import Path

FILE_PATH = Path("data/all_discovered_urls.jsonl")

keys_seen = set()
count = 0

with FILE_PATH.open("r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        obj = json.loads(line)
        keys_seen.update(obj.keys())
        count += 1
        if count == 5:
            break

print("Sampled records:", count)
print("Keys found:", keys_seen)
