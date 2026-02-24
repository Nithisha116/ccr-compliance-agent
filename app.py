import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

# -------------------------------------------------------
# 1. Page Configuration & Styling
# -------------------------------------------------------

load_dotenv()
st.set_page_config(page_title="CCR Advisor", page_icon="⚖️", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { font-size: 2.4rem; font-weight: 700; color: #1E3A8A; text-align: center; }
    .subtitle { text-align: center; color: #64748b; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚖️ CCR Advisor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">California Regulatory Compliance Assistant (Offline RAG Prototype)</div>', unsafe_allow_html=True)

# -------------------------------------------------------
# 2. Session State
# -------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------------------------------
# 3. Sidebar
# -------------------------------------------------------

with st.sidebar:
    st.header("About")
    st.info(
        "This assistant uses Retrieval-Augmented Retrieval (RAG) "
        "to fetch California Code of Regulations (CCR) sections "
        "from a locally indexed vector database."
    )

    st.warning(
        "⚠️ Disclaimer: This system provides educational guidance "
        "only and does not constitute legal advice."
    )

    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# -------------------------------------------------------
# 4. Backend Initialization (Fully Local)
# -------------------------------------------------------

@st.cache_resource
def init_backend():
    client = chromadb.PersistentClient(path="./data/chroma_db")
    collection = client.get_collection(name="ccr_sections")
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return collection, embedding_model

try:
    collection, embedding_model = init_backend()
except Exception as e:
    st.error(f"Initialization Error: {e}")
    st.stop()

# -------------------------------------------------------
# 5. Render Chat History
# -------------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------------------------------------------------------
# 6. Chat Logic (Offline RAG Mode)
# -------------------------------------------------------

if prompt := st.chat_input("Ex: What regulations apply to a restaurant?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Retrieving relevant CCR sections…"):

        query_embedding = embedding_model.encode(prompt).tolist()

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5,
            include=["documents", "metadatas"]
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        context_blocks = []
        citation_links = []

        for doc, meta in zip(documents, metadatas):
            citation = meta.get("citation", "Unknown CCR Section")
            url = meta.get("source_url", "#")

            context_blocks.append(f"📘 CCR {citation}\n{doc}")
            citation_links.append(f"- {citation}")

        context_text = "\n\n".join(context_blocks)

        # Deterministic offline reasoning
        if context_blocks:
            assistant_text = f"""
### 📋 Retrieved CCR Context

The following CCR sections were retrieved based on semantic similarity to your question:

{context_text}

### 🧠 Interpretation

These sections may contain provisions relevant to your query.  
For precise applicability, additional facility-specific details may be required.

### ❓ Suggested Follow-up

- Can you clarify the facility type?
- Are you asking about licensing, safety, or employee regulations?

---

**Referenced CCR Sections:**
{chr(10).join(citation_links)}

⚠️ Disclaimer: Educational use only. Not legal advice.
"""
        else:
            assistant_text = """
⚠️ No relevant CCR sections were found for your query.

💡 This is expected with partial dataset coverage.
💡 Expanding domain-focused crawling improves accuracy.

⚠️ Disclaimer: Educational use only. Not legal advice.
"""

    with st.chat_message("assistant"):
        st.markdown(assistant_text)

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_text}
    )