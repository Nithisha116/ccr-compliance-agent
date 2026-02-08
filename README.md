1.CCR Compliance Agent:
-An end-to-end compliance intelligence backend system that crawls the California Code of Regulations (CCR), structures regulatory data into a canonical hierarchy, indexes it in a vector database, and provides facility-specific compliance guidance using Retrieval-Augmented Generation (RAG).

2.Project Objective
Build a system that can:
-Crawl the California Code of Regulations (CCR).
-Extract individual regulation sections as clean Markdown.
-Organize data into a canonical CCR hierarchy.
-Index the data into a vector database.
-Provide facility-specific compliance guidance (e.g., restaurants, farms, movie theaters).

3.Architecture
CCR Website
   ↓
URL Discovery (Crawl4AI)
   ↓
Section Page Crawling
   ↓
Markdown Extraction
   ↓
Canonical Structuring
   ↓
Data Enrichment (citation, breadcrumbs, timestamps)
   ↓
Vector Database (ChromaDB)
   ↓
Compliance Advisor (RAG Agent via CLI)

-The compliance advisor is exposed via a CLI interface, representing how an API or frontend consumer would interact with the system.

4.Tech Stack

-Python 3.11
-Crawl4AI – robust async web crawling
-Sentence Transformers – semantic embeddings
-ChromaDB – vector database (local, free-tier)
-RAG (Retrieval-Augmented Generation) – compliance reasoning
-JSON / JSONL – structured data storage

5.Repository Structure
ccr-compliance-agent/
│
├── crawler/
│   ├── discover_section_links.py
│   ├── crawl_section_pages.py
│   ├── clean_sections.py
│   ├── enrich_sections.py
│
├── agent/
│   ├── vector_store.py
│   └── facility_advisor.py
│
├── data/
│   ├── section_urls.txt
│   ├── sections_content.jsonl
│   ├── ccr_sections_clean.jsonl
│   ├── ccr_sections_enriched.jsonl
│   ├── chroma_db/
│   ├── crawled_urls.txt
│   ├── failed_urls.txt
│   └── coverage_report.txt
│
└── README.md

6.Canonical Data Schema
Each CCR section is stored with the following fields (when available):
-title_number
-title_name
-division
-chapter
-article
-section_number
-section_name
-citation (e.g., 17 CCR § 113700)
-breadcrumb_path
-source_url
-content_markdown
-retrieved_at

7.Crawling Strategy & Coverage
-Uses Crawl4AI with controlled concurrency
Explicit separation of:
-URL discovery.
-Section page crawling.
-Content extraction.
Tracks:
-Successfully crawled URLs.
-Generates a coverage report.
Current dataset size:
-200 CCR sections.
-This prototype crawls 200 CCR sections to demonstrate completeness tracking and pipeline correctness.
Designed as a scalable prototype
-Easily extendable to thousands of sections.

8.Vector Database Design
-ChromaDB used as the vector database.
Stores:
-Section embeddings.
-Metadata (citations, hierarchy, URLs).
Supports:
-Semantic search.
-Metadata filtering.
-Safe re-indexing.

Why a vector DB?
-Legal questions are semantic, not keyword-based.
-Enables retrieval of relevant regulations even when wording differs.

Compliance Advisor (RAG Agent)
-Uses retrieval.
-Returns specific CCR sections.
-Explains why each section applies.
-Asks follow-up questions when information is insufficient.
-Always includes a “Not legal advice” disclaimer.

9.Example Questions Supported:
-What CCR sections apply to a restaurant in California?
-What regulations should a farm comply with?
-What laws affect movie theater operators?

10.How to Run (End-to-End)
Discover Section URLs-
python crawler/discover_section_links.py

Crawl Section Pages-
python crawler/crawl_section_pages.py

Clean & Structure Sections-
python crawler/clean_sections.py

Enrich Sections (citations)-
python crawler/enrich_sections.py

Index into Vector Database-
python agent/vector_store.py

Run Compliance Advisor-
python agent/facility_advisor.py

11.Known Limitations
-Dataset limited to 200 CCR sections (prototype scale).
-Some CCR pages lack explicit section numbers on source site.
-Legal interpretation is informational only.

12.Future Improvements
-Scale crawling to full CCR corpus.
-Add retry + exponential backoff reporting.
-Expose agent as a REST API.

13.Disclaimer
-This system provides educational and informational guidance only and does not constitute legal advice, Users should consult a qualified attorney or compliance professional for official guidance.
=======
# ccr-compliance-agent
Engineering internship assignment: Building a CCR Compliance Agent using Crawl4AI, vector databases, and LLMs.
>>>>>>> 98aab1cb257c94310fc2cd130798e7ca0361fbbf
