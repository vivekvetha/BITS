# API Assignment 2

This repository contains two related pieces of work:

1. **`app_final.py`** — a Streamlit app (**AI Document Analyzer**) that ingests web articles, PDFs, or YouTube transcripts, summarizes them with OpenAI, and supports multi-turn Q&A. It also includes a **Financial Q&A** mode with an optional side-by-side comparison between a fine-tuned finance model and the base `gpt-4o-mini` model.
2. **`Assignemnt_2_Rag/`** — a separate RAG (retrieval-augmented generation) stack with its own FastAPI/CLI-style entry points, Chroma, and configuration. See [Assignemnt_2_Rag/README.md](Assignemnt_2_Rag/README.md) for that project.

---

## `app_final.py` — AI Document Analyzer

### What it does

| Mode | Input | Behavior |
|------|--------|------------|
| **Web Article** | URL | Downloads and parses article text (`newspaper3k`), then summary + document chat |
| **PDF Upload** | `.pdf` file | Extracts text with `pypdf`, with **PyMuPDF** fallback for tricky encodings |
| **YouTube Video** | YouTube URL | Fetches captions via `youtube-transcript-api` (supports `watch?v=` and `youtu.be` links) |
| **Financial QnA** | Chat only | Finance-focused assistant using a **fine-tuned** checkpoint; optional **Compare** mode shows Finance Model vs base `gpt-4o-mini` in two columns |

**Document modes** (article / PDF / YouTube): after content is loaded, you can **Generate Summary** (first ~8k characters sent to the model) and use **Chat about this document** for multi-turn Q&A grounded in that text (also ~8k chars in context). The document chat thread resets when the loaded content changes.

**Financial QnA**: uses a dedicated system prompt (`FINANCE_SYSTEM`) and either only the fine-tuned model or parallel completions for fine-tuned vs general model when **Compare** is selected. Switching compare mode clears the finance chat thread. Temperature is lower for the fine-tuned model (0.2) and higher for the base model (0.7).

The sidebar shows the last few cross-mode Q&A snippets (**Previous Chat Histories**, capped at five entries).

### Dependencies

Install from the repository root:

```bash
pip install -r requirements.txt
```

Packages: `streamlit`, `openai`, `newspaper3k`, `youtube-transcript-api`, `pypdf`, `pymupdf` (recommended for PDF fallback).

### Configuration and security

The app uses the OpenAI Python client. **Do not commit real API keys.** Configure a key in one of these ways:

- Set the environment variable `OPENAI_API_KEY` and change the client initialization in `app_final.py` to use `OpenAI()` without a hardcoded key (recommended), or
- Use [Streamlit secrets](https://docs.streamlit.io/develop/concepts/connections/secrets-management) for local/cloud deployment.

If an API key was ever committed in plain text, **rotate it** in the OpenAI dashboard and update your local configuration.

**Models:** `FINETUNED_MODEL` and `GENERAL_FINANCE_MODEL` are defined at the top of `app_final.py`. Replace the fine-tuned model ID with your own checkpoint if you do not have access to the one referenced in the file.

### Run the app

From the directory that contains `app_final.py`:

```bash
streamlit run app_final.py
```

Open the URL Streamlit prints (typically `http://localhost:8501`).

### Operational notes

- Article extraction depends on the target site and `newspaper3k`; some pages may fail or return little text.
- YouTube transcripts require available captions for the video.
- Summarization and document Q&A truncate long inputs (~8000 characters) to stay within practical context limits.

---

## Repository layout

```
.
├── app_final.py          # Streamlit: document analyzer + finance Q&A
├── requirements.txt      # Dependencies for app_final.py
├── README.md             # This file
└── Assignemnt_2_Rag/     # RAG service + tests (separate README)
```

For RAG-specific setup, environment variables, and API usage, follow **Assignemnt_2_Rag/README.md**.
