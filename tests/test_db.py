import unittest
import os
from unittest.mock import patch
from pathlib import Path
from src.db.models import RequirementModel
from src.db.connection import init_db, get_db_connection
from src.db.repository import RequirementRepository, AuditRepository

# Create a dummy path for the test database
TEST_DB_PATH = Path(__file__).resolve().parent / "test_requirements.db"

class TestDatabaseLayer(unittest.TestCase):

    @classmethod
    @patch('src.db.connection.DB_PATH', TEST_DB_PATH)
    def setUpClass(cls):
        """Runs once before all tests. Initializes the test database."""
        # Ensure clean slate
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)
        init_db()

    @classmethod
    def tearDownClass(cls):
        """Runs once after all tests. Cleans up the test database."""
        if TEST_DB_PATH.exists():
            os.remove(TEST_DB_PATH)

    @patch('src.db.connection.DB_PATH', TEST_DB_PATH)
    @patch('src.db.repository.get_db_connection')
    def test_insert_requirement_and_audit(self, mock_get_conn):
        # We still want the repository to use the patched DB path context manager
        from src.db.connection import get_db_connection as real_get_conn
        mock_get_conn.side_effect = real_get_conn

        # 1. Create a valid Pydantic model
        req = RequirementModel(
            id="REQ-TEST-001",
            domain="Testing",
            statement="The system shall execute tests automatically.",
            category="Operational",
            source="Test Suite",
            business_justification="Ensure quality.",
            priority="High",
            confidence_score=0.95
        )

        # 2. Save it
        saved_id = RequirementRepository.save_requirement(req, user="Alice", role="Admin")
        self.assertEqual(saved_id, "REQ-TEST-001")

        # 3. Retrieve it
        all_reqs = RequirementRepository.get_all_requirements()
        self.assertEqual(len(all_reqs), 1)
        self.assertEqual(all_reqs[0]["statement"], "The system shall execute tests automatically.")

        # 4. Check Audit Log (Should show 'CREATE')
        logs = AuditRepository.get_logs_for_requirement("REQ-TEST-001")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["action"], "CREATE")
        self.assertEqual(logs[0]["performed_by"], "Alice")

    @patch('src.db.connection.DB_PATH', TEST_DB_PATH)
    @patch('src.db.repository.get_db_connection')
    def test_status_update_audit_trail(self, mock_get_conn):
        from src.db.connection import get_db_connection as real_get_conn
        mock_get_conn.side_effect = real_get_conn

        # Update the status (Simulating Human-in-the-loop approval)
        RequirementRepository.update_status(
            req_id="REQ-TEST-001",
            new_status="Approved",
            user="Bob",
            role="Compliance_Officer"
        )

        # Verify the audit log captured the state change
        logs = AuditRepository.get_logs_for_requirement("REQ-TEST-001")
        self.assertEqual(len(logs), 2) # Create + Update
        
        # Logs are sorted DESC by time, so the first one is the newest
        latest_log = logs[0]
        self.assertEqual(latest_log["action"], "STATUS_CHANGE")
        self.assertEqual(latest_log["previous_state"], "Pending Review")
        self.assertEqual(latest_log["new_state"], "Approved")
        self.assertEqual(latest_log["performed_by"], "Bob")

if __name__ == '__main__':
    unittest.main()