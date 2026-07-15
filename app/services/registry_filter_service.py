import uuid
from typing import List, Dict, Any
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.uploaded_document import UploadedDocument

class RegistryFilterService:
    @staticmethod
    def extract_top_candidates(
        db: Session, 
        workspace_id: str, 
        target_departments: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Component 3: Registry Filter Service (SQL Only)
        Filters thousands of documents down to a tight candidate bucket (max 8).
        Uses overlapping department logic and a 4-tier sorting matrix.
        """
        # Base Filter: Workspace isolation boundary, ready status, and excluding archived files
        query = db.query(UploadedDocument).filter(
            UploadedDocument.workspace_id == uuid.UUID(workspace_id),
            UploadedDocument.status == "ready",
            UploadedDocument.document_status != "Archived"
        )
        
        # 🎯 CORRECTION 1: Dynamic Department Overlap/Intersection Logic
        # Returns the document if it shares ONE or MORE departments with the Intent output
        if target_departments:
            department_filters = [
                UploadedDocument.departments.comparator.contains([dept]) 
                for dept in target_departments
            ]
            query = query.filter(or_(*department_filters))
            
        # 🎯 CORRECTION 2: Four-Tier Progressive Ordering Matrix
        # approved -> authority -> importance -> freshness
        candidate_rows = (
            query.order_by(
                UploadedDocument.approved.desc(),
                UploadedDocument.authority_score.desc(),
                UploadedDocument.importance_score.desc(),
                UploadedDocument.freshness.desc()  # Remove decaying documents early!
            )
            .limit(8)
            .all()
        )
        
        # Serialize into lightweight metadata nodes for the Planner AI
        lightweight_candidates = []
        for doc in candidate_rows:
            meta_blob = doc.knowledge_metadata or {}
            questions = meta_blob.get("questions_this_document_can_answer", [])
            
            lightweight_candidates.append({
                "id": str(doc.id),
                "document_type": str(doc.document_type),
                "document_role": str(doc.document_role),
                "authority_score": int(doc.authority_score),
                "importance_score": int(doc.importance_score),
                "freshness": float(doc.freshness),
                "planner_summary": str(doc.planner_summary),
                "questions_this_document_can_answer": questions
            })
            
        return lightweight_candidates