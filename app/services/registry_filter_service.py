import uuid
import re
from typing import List, Dict, Any, Optional
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
        intent_document_role: Optional[str] = None,
        user_prompt: Optional[str] = None,
        expanded_search_keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Registry Filter Service - Advanced Scoring & Ranking Engine (Relevance & Recency Balanced)
        """
        print("==================================================")
        print(f"DEBUG - current_workspace_id: {workspace_id}")
        print(f"DEBUG - target_departments  : {target_departments}")
        print(f"DEBUG - intent_time_scope   : {intent_time_scope}")
        print(f"DEBUG - intent_document_type: {intent_document_type}")
        print(f"DEBUG - intent_document_role: {intent_document_role}")
        print(f"DEBUG - expanded_keywords   : {expanded_search_keywords}")
        print("==================================================")

        # Phase 1: Workspace Isolation, Ready status
        query = db.query(UploadedDocument).filter(
            UploadedDocument.workspace_id == uuid.UUID(workspace_id),
            UploadedDocument.status == "ready",
            UploadedDocument.document_status != "Archived"
        )
        
        all_workspace_docs = query.all()
        
        # Tokenize user prompt and expanded search keywords
        search_tokens = set()
        if user_prompt:
            search_tokens.update(re.findall(r'\b\w{3,}\b', user_prompt.lower()))
            
        if expanded_search_keywords:
            for kw in expanded_search_keywords:
                if kw:
                    search_tokens.update(re.findall(r'\b\w{3,}\b', str(kw).lower()))

        scored_candidates = []
        
        # Phase 2: Compute Multi-Attribute Relevance Score
        for doc in all_workspace_docs:
            meta_blob = doc.knowledge_metadata or {}
            
            # 🟢 FIX 1: Read keywords from dynamic_metadata JSON array as well
            raw_dynamic_meta = meta_blob.get("dynamic_metadata", [])
            retrieval_keywords = []
            
            if isinstance(raw_dynamic_meta, list):
                for item in raw_dynamic_meta:
                    if isinstance(item, dict):
                        retrieval_keywords.append(str(item.get("value", "")))
                    elif isinstance(item, str):
                        retrieval_keywords.append(item)
            
            # Fallback checks
            retrieval_keywords.extend(meta_blob.get("global_retrieval_keywords", []))
            
            # 🟢 FIX 2: Safely read departments & topics from both root columns and JSON
            doc_departments = doc.departments if isinstance(doc.departments, list) and doc.departments else []
            doc_topics = doc.topics if isinstance(doc.topics, list) and doc.topics else []
            
            # Also read from JSON profile if available
            doc_profile = meta_blob.get("document_profile", {})
            if doc_profile.get("document_type"):
                doc_topics.append(doc_profile.get("document_type"))

            relevance_score = 0.0
            
            # 1. Soft Department Match (+20)
            if target_departments and doc_departments:
                matched_depts = set(d.lower().strip() for d in doc_departments).intersection(
                    set(t.lower().strip() for t in target_departments)
                )
                if matched_depts:
                    relevance_score += 20.0
                    
            # 2. Tokenized Topic / Document Type Overlap Match (+25 max)
            clean_intent_doc_type = (intent_document_type or "").lower()
            clean_doc_type = (doc.document_type or "").lower()
            
            if clean_intent_doc_type and clean_doc_type:
                # Direct string containment match
                if clean_intent_doc_type in clean_doc_type or clean_doc_type in clean_intent_doc_type:
                    relevance_score += 25.0
                else:
                    intent_tokens = set(re.findall(r'\b\w{3,}\b', clean_intent_doc_type))
                    doc_type_tokens = set(re.findall(r'\b\w{3,}\b', clean_doc_type))
                    if intent_tokens.intersection(doc_type_tokens):
                        relevance_score += 15.0

            # 3. Soft Role Match (+15)
            if intent_document_role and doc.document_role:
                if str(doc.document_role).lower().strip() == intent_document_role.lower().strip():
                    relevance_score += 15.0
                        
            # 4. Keyword Overlap (+6 per match, max 30)
            if search_tokens and retrieval_keywords:
                clean_keywords = set(str(k).lower().strip() for k in retrieval_keywords if k)
                keyword_intersection = search_tokens.intersection(clean_keywords)
                relevance_score += min(len(keyword_intersection) * 6.0, 30.0)
                
            # 5. Planner Summary Similarity Boost (+3 per token match, max 20)
            if search_tokens and doc.planner_summary:
                summary_tokens = set(re.findall(r'\b\w{3,}\b', str(doc.planner_summary).lower()))
                summary_intersection = search_tokens.intersection(summary_tokens)
                if summary_intersection:
                    relevance_score += min(len(summary_intersection) * 3.0, 20.0)

            # 6. Authority & Importance Bonus
            doc_authority = float(doc.authority_score or 50)
            doc_importance = float(doc.importance_score or 50)
            authority_bonus = (doc_authority + doc_importance) / 10.0
            
            # Freshness / Approval Bonus
            freshness_bonus = float(doc.freshness or 0.5) * 10.0
            approved_bonus = 5.0 if getattr(doc, "approved", False) else 0.0

            final_calculated_score = relevance_score + authority_bonus + freshness_bonus + approved_bonus

            scored_candidates.append({
                "doc_obj": doc,
                "calculated_score": final_calculated_score,
                "keywords": retrieval_keywords,
                "created_at": doc.created_at
            })
            
        # Phase 3: Sort by calculated score DESC, fallback to created_at DESC
        scored_candidates.sort(key=lambda x: (x["calculated_score"], x["created_at"]), reverse=True)
        
        # 🟢 FIX 3: Guarantee top 3 most recently uploaded files are included in the pool!
        recent_docs = sorted(all_workspace_docs, key=lambda d: d.created_at, reverse=True)[:3]
        recent_ids = set(str(d.id) for d in recent_docs)

        top_candidates = scored_candidates[:15]
        selected_ids = set(str(item["doc_obj"].id) for item in top_candidates)

        # Append missing recent files if pushed out by older high-scoring test files
        for r_doc in recent_docs:
            if str(r_doc.id) not in selected_ids:
                # Find its scored item
                matched_item = next((item for item in scored_candidates if str(item["doc_obj"].id) == str(r_doc.id)), None)
                if matched_item:
                    top_candidates.append(matched_item)

        print("--- SCORING-RANKED CANDIDATE ROW DETAILS ---")
        for item in top_candidates:
            d = item["doc_obj"]
            print(
                f"FINAL SCORE: {item['calculated_score']:.2f} | "
                f"{d.filename} | "
                f"{d.document_type} | "
                f"{d.document_role} | "
                f"Time: {d.time_scope}"
            )
        print("--------------------------------------------")
        print(f"DEBUG - SQL ROWS RETRIEVED: {len(all_workspace_docs)} | RANKED TOP CANDIDATES RETURNED: {len(top_candidates)}")
        print("==================================================")
        
        lightweight_candidates = []
        for item in top_candidates:
            doc = item["doc_obj"]
            meta_blob = doc.knowledge_metadata or {}
            questions = meta_blob.get("questions_this_document_can_answer", [])
            
            lightweight_candidates.append({
                "id": str(doc.id),
                "filename": str(doc.filename) if getattr(doc, "filename", None) else "Unknown Document",
                "document_type": str(doc.document_type),
                "document_role": str(doc.document_role),
                "time_scope": str(doc.time_scope) if getattr(doc, "time_scope", None) else "N/A",
                "document_status": str(doc.document_status) if getattr(doc, "document_status", None) else "N/A",
                "authority_score": int(doc.authority_score or 50),
                "importance_score": int(doc.importance_score or 50),
                "freshness": float(doc.freshness or 0.5),
                "planner_summary": str(doc.planner_summary or ""),
                "retrieval_keywords": item["keywords"],
                "questions_this_document_can_answer": questions,
                "retrieval_score": round(item["calculated_score"], 2)
            })
            
        return lightweight_candidates