import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.models.uploaded_document import UploadedDocument

class RegistryFilterService:
    @staticmethod
    def extract_top_candidates(
        db: Session, 
        workspace_id: str, 
        target_departments: List[str],
        intent_time_scope: Optional[str] = None,
        intent_document_type: Optional[str] = None,
        intent_document_role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Registry Filter Service SQL Core Optimization
        Filters documents down to a context-targeted candidate bucket (max 8).
        """
        # Base Filter: Workspace isolation boundary, ready status, and excluding archived files
        query = db.query(UploadedDocument).filter(
            UploadedDocument.workspace_id == uuid.UUID(workspace_id),
            UploadedDocument.status == "ready",
            UploadedDocument.document_status != "Archived"
        )
        
        # Department Intersection Filter Logic
        if target_departments:
            department_filters = [
                UploadedDocument.departments.comparator.contains([dept]) 
                for dept in target_departments
            ]
            query = query.filter(or_(*department_filters))
            
        # Intent-Driven Multi-Attribute Pre-Filtering Modifications
        if intent_time_scope and intent_time_scope.strip().lower() != "universal":
            query = query.filter(UploadedDocument.time_scope.ilike(f"%{intent_time_scope.strip()}%"))
            
        if intent_document_type and intent_document_type.strip():
            query = query.filter(UploadedDocument.document_type.ilike(f"%{intent_document_type.strip()}%"))
            
        if intent_document_role and intent_document_role.strip():
            query = query.filter(UploadedDocument.document_role.ilike(f"%{intent_document_role.strip()}%"))

        # Four-Tier Progressive Ordering Matrix execution
        candidate_rows = (
            query.order_by(
                UploadedDocument.approved.desc(),
                UploadedDocument.authority_score.desc(),
                UploadedDocument.importance_score.desc(),
                UploadedDocument.freshness.desc()
            )
            .limit(8)
            .all()
        )
        
        # Serialize into clean dictionary nodes for the Planner AI
        lightweight_candidates = []
        for doc in candidate_rows:
            meta_blob = doc.knowledge_metadata or {}
            extracted_keywords = meta_blob.get("global_retrieval_keywords", [])
            questions = meta_blob.get("questions_this_document_can_answer", [])
            
            lightweight_candidates.append({
                "id": str(doc.id),
                "filename": str(doc.filename) if getattr(doc, "filename", None) else "Unknown Document",
                "document_type": str(doc.document_type),
                "document_role": str(doc.document_role),
                "time_scope": str(doc.time_scope) if getattr(doc, "time_scope", None) else "N/A",
                "document_status": str(doc.document_status) if getattr(doc, "document_status", None) else "N/A",
                "authority_score": int(doc.authority_score),
                "importance_score": int(doc.importance_score),
                "freshness": float(doc.freshness),
                "planner_summary": str(doc.planner_summary),
                "retrieval_keywords": extracted_keywords,
                "questions_this_document_can_answer": questions
            })
            
        return lightweight_candidates