import os
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import KB_DIR

def load_text_documents(directory_path: str) -> List[Document]:
    """Recursively loads all .txt and .md files from a directory."""
    documents = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith((".txt", ".md")):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
                    # Attach metadata for citations later
                    doc = Document(
                        page_content=text,
                        metadata={"source": file_path, "filename": file}
                    )
                    documents.append(doc)
    return documents

def process_directory(directory_path: str = str(KB_DIR), chunk_size: int = 1000, chunk_overlap: int = 150) -> List[Document]:
    """Loads and splits documents into optimized chunks for vector embedding."""
    docs = load_text_documents(directory_path)
    
    # Split text logically based on paragraphs and sentences
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    return text_splitter.split_documents(docs)