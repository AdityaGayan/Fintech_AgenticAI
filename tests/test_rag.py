import unittest
import os
import tempfile
import shutil
from unittest.mock import patch

from langchain_core.documents import Document
from langchain_core.embeddings import FakeEmbeddings

from src.rag.document_loader import process_directory
from src.rag.vector_store import build_vector_store
from src.rag.compliance_rag import retrieve_compliance_guidelines

class TestRAGPipeline(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory structure for testing
        cls.test_dir = tempfile.mkdtemp()
        cls.test_kb_dir = os.path.join(cls.test_dir, "knowledge_base")
        cls.test_db_dir = os.path.join(cls.test_dir, "vector_db")
        os.makedirs(cls.test_kb_dir)
        os.makedirs(cls.test_db_dir)

        # Write dummy regulatory files
        with open(os.path.join(cls.test_kb_dir, "pci_dss.txt"), "w") as f:
            f.write("PCI-DSS Req 8: Multi-factor authentication must be implemented for all network access.")
        
        with open(os.path.join(cls.test_kb_dir, "gdpr.txt"), "w") as f:
            f.write("GDPR Article 5: Personal data shall be processed lawfully, fairly and in a transparent manner.")

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary directories after tests finish
        shutil.rmtree(cls.test_dir, ignore_errors=True)

    def test_1_document_loader(self):
        """Test if the document loader successfully reads and chunks text files."""
        docs = process_directory(self.test_kb_dir, chunk_size=50, chunk_overlap=10)
        
        self.assertGreater(len(docs), 0)
        self.assertIn("metadata", docs[0].__dict__)
        self.assertTrue(any("PCI-DSS" in doc.page_content for doc in docs))

    @patch("src.rag.vector_store.VECTOR_DB_DIR", new_callable=lambda: TestRAGPipeline.test_db_dir)
    @patch("src.rag.vector_store.get_embeddings_model")
    def test_2_vector_store_build(self, mock_get_embeddings, mock_db_dir):
        """Test if ChromaDB accepts documents and builds an index."""
        # Use FakeEmbeddings to bypass OpenAI API calls
        mock_get_embeddings.return_value = FakeEmbeddings(size=10)
        
        docs = [Document(page_content="Data must be encrypted at rest.", metadata={"filename": "crypto_policy.txt"})]
        
        vs = build_vector_store(docs, collection_name="test_collection")
        self.assertIsNotNone(vs)
        
    @patch("src.rag.vector_store.VECTOR_DB_DIR", new_callable=lambda: TestRAGPipeline.test_db_dir)
    @patch("src.rag.vector_store.get_embeddings_model")
    def test_3_compliance_retrieval(self, mock_get_embeddings, mock_db_dir):
        """Test if the RAG function correctly queries the vector store and formats results."""
        mock_get_embeddings.return_value = FakeEmbeddings(size=10)
        
        docs = [
            Document(page_content="SOX requires strict audit trails.", metadata={"filename": "sox.txt"}),
        ]
        build_vector_store(docs, collection_name="test_compliance")
        
        # Patch the local get_vector_store inside compliance_rag
        with patch("src.rag.compliance_rag.get_vector_store") as mock_gvs:
            from langchain_community.vectorstores import Chroma
            mock_store = Chroma.from_documents(docs, FakeEmbeddings(size=10))
            mock_gvs.return_value = mock_store
            
            results = retrieve_compliance_guidelines("audit trails", top_k=1)
            
            self.assertEqual(len(results), 1)
            self.assertIn("content", results[0])
            self.assertIn("source", results[0])
            self.assertIn("relevance_score", results[0])
            self.assertEqual(results[0]["source"], "sox.txt")

if __name__ == '__main__':
    unittest.main()