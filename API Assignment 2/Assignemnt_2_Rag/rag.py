import os
from pypdf import PdfReader
from typing import List, Dict, Tuple, Any
from openai import OpenAI
import chromadb
import hashlib
from datetime import datetime

from config import OPENAI_CONFIG


class RAGSystem:
    """
    Retrieval-Augmented Generation System
    Combines PDF loading, document splitting, embeddings, and vector retrieval
    """
    NO_INFO_MESSAGE = "This information is not available in the provided documents."

    def __init__(self, api_key: str, persist_directory: str = "./chroma_data"):
        """
        Initialize RAG System

        Args:
            api_key: OpenAI API key
            persist_directory: Directory to persist ChromaDB data
        """
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.persist_directory = persist_directory

        # Initialize ChromaDB with new API
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        self.collection = None
        self.documents_metadata = {}

    def load_pdf(self, pdf_path: str) -> str:
        """
        Load and extract text from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text from PDF
        """
        text = ""
        failed_pages = 0
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text() or ""
                    except Exception as page_error:
                        failed_pages += 1
                        print(
                            f"⚠️ Skipping page {page_num + 1} in {pdf_path}: {page_error}"
                        )
                        continue
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            if failed_pages:
                print(
                    f"⚠️ Loaded PDF with {failed_pages} page(s) skipped due to extraction errors: {pdf_path}"
                )
            print(f"✓ Successfully loaded PDF: {pdf_path}")
            return text
        except Exception as e:
            print(f"✗ Error loading PDF: {str(e)}")
            raise

    def split_documents(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> Tuple[List[str], List[Dict]]:
        """
        Split documents into chunks and extract metadata (page numbers, topics)

        Args:
            text: Full text to split
            chunk_size: Size of each chunk
            overlap: Overlap between chunks

        Returns:
            Tuple of (List of text chunks, List of chunk metadata with page info)
        """
        chunks = []
        chunk_metadata = []
        current_page = 1

        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                page_number = current_page

                # Extract page number from chunk if it contains page marker
                if "--- Page" in chunk:
                    lines = chunk.split("\n")
                    for line in lines:
                        if "--- Page" in line:
                            try:
                                # Extract page number
                                page_str = line.split("--- Page ")[1].split(" ---")[0]
                                page_number = int(page_str.strip())
                                current_page = page_number
                                break
                            except (IndexError, ValueError):
                                pass

                chunks.append(chunk)
                chunk_metadata.append(
                    {"page_number": page_number, "chunk_index": len(chunks)}
                )

        print(f"✓ Document split into {len(chunks)} chunks")
        return chunks, chunk_metadata

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-ada-002", input=text
                )
                embedding = response.data[0].embedding
                embeddings.append(embedding)
            except Exception as e:
                print(f"✗ Error generating embedding: {str(e)}")
                raise

        print(f"✓ Generated {len(embeddings)} embeddings")
        return embeddings

    def create_collection(
        self, collection_name: str = "documents", delete_existing: bool = False
    ):
        """
        Create or load a ChromaDB collection

        Args:
            collection_name: Name of the collection
            delete_existing: If True, delete existing collection before creating new one
        """
        try:
            # Delete existing collection if requested
            if delete_existing:
                try:
                    self.chroma_client.delete_collection(name=collection_name)
                    print(f"✓ Deleted existing collection: {collection_name}")
                except:
                    pass

            # Try to load existing collection first
            try:
                self.collection = self.chroma_client.get_collection(
                    name=collection_name
                )
                print(f"✓ Loaded existing ChromaDB collection: {collection_name}")
            except:
                # Create new collection if it doesn't exist
                self.collection = self.chroma_client.create_collection(
                    name=collection_name, metadata={"hnsw:space": "cosine"}
                )
                print(f"✓ Created new ChromaDB collection: {collection_name}")
        except Exception as e:
            print(f"✗ Error managing collection: {str(e)}")
            raise

    def extract_topic(self, text: str) -> str:
        """
        Extract topic/heading from text snippet

        Args:
            text: Full text chunk

        Returns:
            Topic or first significant phrase
        """
        lines = text.split("\n")
        for line in lines:
            clean_line = line.strip()
            # Skip page markers
            if "--- Page" in clean_line or clean_line == "---" or clean_line == "":
                continue
            # Look for lines with keywords (What is, ➢, bullet points, etc.)
            if len(clean_line) > 10 and len(clean_line) < 150:
                return clean_line[:100]  # Return first meaningful line as topic
        return ""

    def create_snippet(self, text: str, max_length: int = 200) -> str:
        """
        Create a short snippet from text

        Args:
            text: Full text
            max_length: Maximum length of snippet

        Returns:
            Short text snippet
        """
        # Remove page markers and extra whitespace
        clean_text = text.replace("--- Page", "").replace("---", "").strip()
        # Remove multiple spaces
        clean_text = " ".join(clean_text.split())
        # Return snippet
        return (
            clean_text[:max_length] + "..."
            if len(clean_text) > max_length
            else clean_text
        )

    def vectorize_documents(
        self, chunks: List[str], chunk_metadata: List[Dict], pdf_name: str = "document"
    ):
        """
        Vectorize document chunks and store in ChromaDB

        Args:
            chunks: List of text chunks
            chunk_metadata: List of metadata for each chunk (with page_number)
            pdf_name: Name of the PDF document
        """
        if self.collection is None:
            self.create_collection()

        embeddings = self.get_embeddings(chunks)

        # Prepare data for ChromaDB with compact metadata
        ids = [f"{pdf_name}_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": pdf_name,
                "chunk_number": str(i + 1),
                "page_number": str(chunk_metadata[i].get("page_number", 0)),
                "topic": self.extract_topic(chunks[i]),
                "snippet": self.create_snippet(chunks[i]),
            }
            for i in range(len(chunks))
        ]

        # Add to collection
        self.collection.add(
            ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas
        )

        print(f"✓ Vectorized {len(chunks)} chunks in ChromaDB")
        self.documents_metadata[pdf_name] = len(chunks)

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """
        Retrieve top K similar documents from ChromaDB

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of retrieved documents with scores
        """
        if self.collection is None:
            print("✗ No collection initialized. Please load documents first.")
            return []

        # Get embedding for query
        try:
            query_embedding = (
                self.client.embeddings.create(
                    model="text-embedding-ada-002", input=query
                )
                .data[0]
                .embedding
            )
        except Exception as e:
            print(f"✗ Error generating query embedding: {str(e)}")
            return []

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        retrieved_docs = []
        if results["documents"] and len(results["documents"]) > 0:
            for i, (doc, metadata, distance) in enumerate(
                zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ):
                # Convert distance to similarity score (0-1)
                similarity = 1 - (distance / 2)
                retrieved_docs.append(
                    {
                        "rank": i + 1,
                        "content": doc,
                        "metadata": metadata,
                        "similarity_score": round(similarity, 4),
                    }
                )

        return retrieved_docs

    def validate_context(
        self, context: List[Dict], min_similarity: float = 0.3
    ) -> Tuple[bool, str, List[Dict]]:
        """
        Validate if the retrieved context is sufficient to answer the query

        Args:
            context: Retrieved documents
            min_similarity: Minimum similarity score threshold (0-1)

        Returns:
            Tuple of (is_valid, message, filtered_context)
        """
        if not context:
            return False, "No relevant documents found in the knowledge base.", []

        # Filter by minimum similarity
        filtered = [doc for doc in context if doc["similarity_score"] >= min_similarity]

        if not filtered:
            avg_score = sum(d["similarity_score"] for d in context) / len(context)
            return (
                False,
                f"No sufficiently relevant documents found. Average relevance: {avg_score:.1%} (threshold: {min_similarity:.0%})",
                [],
            )

        return True, f"Found {len(filtered)} relevant document(s)", filtered

    def normalize_answer_output(self, answer_text: str) -> str:
        """
        Enforce a single response mode: either grounded answer or fallback message.
        """
        text = (answer_text or "").strip()
        if not text:
            return self.NO_INFO_MESSAGE

        fallback = self.NO_INFO_MESSAGE
        fallback_count = text.count(fallback)
        if fallback_count == 0:
            return text

        cleaned = text.replace(fallback, "").strip()
        cleaned = cleaned.lstrip("-:;,. ").rstrip()
        if cleaned:
            return cleaned
        return fallback

    def generate_answer(
        self, query: str, context: List[Dict], max_tokens: int = 2000
    ) -> str:
        """
        Generate answer using ONLY retrieved context from documents

        Args:
            query: User query
            context: Retrieved documents
            max_tokens: Maximum tokens in response (default 2000 for detailed answers)

        Returns:
            Answer based strictly on provided documents, or message if information not available
        """
        # Validate context first
        is_valid, validation_msg, filtered_context = self.validate_context(
            context, min_similarity=0.3
        )

        if not is_valid:
            return f"Cannot answer the question: {validation_msg}"

        # Prepare context with source information
        context_text = "\n\n".join(
            [
                f"[Document {doc['rank']} - Relevance: {doc['similarity_score']:.1%}]\nSource: {doc['metadata'].get('source', 'Unknown')}\nContent:\n{doc['content']}"
                for doc in filtered_context
            ]
        )

        prompt = f"""You are an assistant that answers ONLY based on the provided documents. You must NOT use any external knowledge or general information not present in the documents.

CRITICAL RULES:
1. ONLY answer using information explicitly stated in the provided documents
2. NEVER make up facts, examples, or information not in the documents
3. NEVER use general knowledge or external sources
4. If the answer is not in the documents, reply with exactly this sentence and nothing else: "This information is not available in the provided documents."
5. Be honest about the limits of the provided information
6. Do NOT end your answer with parenthetical citations, document filenames, session codes, lecture IDs, or lists such as (DOC_NAME-1, SESSION-2). The reader sees sources elsewhere—keep the answer as plain explanatory prose only.

Documents (Your ONLY source of information):
{context_text}

User Question: {query}

Instructions:
- Answer ONLY based on the documents above
- If no answer is available from documents, return only the exact fallback sentence
- Do not provide examples or details not in the documents
- Keep your answer factual and directly from the documents
- Never mix a grounded answer with the fallback sentence in the same response
- Finish with a complete sentence; no trailing source codes or bracketed references

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG["chat_model"],
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a strict assistant that answers ONLY based on provided documents. "
                            "You DO NOT have general knowledge. You MUST refuse to answer with information "
                            "not found in the documents. Never make up information. "
                            "Do not append document names, session codes, or parenthetical lecture citations "
                            "at the end of your reply—plain prose only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.3,  # Reduced from 0.7 to make answers more deterministic and less creative
            )
            answer_text = response.choices[0].message.content or ""
            return self.normalize_answer_output(answer_text)
        except Exception as e:
            print(f"✗ Error generating answer: {str(e)}")
            return "Unable to generate answer."

    def process_pdf(self, pdf_path: str, collection_name: str = "documents") -> bool:
        """
        Complete pipeline: load PDF -> split -> embed -> vectorize

        Args:
            pdf_path: Path to PDF file
            collection_name: Name for the collection

        Returns:
            Success status
        """
        try:
            # Load PDF
            text = self.load_pdf(pdf_path)

            # Split documents and extract metadata
            chunks, chunk_metadata = self.split_documents(text)

            # Create collection if needed
            if self.collection is None:
                self.create_collection(collection_name)

            # Vectorize
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            self.vectorize_documents(chunks, chunk_metadata, pdf_name)

            print("✓ PDF processing completed successfully!")
            return True
        except Exception as e:
            print(f"✗ Pipeline error: {str(e)}")
            return False

    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection"""
        if self.collection is None:
            return {"status": "No collection initialized"}

        return {
            "collection_name": self.collection.name,
            "total_documents": self.collection.count(),
            "documents_processed": self.documents_metadata,
        }

    def clear_collection(self, collection_name: str = "documents") -> bool:
        """
        Clear all documents from collection

        Args:
            collection_name: Name of the collection to clear

        Returns:
            Success status
        """
        try:
            self.chroma_client.delete_collection(name=collection_name)
            self.collection = None
            self.documents_metadata = {}
            print(f"✓ Collection '{collection_name}' cleared successfully!")
            return True
        except Exception as e:
            print(f"✗ Error clearing collection: {str(e)}")
            return False

    def list_pdf_files(self, documents_dir: str) -> List[str]:
        """Return sorted absolute paths to PDF files in ``documents_dir``."""
        if not os.path.isdir(documents_dir):
            return []
        paths: List[str] = []
        for name in sorted(os.listdir(documents_dir)):
            if name.lower().endswith(".pdf"):
                paths.append(os.path.join(documents_dir, name))
        return paths

    def connect_and_sync_documents_folder(
        self,
        documents_dir: str = "./Document",
        collection_name: str = "documents",
        force_reindex: bool = False,
    ) -> Dict[str, Any]:
        """
        Attach to persisted Chroma and optionally ingest PDFs from a folder.

        If the collection already has vectors and ``force_reindex`` is False,
        PDFs are not processed again (avoids duplicate chunks and API calls).

        Args:
            documents_dir: Directory containing PDF files
            collection_name: Chroma collection name
            force_reindex: If True, delete the collection and rebuild from PDFs

        Returns:
            Summary dict with status, paths, counts, and messages
        """
        self.create_collection(collection_name, delete_existing=force_reindex)

        assert self.collection is not None
        existing_count = self.collection.count()

        if existing_count > 0 and not force_reindex:
            return {
                "status": "loaded_existing",
                "message": (
                    "Using existing Chroma index; skipped re-indexing. "
                    "Enable force re-index to rebuild from the Document folder "
                    "if there is a change in the documents."
                ),
                "documents_dir": os.path.abspath(documents_dir),
                "pdf_files": self.list_pdf_files(documents_dir),
                "total_documents": existing_count,
                "pdfs_processed": [],
                "pdfs_failed": [],
            }

        pdf_paths = self.list_pdf_files(documents_dir)
        if not pdf_paths:
            return {
                "status": "no_pdfs",
                "message": (
                    f"No PDF files found in {os.path.abspath(documents_dir)}. "
                    "Add .pdf files to that folder, or use an existing Chroma index."
                ),
                "documents_dir": os.path.abspath(documents_dir),
                "pdf_files": [],
                "total_documents": existing_count,
                "pdfs_processed": [],
                "pdfs_failed": [],
            }

        self.documents_metadata = {}
        processed: List[str] = []
        failed: List[str] = []

        for pdf_path in pdf_paths:
            name = os.path.basename(pdf_path)
            try:
                if self.process_pdf(pdf_path, collection_name=collection_name):
                    processed.append(name)
                else:
                    failed.append(name)
            except Exception:
                failed.append(name)

        final_count = self.collection.count()
        return {
            "status": "ingested" if not failed else "ingested_with_errors",
            "message": (
                f"Indexed {len(processed)} PDF(s) from the Document folder "
                f"({final_count} chunks in Chroma)."
            ),
            "documents_dir": os.path.abspath(documents_dir),
            "pdf_files": pdf_paths,
            "total_documents": final_count,
            "pdfs_processed": processed,
            "pdfs_failed": failed,
        }
