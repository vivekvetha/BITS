import streamlit as st
import os
from dotenv import load_dotenv
from rag import RAGSystem
import json
from datetime import datetime
from config import CHROMADB_CONFIG, DOCUMENTS_FOLDER, RETRIEVAL_CONFIG

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="RAG Application",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom styling
st.markdown(
    """
    <style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "rag_system" not in st.session_state:
    st.session_state.rag_system = None
    st.session_state.search_history = []
    st.session_state.api_key = None
    st.session_state.last_sync_result = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "k_factor_slider" not in st.session_state:
    st.session_state.k_factor_slider = int(RETRIEVAL_CONFIG.get("default_k", 5))
if "rag_init_error" not in st.session_state:
    st.session_state.rag_init_error = None
if "reindex_pending" not in st.session_state:
    st.session_state.reindex_pending = False


def initialize_rag(force_reindex: bool = False, silent: bool = False) -> bool:
    """Initialize RAG system, load persisted Chroma, and ingest PDFs from Document folder when needed."""
    api_key = st.session_state.api_key or os.getenv("OPENAI_API_KEY")

    if not api_key:
        if not silent:
            st.error(
                "⚠️ OpenAI API Key not found. Set OPENAI_API_KEY or enter your key in the **sidebar** (arrow top-left)."
            )
        return False

    st.session_state.rag_init_error = None

    try:
        rag = RAGSystem(
            api_key=api_key,
            persist_directory=CHROMADB_CONFIG["persist_directory"],
        )
        sync = rag.connect_and_sync_documents_folder(
            documents_dir=DOCUMENTS_FOLDER,
            collection_name=CHROMADB_CONFIG["collection_name"],
            force_reindex=force_reindex,
        )
        st.session_state.rag_system = rag
        st.session_state.last_sync_result = sync
        return True
    except Exception as e:
        st.session_state.rag_init_error = str(e)
        st.session_state.rag_system = None
        if not silent:
            st.error(f"Error initializing RAG system: {str(e)}")
        return False


def ensure_rag_initialized() -> None:
    """Load RAG once on startup (and after refresh) when an API key is available."""
    if st.session_state.rag_system is not None:
        return
    initialize_rag(force_reindex=False, silent=True)


def render_retrieved_chunks_expander(retrieved_docs: list, *, expanded: bool = False):
    """Show retrieved chunks inside a Source expander (chat assistant bubble)."""
    with st.expander("Source", expanded=expanded):
        for doc in retrieved_docs:
            metadata = doc["metadata"]
            doc_name = (
                metadata.get("source", "Unknown")
                .replace("temp_", "")
                .replace("_", " ")
                .title()
            )
            page_num = metadata.get("page_number", "0")
            topic = metadata.get("topic", "No topic")
            with st.expander(
                f"📄 {doc_name} (Page {page_num}) — {topic[:50]}...",
                expanded=(doc["rank"] == 1),
            ):
                c1, c2 = st.columns([3, 1])
                with c1:
                    body = doc["content"]
                    st.write(body[:500] + "..." if len(body) > 500 else body)
                with c2:
                    st.metric("Relevance", f"{doc['similarity_score']:.0%}")
                if topic and topic.strip():
                    st.caption(f"Topic: {topic[:120]}")
                st.caption(f"Preview: {metadata.get('snippet', 'N/A')[:160]}")


def save_search_history(query: str, results_count: int, k_factor: int):
    """Save search to history"""
    search_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "k_factor": k_factor,
        "results_count": results_count,
    }
    st.session_state.search_history.insert(0, search_entry)
    # Keep only last 50 searches
    st.session_state.search_history = st.session_state.search_history[:50]


def render_settings_panel() -> None:
    """API key, retrieval, reindex, and query log (Streamlit left sidebar)."""
    st.header("⚙️ Configuration")

    api_key_input = st.text_input(
        "Enter OpenAI API Key",
        type="password",
        help="You can also set OPENAI_API_KEY environment variable",
    )

    if api_key_input:
        st.session_state.api_key = api_key_input
        st.session_state.rag_init_error = None

    st.slider(
        "K factor (chunks to retrieve)",
        min_value=int(RETRIEVAL_CONFIG["min_k"]),
        max_value=int(RETRIEVAL_CONFIG["max_k"]),
        step=1,
        key="k_factor_slider",
        help="How many document chunks to retrieve for each chat answer",
    )

    if st.button(
        "Reindex",
        width="stretch",
        type="primary",
        help=(
            "Deletes the Chroma collection and rebuilds embeddings from every PDF "
            "in the Document folder. Use after adding or changing PDFs."
        ),
    ):
        st.session_state.reindex_pending = True
        st.rerun()

    st.markdown("---")
    st.subheader("💬 Chat History")

    if st.button("Clear chat", width="stretch"):
        st.session_state.chat_messages = []
        st.rerun()

    if st.session_state.search_history:
        history_data = [
            {"Query": entry["query"]}
            for entry in st.session_state.search_history[:10]
        ]

        st.dataframe(history_data, width="stretch", hide_index=True)

        if st.button("🗑️ Clear query log", width="stretch"):
            st.session_state.search_history = []
            st.rerun()

        history_json = json.dumps(st.session_state.search_history, indent=2)
        st.download_button(
            label="⬇️ Export chat log",
            data=history_json,
            file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            width="stretch",
        )
    else:
        st.caption("No queries in the log yet. Send a message in the chat.")

    st.markdown("---")
    st.markdown("### 📚 Supported Features")
    st.markdown(
        """
    - **Startup**: Connects to Chroma and loads PDFs when an API key is set
    - **Reindex**: Rebuilds the vector store from the `Document` folder
    - **K factor**: Chunks to retrieve per reply (sidebar)
    - **Chat history**: Conversation reset and recent query log (sidebar)
    """
    )


def main():
    st.title("🤖 Finance Assistant")

    with st.sidebar:
        render_settings_panel()

    st.markdown("---")

    if st.session_state.reindex_pending:
        ok = False
        with st.status("Rebuilding document index…", expanded=True) as status:
            status.write(
                "Removing the old vector collection and re-embedding every PDF in "
                "your **Document** folder. This may take a minute."
            )
            ok = initialize_rag(force_reindex=True, silent=False)
            if ok:
                status.update(
                    label="Index rebuilt",
                    state="complete",
                    expanded=False,
                )
            else:
                status.update(
                    label="Reindex failed — check the error above",
                    state="error",
                    expanded=True,
                )
        st.session_state.reindex_pending = False
        if ok:
            res = st.session_state.last_sync_result
            if res:
                if res["status"] == "no_pdfs":
                    st.warning(res["message"])
                elif res["status"] == "ingested_with_errors" and res.get(
                    "pdfs_failed"
                ):
                    st.error("Failed: " + ", ".join(res["pdfs_failed"]))
            st.rerun()

    has_api_key = bool(
        st.session_state.api_key or os.getenv("OPENAI_API_KEY")
    )
    if st.session_state.rag_system is None and has_api_key:
        with st.status("Connecting to document index…", expanded=True) as status:
            status.write(
                "Loading Chroma and your PDFs (embeddings run only when the index is empty)."
            )
            ensure_rag_initialized()
            if st.session_state.rag_system:
                status.update(
                    label="Index ready — you can chat below",
                    state="complete",
                    expanded=False,
                )
            else:
                status.update(
                    label="Could not connect to the index",
                    state="error",
                    expanded=True,
                )

    # Main content — single summary for PDF path and index sync
    os.makedirs(DOCUMENTS_FOLDER, exist_ok=True)
    doc_dir = os.path.abspath(DOCUMENTS_FOLDER)
    res = st.session_state.last_sync_result

    if st.session_state.rag_init_error:
        sync_text = f"Could not connect: {st.session_state.rag_init_error}"
    elif st.session_state.rag_system and res and res.get("message"):
        sync_text = res["message"]
    elif not (st.session_state.api_key or os.getenv("OPENAI_API_KEY")):
        sync_text = (
            "Waiting for an API key. Open the **sidebar** (arrow top-left), paste your key, "
            "or set OPENAI_API_KEY; the app will connect automatically."
        )
    else:
        sync_text = "Connecting to the index… If this message stays, check your API key."

    info_body = (
        f"**PDF source:** `{doc_dir}` — on startup the app attaches to persisted Chroma "
        f"data and ingests PDFs only when the index is empty (unless you use **Reindex**).\n\n"
        f"**Last index sync:** {sync_text}"
    )
    st.info(info_body)

    st.markdown("---")

    # Chat: render history first, then handle new input (Streamlit chat pattern)
    k_factor = int(st.session_state.k_factor_slider)

    for i, msg in enumerate(st.session_state.chat_messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("retrieved_docs"):
                render_retrieved_chunks_expander(
                    msg["retrieved_docs"], expanded=False
                )
                wc = len(msg["content"].split())
                avg_score = sum(
                    d["similarity_score"] for d in msg["retrieved_docs"]
                ) / len(msg["retrieved_docs"])
                st.caption(
                    f"{len(msg['retrieved_docs'])} sources · ~{wc} words · "
                    f"avg relevance {avg_score:.0%}"
                )
                st.download_button(
                    label="Download this answer",
                    data=msg["content"],
                    file_name=f"answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    width="stretch",
                    key=f"chat_dl_{i}",
                )

    if prompt := st.chat_input("Ask something about your documents…"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        assistant_entry = None
        dl_key_idx = len(st.session_state.chat_messages)

        with st.chat_message("assistant"):
            if not st.session_state.rag_system:
                text = (
                    "The assistant is not connected yet. Set **OPENAI_API_KEY** or open "
                    "the **sidebar** (arrow top-left) and enter your key—the app loads the "
                    "RAG index automatically on startup. Use **Reindex** there after you "
                    "change PDFs in the Document folder."
                )
                st.markdown(text)
                assistant_entry = {
                    "role": "assistant",
                    "content": text,
                    "retrieved_docs": None,
                }
            else:
                try:
                    with st.spinner(f"Retrieving top {k_factor} chunks…"):
                        retrieved_docs = st.session_state.rag_system.retrieve(
                            prompt, k=k_factor
                        )
                    if not retrieved_docs:
                        text = (
                            "No relevant chunks were found in the index. "
                            "Check that documents are loaded and try a different question."
                        )
                        st.markdown(text)
                        assistant_entry = {
                            "role": "assistant",
                            "content": text,
                            "retrieved_docs": None,
                        }
                    else:
                        save_search_history(
                            prompt, len(retrieved_docs), k_factor
                        )
                        with st.spinner("Generating answer…"):
                            answer = st.session_state.rag_system.generate_answer(
                                prompt, retrieved_docs
                            )
                        st.markdown(answer)
                        render_retrieved_chunks_expander(
                            retrieved_docs, expanded=False
                        )
                        avg_score = sum(
                            d["similarity_score"] for d in retrieved_docs
                        ) / len(retrieved_docs)
                        st.caption(
                            f"{len(retrieved_docs)} sources · "
                            f"avg relevance {avg_score:.0%}"
                        )
                        st.download_button(
                            label="Download this answer",
                            data=answer,
                            file_name=f"answer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            width="stretch",
                            key=f"chat_dl_{dl_key_idx}",
                        )
                        assistant_entry = {
                            "role": "assistant",
                            "content": answer,
                            "retrieved_docs": retrieved_docs,
                        }
                except Exception as e:
                    text = f"Something went wrong: {e}"
                    st.error(text)
                    assistant_entry = {
                        "role": "assistant",
                        "content": text,
                        "retrieved_docs": None,
                    }

        if assistant_entry:
            st.session_state.chat_messages.append(assistant_entry)

    st.markdown("---")

    # Footer
    st.markdown(
        """
    <div style='text-align: center'>
        <p style='color: gray; font-size: 12px;'>
            RAG Application | OpenAI GPT-4o mini | ChromaDB Vector Store<br>
            © 2024 - All rights reserved
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
