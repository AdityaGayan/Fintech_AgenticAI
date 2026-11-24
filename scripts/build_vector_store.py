"""Build the persistent Chroma collection from local knowledge-base files."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.document_loader import process_directory
from src.rag.vector_store import build_vector_store


def main() -> None:
    documents = process_directory()
    if not documents:
        raise SystemExit("No .txt or .md documents found in data/knowledge_base")

    store = build_vector_store(documents, collection_name="fintech_compliance")
    print(f"Indexed {store._collection.count()} chunks in fintech_compliance")


if __name__ == "__main__":
    main()
