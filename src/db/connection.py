import sqlite3
import threading
from contextlib import contextmanager
from src.config import DB_PATH

# Thread lock to prevent SQLite database locked errors in concurrent Streamlit sessions
_db_lock = threading.Lock()

@contextmanager
def get_db_connection():
    """Context manager for thread-safe SQLite connections with WAL mode."""
    with _db_lock:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        finally:
            conn.close()

def init_db():
    """Initializes the database schemas for requirements and audit logs."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Requirements Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS requirements (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                statement TEXT NOT NULL,
                category TEXT NOT NULL,
                source TEXT NOT NULL,
                business_justification TEXT,
                priority TEXT,
                compliance_mapping TEXT,
                risk_level TEXT,
                confidence_score REAL,
                status TEXT DEFAULT 'Pending Review',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Audit/HITL Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id TEXT,
                action TEXT NOT NULL,
                performed_by TEXT NOT NULL,
                role TEXT NOT NULL,
                previous_state TEXT,
                new_state TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (requirement_id) REFERENCES requirements (id)
            )
        ''')
        
        conn.commit()