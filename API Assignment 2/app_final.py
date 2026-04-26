import io
import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from newspaper import Article, Config
from youtube_transcript_api import YouTubeTranscriptApi
import pypdf
import textwrap
import logging
from urllib.parse import parse_qs, urlparse

try:
    import pymupdf

    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY not found. Set it in a .env file or environment variable.")
    st.stop()

client = OpenAI(api_key=api_key)

# Finance Model (OpenAI fine-tuned checkpoint) for specialized Q&A
# FINETUNED_MODEL = "ft:gpt-4o-mini-2024-07-18:personal:finance-assistant:DWjMH7QU"
FINETUNED_MODEL = "ft:gpt-4o-mini-2024-07-18:personal:finance-assistant-new:DWkuLO3d"
GENERAL_FINANCE_MODEL = "gpt-4o-mini-2024-07-18"

st.title("AI Document Analyzer")

# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Multi-turn Q&A for current document or finance session (UI + API context)
if "doc_qa_thread" not in st.session_state:
    st.session_state.doc_qa_thread = []
if "finance_qa_thread" not in st.session_state:
    st.session_state.finance_qa_thread = []
if "_doc_thread_hash" not in st.session_state:
    st.session_state._doc_thread_hash = None


def sync_doc_thread_to_context():
    """Clear document Q&A when loaded content changes so chats stay tied to one source."""
    h = hash(st.session_state.context) if st.session_state.context else None
    if st.session_state._doc_thread_hash != h:
        st.session_state.doc_qa_thread = []
        st.session_state._doc_thread_hash = h


def render_chat_thread(turns):
    """ChatGPT-style bubbles (Streamlit chat_message)."""
    for turn in turns:
        with st.chat_message("user"):
            st.markdown(turn["question"])
        with st.chat_message("assistant"):
            st.markdown(turn.get("answer") or "_No response_")


def render_finance_model_comparison_thread(turns):
    """Finance Q&A: one user bubble, assistant with Finance Model vs Base Model side by side."""
    for turn in turns:
        with st.chat_message("user"):
            st.markdown(turn["question"])
        with st.chat_message("assistant"):
            if "answer_ft" in turn and "answer_general" in turn:
                col_ft, col_gen = st.columns(2, gap="medium")
                with col_ft:
                    st.markdown("**Finance Model**")
                    st.caption(FINETUNED_MODEL)
                    st.markdown(turn.get("answer_ft") or "_No response_")
                with col_gen:
                    st.markdown("**Base model**")
                    st.caption(GENERAL_FINANCE_MODEL)
                    st.markdown(turn.get("answer_general") or "_No response_")
            else:
                st.caption("Legacy turn format; use **Clear chat** if replies look wrong.")
                st.markdown(turn.get("answer") or "_No response_")


def _finance_chat_messages(question, prior_turns):
    """Build OpenAI messages for general-finance Q&A (system + history + current question)."""
    messages = [{"role": "system", "content": FINANCE_SYSTEM}]
    for turn in prior_turns:
        messages.append({"role": "user", "content": turn["question"]})
        messages.append({"role": "assistant", "content": turn["answer"]})
    messages.append({"role": "user", "content": question})
    return messages


def completion_params_for_model(model: str):
    """Temperature and max_tokens tuned for Finance Model vs Base Model mini."""
    if model == FINETUNED_MODEL:
        return 0.2, 1000
    return 0.7, 1000


def finance_model_completion(question, prior_turns, model: str):
    """
    Run a single finance Q&A completion with the given model.
    prior_turns: list of {"question", "answer"} (assistant text from that same model).
    """
    messages = _finance_chat_messages(question, prior_turns)
    temperature, max_tokens = completion_params_for_model(model)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Finance model completion error ({model}): {e}")
        return f"Error: {e}"


# Function to add to chat history (keep only last 5)
def add_to_chat_history(question, answer, input_type):
    """Add Q&A pair to chat history, keeping only last 5"""
    st.session_state.chat_history.append(
        {"question": question, "answer": answer, "input_type": input_type}
    )
    # Keep only last 5 chat histories
    if len(st.session_state.chat_history) > 5:
        st.session_state.chat_history = st.session_state.chat_history[-5:]


st.sidebar.header("📋 Previous Chat Histories")
if st.session_state.chat_history:
    with st.sidebar.expander(
        f"View Last {len(st.session_state.chat_history)} Conversations"
    ):
        for idx, chat in enumerate(st.session_state.chat_history, 1):
            st.markdown(f"**Chat {idx}** ({chat['input_type']})")
            st.markdown(f"**Q:** {chat['question'][:100]}...")
            st.markdown(f"**A:** {chat['answer'][:150]}...")
            st.divider()
else:
    st.sidebar.info("No chat history yet")

st.sidebar.header("Input Options")

INPUT_TYPE_DESCRIPTIONS = {
    "Web Article": (
        "Paste a web page URL. The article is parsed for **Generate Summary** and "
        "document chat"
    ),
    "PDF Upload": (
        "Upload a PDF. Summary and document chat."
    ),
    "YouTube Video": (
        "Paste a YouTube link to load captions, then summarize and chat about the "
        "transcript."
    ),
    "Financial QnA": (
        "Finance Q&A with **FINANCE_SYSTEM**. Use **Finance Model only** or "
        "**Compare** (Finance Model vs Base Model)"
    ),
}

input_type = st.sidebar.selectbox(
    "Choose input type", list(INPUT_TYPE_DESCRIPTIONS.keys())
)

finance_compare = False
if input_type == "Financial QnA":
    st.sidebar.header("Finance Q&A")
    finance_mode = st.sidebar.radio(
        "Response mode",
        ["Finance Model", "Compare: Finance Model vs Base Model"],
        key="finance_qa_response_mode",
    )
    finance_compare = finance_mode.startswith("Compare")
    _fc_key = "_last_finance_compare_mode"
    if _fc_key not in st.session_state:
        st.session_state[_fc_key] = finance_compare
    elif st.session_state[_fc_key] != finance_compare:
        st.session_state.finance_qa_thread = []
        st.session_state[_fc_key] = finance_compare

st.sidebar.caption(INPUT_TYPE_DESCRIPTIONS[input_type])

if input_type != "Financial QnA":
    st.sidebar.caption(
        f"Summary & document chat: `{GENERAL_FINANCE_MODEL}`"
    )
else:
    if finance_compare:
        st.sidebar.caption(
            f"**Compare:** `{FINETUNED_MODEL}` vs `{GENERAL_FINANCE_MODEL}`"
        )
    else:
        st.sidebar.caption(f"**Finance Model:** `{FINETUNED_MODEL}`")

# ---------- TEXT EXTRACTION FUNCTIONS ----------


def extract_text_from_url(url):
    logging.info(f"Extracting text from URL: {url}")
    try:
        config = Config()
        config.request_timeout = 15  # Increase timeout to 15 seconds
        article = Article(url, config=config)
        article.download()
        article.parse()
        logging.info("Successfully extracted text from URL")
        return article.text
    except Exception as e:
        logging.error(f"Error extracting text from URL {url}: {e}")
        return ""


def _read_uploaded_pdf_bytes(file):
    """Reset file pointer and return full PDF bytes (Streamlit UploadedFile / BytesIO)."""
    if hasattr(file, "seek"):
        file.seek(0)
    data = file.read()
    if hasattr(file, "seek"):
        file.seek(0)
    return data


def _extract_text_pymupdf(pdf_bytes: bytes) -> str:
    if not HAS_PYMUPDF:
        return ""
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    try:
        return "".join(page.get_text() or "" for page in doc)
    finally:
        doc.close()


def extract_text_from_pdf(file):
    """
    Try pypdf first; on encoding errors (e.g. /SymbolSetEncoding) or empty text,
    fall back to PyMuPDF, which handles many more PDF font setups.
    """
    logging.info("Extracting text from PDF")
    try:
        pdf_bytes = _read_uploaded_pdf_bytes(file)
    except Exception as e:
        logging.error(f"Could not read PDF upload: {e}")
        return ""

    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        text = "".join((page.extract_text() or "") for page in reader.pages)
        if text.strip():
            logging.info("Successfully extracted text from PDF (pypdf)")
            return text
        logging.warning("pypdf returned no text; trying PyMuPDF fallback")
    except Exception as e:
        logging.warning(f"pypdf failed ({e}); trying PyMuPDF fallback")

    if not HAS_PYMUPDF:
        logging.error(
            "PyMuPDF is not installed. Run: pip install pymupdf "
            "(required as fallback for PDFs with custom font encodings)."
        )
        return ""

    try:
        text = _extract_text_pymupdf(pdf_bytes)
        if text.strip():
            logging.info("Successfully extracted text from PDF (PyMuPDF)")
            return text
        logging.error("PyMuPDF returned no extractable text")
        return ""
    except Exception as e:
        logging.error(f"PyMuPDF extraction failed: {e}")
        return ""


def extract_text_from_youtube(url):
    logging.info(f"Extracting transcript from YouTube URL: {url}")
    try:
        parsed = urlparse(url)
        video_id = ""

        if "youtu.be" in parsed.netloc:
            # Short URL format: https://youtu.be/<video_id>?...
            video_id = parsed.path.lstrip("/").split("/")[0]
        elif "youtube.com" in parsed.netloc:
            # Standard format: https://www.youtube.com/watch?v=<video_id>
            video_id = parse_qs(parsed.query).get("v", [""])[0]

        if not video_id:
            logging.error(f"Could not extract video id from URL: {url}")
            return ""

        # Support both old and new youtube-transcript-api interfaces
        if hasattr(YouTubeTranscriptApi, "get_transcript"):
            transcript_items = YouTubeTranscriptApi.get_transcript(video_id)
        else:
            transcript_items = YouTubeTranscriptApi().fetch(video_id)

        text_chunks = []
        for item in transcript_items:
            if isinstance(item, dict):
                text_chunks.append(item.get("text", ""))
            else:
                text_chunks.append(getattr(item, "text", ""))

        text = " ".join(chunk for chunk in text_chunks if chunk).strip()
        logging.info("Successfully extracted transcript from YouTube")
        return text
    except Exception as e:
        logging.error(f"Error extracting transcript from YouTube URL {url}: {e}")
        return ""


# ---------- AI FUNCTIONS ----------
def summarize_text(text, model: str):
    logging.info(f"Starting text summarization (model={model})")
    try:
        prompt = f"""
        Summarize the following content.

        Provide:
        1. Short Summary
        2. Key Points
        """

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt + text[:8000]}],
        )
        logging.info("Successfully summarized text")
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error summarizing text: {e}")
        return "Error in summarization"


FINANCE_SYSTEM = """You are a specialized finance expert. Using your training knowledge of financial concepts, terminology, and principles, provide COMPREHENSIVE and DETAILED responses.

For each answer, when appropriate, include:
- Complete definition and explanation of the concept
- Formula or calculation method if applicable
- What it measures and its practical significance
- How it's interpreted and used in financial analysis
- Typical ranges or benchmarks if relevant
- Related financial concepts or ratios
- Real-world application examples

Base your answers on specialized finance knowledge. Be thorough. If the user refers to something from earlier in the conversation, use that context."""


def ask_question(question, context, prior_turns=None, model: str | None = None):
    """Q&A over loaded document (article, PDF, or transcript)."""
    prior_turns = prior_turns or []
    model = model or GENERAL_FINANCE_MODEL
    temperature, max_tokens = completion_params_for_model(model)
    logging.info(f"Answering question (model={model}): {question}")
    try:
        doc_system = (
            "Answer using the provided document. If the user refers to earlier "
            "messages in the conversation, use those together with the document.\n\n"
            f"Document:\n{context[:8000]}"
        )
        messages = [{"role": "system", "content": doc_system}]
        for turn in prior_turns:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        logging.info("Successfully answered question")
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error answering question: {e}")
        return "Error in answering question"


# ---------- USER INPUT ----------

if "context" not in st.session_state:
    st.session_state.context = ""

if input_type == "Web Article":

    url = st.text_input("Enter article URL")

    if st.button("Analyze Article") and url:
        logging.info(f"User selected to analyze article: {url}")
        st.session_state.context = extract_text_from_url(url)
        st.success("Article loaded!")

elif input_type == "PDF Upload":

    file = st.file_uploader("Upload PDF", type=["pdf"])

    if file:
        logging.info("User uploaded PDF")
        st.session_state.context = extract_text_from_pdf(file)
        st.success("PDF loaded!")

elif input_type == "YouTube Video":

    url = st.text_input("Enter YouTube URL")

    if st.button("Analyze Video") and url:
        logging.info(f"User selected to analyze YouTube video: {url}")
        st.session_state.context = extract_text_from_youtube(url)
        st.success("Video transcript loaded!")

elif input_type == "Financial QnA":
    # Question entry lives in the Financial Q&A section below (single input for multi-turn chat).
    pass

# ---------- SUMMARY ----------

if st.session_state.context:
    if st.button("Generate Summary"):
        logging.info("User requested summary generation")
        summary = summarize_text(st.session_state.context, GENERAL_FINANCE_MODEL)

        st.subheader("Summary")
        st.write(summary)

# ---------- QUESTION ANSWERING ----------

# Handle Financial QnA (direct questions without document context)
if input_type == "Financial QnA":
    head_l, head_r = st.columns([5, 1])
    with head_l:
        if finance_compare:
            st.markdown("### Finance assistant — model comparison")
            st.caption(
                f"**Finance Model** (`{FINETUNED_MODEL}`) "
                f"vs **Base Model** (`{GENERAL_FINANCE_MODEL}`)"
            )
        else:
            st.markdown("### Finance assistant")
            st.caption(f"Finance Model: `{FINETUNED_MODEL}`")
    with head_r:
        if st.button("Clear chat", key="clear_finance_thread"):
            st.session_state.finance_qa_thread = []
            st.rerun()

    if finance_compare:
        render_finance_model_comparison_thread(st.session_state.finance_qa_thread)
    else:
        render_chat_thread(st.session_state.finance_qa_thread)

    if prompt := st.chat_input(
        "Message finance assistant…",
        key="finance_chat_input",
    ):
        q = prompt.strip()
        if q:
            thread = list(st.session_state.finance_qa_thread)

            if finance_compare:
                logging.info("Answering finance question (Finance Model vs base)")
                prior_ft = [
                    {"question": t["question"], "answer": t["answer_ft"]}
                    for t in thread
                    if t.get("answer_ft") is not None
                ]
                prior_gen = [
                    {"question": t["question"], "answer": t["answer_general"]}
                    for t in thread
                    if t.get("answer_general") is not None
                ]
                with st.spinner("Running Finance Model and base models…"):
                    answer_ft = finance_model_completion(q, prior_ft, FINETUNED_MODEL)
                    answer_general = finance_model_completion(
                        q, prior_gen, GENERAL_FINANCE_MODEL
                    )
                st.session_state.finance_qa_thread.append(
                    {
                        "question": q,
                        "answer_ft": answer_ft,
                        "answer_general": answer_general,
                    }
                )
                combined_preview = (
                    f"[Finance Model] {answer_ft[:200]}… | [Base] {answer_general[:200]}…"
                    if len(answer_ft) > 200 or len(answer_general) > 200
                    else f"[Finance Model] {answer_ft} | [Base] {answer_general}"
                )
                add_to_chat_history(q, combined_preview, input_type)
            else:
                logging.info(
                    f"Answering finance question (model={FINETUNED_MODEL}): {q}"
                )
                prior = [
                    {"question": t["question"], "answer": t["answer"]}
                    for t in thread
                    if t.get("answer") is not None
                ]
                with st.spinner("Thinking…"):
                    answer = finance_model_completion(q, prior, FINETUNED_MODEL)
                st.session_state.finance_qa_thread.append(
                    {"question": q, "answer": answer}
                )
                add_to_chat_history(q, answer, input_type)
            st.rerun()

# Handle questions about loaded content (documents/videos)
elif st.session_state.context:
    sync_doc_thread_to_context()

    head_l, head_r = st.columns([5, 1])
    with head_l:
        st.markdown("### Chat about this document")
        st.caption(
            f"`{GENERAL_FINANCE_MODEL}` · Answers use your loaded article, PDF, or transcript"
        )
    with head_r:
        if st.button("Clear chat", key="clear_doc_thread"):
            st.session_state.doc_qa_thread = []
            st.rerun()

    render_chat_thread(st.session_state.doc_qa_thread)

    if prompt := st.chat_input(
        "Ask about this content…",
        key="doc_chat_input",
    ):
        q = prompt.strip()
        if q:
            logging.info(
                f"User asked question (model={GENERAL_FINANCE_MODEL}): {q}"
            )
            prior = list(st.session_state.doc_qa_thread)
            with st.spinner("Thinking…"):
                answer = ask_question(
                    q,
                    st.session_state.context,
                    prior_turns=prior,
                    model=GENERAL_FINANCE_MODEL,
                )
            st.session_state.doc_qa_thread.append({"question": q, "answer": answer})
            add_to_chat_history(q, answer, input_type)
            st.rerun()
