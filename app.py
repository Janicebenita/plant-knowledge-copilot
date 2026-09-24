from pathlib import Path

from dotenv import load_dotenv
import streamlit as st

from plant_copilot.answering import GroqCompletionClient, answer_question
from plant_copilot.config import Settings
from plant_copilot.history import ConversationHistory
from plant_copilot.knowledge import KnowledgeBase

load_dotenv()
st.set_page_config(page_title="Plant Knowledge Copilot", page_icon="🏭", layout="wide")
st.title("🏭 Plant Knowledge Copilot")
st.caption("Evidence-grounded answers for plant documents — not a substitute for verified industrial guidance.")
st.warning("Demo records included with this project are SYNTHETIC. Validate all procedures with authorized plant documentation and personnel.")

settings = Settings()
settings.validate()

@st.cache_resource
def resources():
    kb = KnowledgeBase(settings.chroma_path, settings.collection, settings.embedding_model)
    try:
        history = ConversationHistory()
    except Exception as exc:
        st.warning(f"MongoDB unavailable; using session-only history: {exc}")
        history = None
    return kb, history

kb, history = resources()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = ConversationHistory.new_id()

with st.sidebar:
    st.header("Knowledge base")
    st.caption(f"Embedding: `{settings.embedding_model}` · cosine · collection `{settings.collection}`")
    uploads = st.file_uploader("Upload documents", type=["txt", "md", "pdf", "docx", "html", "htm"], accept_multiple_files=True)
    size = st.number_input("Chunk size (characters)", min_value=100, value=settings.chunk_size, step=50)
    overlap = st.number_input("Overlap (characters)", min_value=0, max_value=int(size)-1, value=min(settings.chunk_overlap, int(size)-1), step=10)
    if st.button("Index documents", type="primary", disabled=not uploads):
        for item in uploads:
            try:
                result = kb.ingest(item.name, item.getvalue(), int(size), int(overlap))
                st.success(f"{item.name}: {result['status']} ({result['chunks']} chunks)")
            except Exception as exc:
                st.error(f"{item.name}: {exc}")
    if st.button("Index bundled synthetic examples"):
        indexed = 0
        for path in sorted(Path("demo_data").glob("SYNTHETIC_*")):
            try:
                result = kb.ingest(path.name, path.read_bytes(), int(size), int(overlap))
                indexed += result["chunks"]
            except Exception as exc:
                st.error(f"{path.name}: {exc}")
        st.success(f"Processed bundled SYNTHETIC examples ({indexed} chunks present).")
    st.metric("Indexed chunks", kb.collection.count())
    st.divider()
    durable = history is not None and history.durable
    st.info("Conversation history: MongoDB (durable)" if durable else "Conversation history: this browser session only")
    if st.button("New conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = ConversationHistory.new_id()
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Ask a question about indexed plant documents"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            hits = kb.search(question, settings.top_k, settings.threshold)
            client = GroqCompletionClient() if hits else None
            response = answer_question(question, hits, client, settings.groq_model)
            st.markdown(response.text)
            for i, hit in enumerate(response.hits, 1):
                page = f", page {hit.page}" if hit.page else ""
                with st.expander(f"[{i}] {hit.source}{page} · relevance {hit.score:.2f}"):
                    st.write(hit.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            if history:
                history.save(st.session_state.conversation_id, "user", question)
                history.save(st.session_state.conversation_id, "assistant", response.text)
        except Exception as exc:
            st.error(str(exc))
