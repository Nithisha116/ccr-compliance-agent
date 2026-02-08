import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

DATA_FILE = Path("data/ccr_sections_enriched.jsonl")
CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "ccr_sections"

def safe(value):
    """Ensure ChromaDB-compatible metadata values"""
    return str(value) if value is not None else ""

def main():
    # Persistent Chroma client
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Idempotent collection creation
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    documents = []
    metadatas = []
    ids = []

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            record = json.loads(line)

            documents.append(record["content_markdown"])

            metadatas.append({
                "title_number": safe(record.get("title_number")),
                "title_name": safe(record.get("title_name")),
                "division": safe(record.get("division")),
                "chapter": safe(record.get("chapter")),
                "article": safe(record.get("article")),
                "section_number": safe(record.get("section_number")),
                "section_name": safe(record.get("section_name")),
                "citation": safe(record.get("citation")),
                "breadcrumb_path": safe(record.get("breadcrumb_path")),
                "source_url": safe(record.get("source_url")),
                "retrieved_at": safe(record.get("retrieved_at")),
            })

            ids.append(f"ccr_{i}")

    print(f"🔢 Embedding {len(documents)} enriched CCR sections...")

    # Idempotent re-indexing
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print("✅ CCR sections embedded from enriched dataset and persisted to disk")

if __name__ == "__main__":
    main()
