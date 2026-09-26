import json
from typing import List, Optional
from src.db.connection import get_db_connection
from src.db.models import RequirementModel, AuditLogModel

class RequirementRepository:
    
    @staticmethod
    def save_requirement(req: RequirementModel, user: str, role: str) -> str:
        """Inserts or updates a requirement and creates an audit trail."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if requirement exists for audit log
            cursor.execute("SELECT status FROM requirements WHERE id = ?", (req.id,))
            existing = cursor.fetchone()
            action = "UPDATE" if existing else "CREATE"
            previous_state = existing["status"] if existing else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO requirements 
                (id, domain, statement, category, source, business_justification, 
                 priority, compliance_mapping, risk_level, confidence_score, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                req.id, req.domain, req.statement, req.category, req.source, 
                req.business_justification, req.priority, req.compliance_mapping, 
                req.risk_level, req.confidence_score, req.status
            ))
            
            # Record audit trail
            cursor.execute('''
                INSERT INTO audit_logs (requirement_id, action, performed_by, role, previous_state, new_state)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (req.id, action, user, role, previous_state, req.status))
            
            conn.commit()
            return req.id

    @staticmethod
    def get_all_requirements() -> List[dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM requirements ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update_status(req_id: str, new_status: str, user: str, role: str):
        """Dedicated HITL method for status changes."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM requirements WHERE id = ?", (req_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Requirement {req_id} not found.")
            
            cursor.execute("UPDATE requirements SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", 
                           (new_status, req_id))
            
            cursor.execute('''
                INSERT INTO audit_logs (requirement_id, action, performed_by, role, previous_state, new_state)
                VALUES (?, 'STATUS_CHANGE', ?, ?, ?, ?)
            ''', (req_id, user, role, row["status"], new_status))
            conn.commit()

class AuditRepository:
    
    @staticmethod
    def get_logs_for_requirement(req_id: str) -> List[dict]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Order by id DESC guarantees absolute chronological order for sub-second inserts
            cursor.execute("SELECT * FROM audit_logs WHERE requirement_id = ? ORDER BY id DESC", (req_id,))
            return [dict(row) for row in cursor.fetchall()]