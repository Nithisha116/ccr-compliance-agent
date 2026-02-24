import chromadb 
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# Disclaimer (Required for compliance / PDF spec)
# --------------------------------------------------

DISCLAIMER = (
    "\n⚠️ Disclaimer: This information is for educational purposes only and "
    "does not constitute legal advice. Please consult a qualified attorney "
    "or compliance professional for official guidance.\n"
)

# --------------------------------------------------
# Facility rules & reasoning model
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
        ],
        "irrelevant_titles": [
            "investment",
            "finance",
            "securities",
            "motor vehicles",
            "student loan",
            "tax"
        ]
    },

    "farm": {
        "allowed_titles": [
            "Food",
            "Agriculture",
            "Environmental",
            "Pesticide",
            "Labor"
        ],
        "keywords": [
            "farm", "agriculture", "pesticide",
            "fertilizer", "livestock", "worker", "environment"
        ],
        "follow_up_questions": [
            "Do you use pesticides or fertilizers?",
            "Do you employ seasonal or migrant workers?",
            "Do you raise livestock?"
        ],
        "irrelevant_titles": [
            "investment",
            "finance",
            "securities",
            "motor vehicles"
        ]
    },

    "movie theater": {
        "allowed_titles": [
            "Public Safety",
            "Fire",
            "Building",
            "Labor"
        ],
        "keywords": [
            "theater", "public assembly", "fire",
            "occupancy", "emergency", "exit", "employee"
        ],
        "follow_up_questions": [
            "What is the seating capacity?",
            "Do you sell food or beverages?",
            "Do you employ security staff?"
        ],
        "irrelevant_titles": [
            "investment",
            "finance",
            "agriculture"
        ]
    }
}

# --------------------------------------------------
# Relevance scoring engine
# --------------------------------------------------

def relevance_score(section, facility_type):
    rules = FACILITY_RULES[facility_type]

    title = (section.get("title_name") or "").lower()
    content = (section.get("content_markdown") or "").lower()

    score = 0

    # Hard rejection of clearly irrelevant domains
    if any(bad in title for bad in rules["irrelevant_titles"]):
        return -1

    # Strong domain alignment
    for allowed in rules["allowed_titles"]:
        if allowed.lower() in title:
            score += 3

    # Operational signals
    for kw in rules["keywords"]:
        if kw in content:
            score += 2

    return score

# --------------------------------------------------
# Explanation generator
# --------------------------------------------------

def explain_relevance(section, facility_type):
    title = section.get("title_name") or "this CCR title"
    section_no = section.get("section_number") or "an unnumbered section"

    return (
        f"This section is considered relevant because {facility_type}s commonly "
        f"operate under regulatory domains related to {title}. Section {section_no} "
        f"contains provisions that may influence operational, safety, or compliance "
        f"obligations for this facility type."
    )

# --------------------------------------------------
# Main RAG Agent
# --------------------------------------------------

def main():
    client = chromadb.PersistentClient(path="data/chroma_db")
    collection = client.get_collection("ccr_sections")

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    facility_type = ""

    while facility_type not in FACILITY_RULES:
        facility_type = input(
            "Enter facility type (restaurant, farm, movie theater): "
        ).strip().lower()

        if facility_type not in FACILITY_RULES:
            print("❌ Unsupported facility type. Try again.\n")

    query_text = f"California regulations and compliance requirements for operating a {facility_type}"
    query_embedding = model.encode(query_text).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=30
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
        print("⚠️ No strongly relevant sections identified from current dataset.\n")

    print("❓ Follow-up questions to refine compliance guidance:")
    for q in FACILITY_RULES[facility_type]["follow_up_questions"]:
        print(f"  - {q}")

    print(DISCLAIMER)

# --------------------------------------------------
# Entrypoint
# --------------------------------------------------

if __name__ == "__main__":
    main()
