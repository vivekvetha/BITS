"""
Configuration settings for RAG Application
"""

# Document Processing Settings
DOCUMENT_CONFIG = {
    "chunk_size": 1000,  # Characters per chunk
    "overlap": 200,  # Characters overlap between chunks
    "min_chunk_size": 50,  # Minimum chunk size to include
}

# Local PDF source (no browser upload; place .pdf files here)
DOCUMENTS_FOLDER = "./documents"

# ChromaDB Settings
CHROMADB_CONFIG = {
    "persist_directory": "./chroma_data",
    "collection_name": "documents",
    "similarity_metric": "cosine",  # cosine, euclidean, etc.
}

# OpenAI Settings
OPENAI_CONFIG = {
    "embedding_model": "text-embedding-ada-002",
    "embedding_dimensions": 1536,
    "chat_model": "gpt-4o-mini",
    "max_tokens": 2000,  # Increased for detailed answers
    "temperature": 0.3,  # Reduced to 0.3 to prevent hallucination and make responses more deterministic
}

# Retrieval Settings
RETRIEVAL_CONFIG = {
    "default_k": 5,  # Default number of results
    "min_k": 1,
    "max_k": 20,
    "min_similarity": 0.3,  # Minimum 30% similarity threshold - documents below this are filtered out
}

# Streamlit Settings
STREAMLIT_CONFIG = {
    "page_title": "RAG Application",
    "page_icon": "🤖",
    "layout": "wide",
    "history_size": 50,  # Keep last 50 searches
}
