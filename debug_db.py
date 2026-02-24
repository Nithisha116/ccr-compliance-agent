import chromadb

client = chromadb.PersistentClient(path="./data/chroma_db")
collection = client.get_collection("ccr_sections")

data = collection.get(include=["metadatas"])
citations = [m.get("citation") for m in data["metadatas"]]

print("\nTotal sections in DB:", len(citations))

print("\nSample citations:")
for c in citations[:60]:
    print("-", c)

print("\nCheck for 21905:")
print(any("21905" in str(c) for c in citations))