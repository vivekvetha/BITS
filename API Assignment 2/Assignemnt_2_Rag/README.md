# RAG Application (Retrieval-Augmented Generation)

A Streamlit app that loads PDFs from a local folder, embeds them into **ChromaDB**, and answers questions in a **chat UI** using OpenAI embeddings and **`gpt-4o-mini`** (configurable in `config.py`).

---

## What this project does

1. **Retrieval**: Embed the user question, search Chroma for the top‑K similar chunks.  
2. **Augmentation**: Pass those chunks as context to the chat model.  
3. **Generation**: Produce an answer grounded in the retrieved text (with a **Source** expander for raw chunks).

---

## Features

| Area | Details |
|------|---------|
| PDFs | Read from **`documents/`** (path: `DOCUMENTS_FOLDER` in `config.py`). No browser upload. |
| Index | Persisted under **`chroma_data/`**. On startup, existing data is reused; new PDFs are ingested only when the collection is empty unless you **Reindex**. |
| UI | **Chat** in the main area; **sidebar** (starts collapsed) for API key, **K** slider, **Reindex**, **Clear chat**, query log, export. |
| Models | Embeddings: `text-embedding-ada-002`. Chat: `gpt-4o-mini` (`OPENAI_CONFIG` in `config.py`). |
| History | Sidebar shows recent **queries** only; **Export chat log** downloads full JSON (timestamps, K, counts). |

---

## Quick start

### Prerequisites

- Python **3.10+** recommended (3.8+ may work).  
- An [OpenAI API key](https://platform.openai.com/api-keys).  
- One or more **`.pdf`** files in the `documents` folder (see `config.py` → `DOCUMENTS_FOLDER`).

### Install and run

```bash
cd Assignemnt_2_Rag
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
streamlit run app.py
```

Open **http://localhost:8501**. Use the **arrow** at the top-left to open the **sidebar** if it is collapsed.

### First-time flow

1. Put PDFs in **`documents/`** (or the folder set in `config.py`).  
2. Ensure **`OPENAI_API_KEY`** is in `.env` or paste it in the sidebar.  
3. The app **connects and indexes automatically** on load when a key is present (see progress in the main area).  
4. Chat in the main input. Adjust **K** in the sidebar if you want more or fewer chunks.  
5. After **changing or adding PDFs**, click **Reindex** to rebuild the vector store.

---

## Configuration (`config.py`)

| Setting | Role |
|---------|------|
| `DOCUMENTS_FOLDER` | Directory scanned for `*.pdf`. |
| `CHROMADB_CONFIG` | `persist_directory`, `collection_name`, metric. |
| `OPENAI_CONFIG` | `embedding_model`, `chat_model`, `max_tokens`, `temperature`. |
| `RETRIEVAL_CONFIG` | Default / min / max **K**, similarity threshold for answers. |
| `DOCUMENT_CONFIG` | Chunk size and overlap for splitting. |

---

## Project layout

```
Assignemnt_2_Rag/
├── app.py              # Streamlit UI (chat, sidebar, auto-init, reindex)
├── rag.py              # RAGSystem: load, split, embed, Chroma, retrieve, answer
├── config.py           # Paths and model / retrieval settings
├── requirements.txt    # Pinned dependencies
├── test_rag.py         # CLI demo / tests (optional)
├── .env.example        # Template for OPENAI_API_KEY
├── documents/          # Place PDFs here (name from config)
├── chroma_data/        # Created at runtime (gitignored)
└── README.md           # This file
```

**Dependencies** (see `requirements.txt` for versions): `openai`, `chromadb`, `pypdf`, `streamlit`, `python-dotenv`, `langchain`.

---

## Architecture (high level)

```
PDFs in documents/  →  load_pdf / split_documents
        →  embeddings (OpenAI)  →  ChromaDB collection (persisted)
User message (app)  →  retrieve(query, k)  →  generate_answer(query, chunks)
        →  chat UI + optional Source expander
```

---

## `RAGSystem` API (`rag.py`) — summary

| Method | Purpose |
|--------|---------|
| `__init__(api_key, persist_directory)` | OpenAI client + Chroma persistent client. |
| `load_pdf(path)` | Extract text with page markers. |
| `split_documents(text, chunk_size, overlap)` | Chunks + per-chunk metadata. |
| `get_embeddings(texts)` | Batch embeddings (`text-embedding-ada-002`). |
| `create_collection(name, delete_existing)` | Get or create Chroma collection. |
| `vectorize_documents(chunks, metadata, pdf_name)` | Add chunks to the collection. |
| `process_pdf(path)` | Load → split → embed → store one PDF. |
| `connect_and_sync_documents_folder(dir, …, force_reindex)` | Startup / reindex orchestration (skip if index populated unless forced). |
| `list_pdf_files(dir)` | Sorted list of PDF paths. |
| `retrieve(query, k)` | Query embedding + Chroma similarity search. |
| `validate_context(context, min_similarity)` | Filter weak matches before answering. |
| `generate_answer(query, context)` | Chat completion using `OPENAI_CONFIG["chat_model"]`. |
| `get_collection_stats()` | Name, chunk count, etc. |
| `clear_collection(name)` | Delete collection (still available for scripts/tests). |

For argument details and edge cases, see docstrings in **`rag.py`**.

---

## Data shapes

**Retrieved chunk** (each element from `retrieve`):

```json
{
  "rank": 1,
  "content": "…",
  "metadata": {
    "source": "filename_without_ext",
    "chunk_number": "1",
    "page_number": "3",
    "topic": "…",
    "snippet": "…"
  },
  "similarity_score": 0.85
}
```

**Exported chat log entry** (JSON from sidebar export):

```json
{
  "timestamp": "2026-04-25 12:00:00",
  "query": "What is DevOps?",
  "k_factor": 5,
  "results_count": 5
}
```

---

## Security and operations

- Do **not** commit `.env` or real API keys.  
- **`chroma_data/`** holds local vectors; delete it to wipe the index (or use **Reindex** for a controlled rebuild).  
- Usage is billed by **OpenAI** (embeddings + chat); monitor usage in the OpenAI dashboard.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| API key errors | Set `OPENAI_API_KEY` in `.env` or sidebar; restart or refresh. |
| Empty or stale index | Add PDFs to `documents/`, then **Reindex**. |
| No chunks retrieved | Lower similarity expectations in code, raise **K**, or rephrase the question. |
| Rate limits | Wait and retry; reduce how often you reindex large PDF sets. |
| Import / version errors | Use a virtualenv; `pip install -r requirements.txt` again. |

---

## CLI demo

```bash
python test_rag.py
```

Uses `sample_document.pdf` if present (see `test_rag.py` for paths).

---

## License and purpose

Educational / assignment use. Extend or replace models and paths via **`config.py`** and env vars.
