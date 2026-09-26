from typing import List, Dict
from src.rag.vector_store import get_vector_store

def retrieve_compliance_guidelines(query: str, top_k: int = 3) -> List[Dict[str, str]]:
    """
    Searches the knowledge base for relevant regulations based on the query.
    Returns the raw text and its original source filename.
    """
    vector_store = get_vector_store()
    
    # Perform similarity search; returns tuples of (Document, distance_score)
    results = vector_store.similarity_search_with_score(query, k=top_k)
    
    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("filename", "Unknown Source"),
            "relevance_score": float(score)  # Lower score usually means closer distance in Chroma
        })
        
    return formatted_results