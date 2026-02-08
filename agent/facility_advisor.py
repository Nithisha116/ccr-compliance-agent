import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

# --------------------------------------------------
# Disclaimer (PDF explicitly requires this)
# --------------------------------------------------

DISCLAIMER = (
    "\n⚠️ Disclaimer: This information is for educational purposes only and "
    "does not constitute legal advice. Please consult a qualified attorney "
    "or compliance professional for official guidance.\n"
)

# --------------------------------------------------
# Facility rules & intent (engineering reasoning)
# --------------------------------------------------

FACILITY_RULES = {
    "restaurant": {
        "allowed_titles": [
            "Public Health",
            "Food",
            "Agriculture",
            "Alcoholic Beverage",
            "Labor",
            "Occupational Safety",
            "Health"
        ],
        "keywords": [
            "food", "restaurant", "sanitation", "hygiene", "kitchen",
            "employee", "health", "permit", "alcohol", "beverage",
            "refrigeration", "inspection"
        ],
        "follow_up_questions": [
            "Do you prepare food on-site?",
            "Do you serve alcohol?",
            "How many employees work at the facility?",
            "Is food stored or refrigerated on the premises?"
        ]
    },
    "farm": {
        "allowed_titles": [
            "Food",
            "Agriculture",
            "Environmental Protection",
            "Labor",
            "Pesticide"
        ],
        "keywords": [
            "farm", "agriculture", "pesticide",
            "fertilizer", "livestock", "worker", "environment"
        ],
        "follow_up_questions": [
            "Do you use pesticides or fertilizers?",
            "Do you employ seasonal or migrant workers?",
            "Do you raise livestock?"
        ]
    },
    "movie theater": {
        "allowed_titles": [
            "Public Safety",
            "Fire",
            "Building Standards",
            "Labor"
        ],
        "keywords": [
            "theater", "public assembly", "fire safety",
            "occupancy", "emergency", "employee"
        ],
        "follow_up_questions": [
            "What is the seating capacity?",
            "Do you sell food or beverages?",
            "Do you employ security staff?"
        ]
    }
}

# --------------------------------------------------
# Relevance scoring (THIS is the key fix)
# --------------------------------------------------

def relevance_score(section, facility_type):
    rules = FACILITY_RULES[facility_type]

    title = (section.get("title_name") or "").lower()
    content = (section.get("content_markdown") or "").lower()

    score = 0

    # Strong signal: correct regulatory domain
    for allowed in rules["allowed_titles"]:
        if allowed.lower() in title:
            score += 3

    # Medium signal: operational keywords
    for kw in rules["keywords"]:
        if kw in content:
            score += 2

    # Penalize clearly irrelevant domains
    if any(bad in title for bad in ["investment", "finance", "securities"]):
        score -= 3

    return score

# --------------------------------------------------
# Human-readable explanation (mentor-facing)
# --------------------------------------------------

def explain_relevance(section, facility_type):
    title = section.get("title_name") or "this CCR title"
    section_no = section.get("section_number") or "an unnumbered section"

    return (
        f"This section applies because {facility_type}s are regulated under "
        f"{title}. Section {section_no} contains provisions that may affect "
        f"operational, safety, or compliance requirements for this type of facility."
    )

# --------------------------------------------------
# Main RAG agent
# --------------------------------------------------

def main():
    # Load vector database
    client = chromadb.PersistentClient(path="data/chroma_db")
    collection = client.get_collection("ccr_sections")

    # Load embedding model
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Input validation loop
    facility_type = ""
    while facility_type not in FACILITY_RULES:
        facility_type = input(
            "Enter facility type (restaurant, farm, movie theater): "
        ).strip().lower()

        if facility_type not in FACILITY_RULES:
            print("❌ Invalid input. Please choose a supported facility type.\n")

    # Embed query (intentionally broad)
    query_embedding = model.encode(facility_type).tolist()

    # Retrieve candidate sections
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=25
    )

    print(f"\n📋 Applicable CCR Sections for {facility_type.capitalize()}:\n")

    scored_sections = []

    for metadata, document in zip(
        results["metadatas"][0],
        results["documents"][0]
    ):
        section = {
            **metadata,
            "content_markdown": document
        }

        score = relevance_score(section, facility_type)
        if score > 0:
            scored_sections.append((score, section))

    # Sort by relevance score
    scored_sections.sort(key=lambda x: x[0], reverse=True)

    shown = 0

    for _, section in scored_sections:
        citation = section.get("citation") or "CCR § (see source)"
        breadcrumb = section.get("breadcrumb_path") or "CCR hierarchy unavailable"
        source = section.get("source_url") or "Source unavailable"

        print(f"📘 {citation}")
        print(f"🧭 Path: {breadcrumb}")
        print(f"🧠 Why it applies: {explain_relevance(section, facility_type)}")
        print(f"🔗 Source: {source}\n")

        shown += 1
        if shown >= 5:
            break

    if shown == 0:
        print("⚠️ No strongly relevant sections found with current information.\n")

    # Follow-up questions (PDF requirement)
    print("❓ Follow-up questions to refine compliance guidance:")
    for q in FACILITY_RULES[facility_type]["follow_up_questions"]:
        print(f"  - {q}")

    print(DISCLAIMER)

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------

if __name__ == "__main__":
    main()
