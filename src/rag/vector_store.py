from typing import List
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from src.config import VECTOR_DB_DIR, GEMINI_API_KEY, DEFAULT_EMBEDDING_MODEL

def get_embeddings_model():
    """Initializes the free, local HuggingFace embedding model."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_vector_store(collection_name: str = "fintech_compliance") -> Chroma:
    """Loads the existing persistent Chroma vector database."""
    return Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=get_embeddings_model(),
        collection_name=collection_name
    )

def build_vector_store(documents: List[Document], collection_name: str = "fintech_compliance") -> Chroma:
    """Embeds documents, saves them to ChromaDB, and returns the store."""
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings_model(),
        persist_directory=str(VECTOR_DB_DIR),
        collection_name=collection_name
    )
    return vector_store