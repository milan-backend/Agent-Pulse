import uuid
import re
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
        intent_document_role: Optional[str] = None,
        user_prompt: Optional[str] = None,
        expanded_search_keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Registry Filter Service - Advanced Scoring & Ranking Engine (Relevance-First)
        Evolves the registry from static database filtering to a semantic ranking system.
        """
        # 🔍 LIVE LOG DEBUGGING
        print("==================================================")
        print(f"DEBUG - current_workspace_id: {workspace_id}")
        print(f"DEBUG - target_departments  : {target_departments}")
        print(f"DEBUG - intent_time_scope   : {intent_time_scope}")
        print(f"DEBUG - intent_document_type: {intent_document_type}")
        print(f"DEBUG - intent_document_role: {intent_document_role}")
        print(f"DEBUG - expanded_keywords   : {expanded_search_keywords}")
        print("==================================================")

        # Phase 1: Workspace Isolation, Ready status, and excluding Archived
        query = db.query(UploadedDocument).filter(
            UploadedDocument.workspace_id == uuid.UUID(workspace_id),
            UploadedDocument.status == "ready",
            UploadedDocument.document_status != "Archived"
        )
        
        all_workspace_docs = query.all()
        
        # 🎯 IMPROVEMENT 2: Tokenize and combine raw prompt AND expanded keywords
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
            retrieval_keywords = meta_blob.get("retrieval_keywords", [])
            doc_topics = doc.topics if isinstance(doc.topics, list) else []
            doc_departments = doc.departments if isinstance(doc.departments, list) else []
            
            relevance_score = 0.0
            
            # 1. Soft Department Match (+20)
            if target_departments and doc_departments:
                matched_depts = set(d.lower().strip() for d in doc_departments).intersection(
                    set(t.lower().strip() for t in target_departments)
                )
                if matched_depts:
                    relevance_score += 20.0
                    
            # 2. 🎯 IMPROVEMENT 3: Tokenized Topic Overlap Match (+20 max)
            if intent_document_type and doc_topics:
                # Tokenize the intent document type/topic target
                intent_topic_tokens = set(re.findall(r'\b\w{3,}\b', intent_document_type.lower()))
                # Tokenize all document topics stored in the registry
                doc_topic_tokens = set()
                for topic in doc_topics:
                    doc_topic_tokens.update(re.findall(r'\b\w{3,}\b', str(topic).lower()))
                
                matched_topics = intent_topic_tokens.intersection(doc_topic_tokens)
                if matched_topics:
                    # Provide +5 per token match up to +20 points
                    relevance_score += min(len(matched_topics) * 5.0, 20.0)
                    
            # 3. Soft Role Match (+15)
            if intent_document_role and doc.document_role:
                if str(doc.document_role).lower().strip() == intent_document_role.lower().strip():
                    relevance_score += 15.0
                    
            # 4. Soft Time Match (+15)
            if intent_time_scope and doc.time_scope:
                clean_time = intent_time_scope.lower().strip()
                clean_doc_time = str(doc.time_scope).lower().strip()
                if clean_time in clean_doc_time or clean_doc_time in clean_time:
                    if clean_time not in ["universal", "unspecified", "historical"]:
                        relevance_score += 15.0
                        
            # 5. 🎯 IMPROVEMENT 2: Soft Retrieval Keyword Overlap (+6 per match, max 30)
            # Evaluated against both prompt AND expanded strategic concepts
            if search_tokens and retrieval_keywords:
                keyword_intersection = search_tokens.intersection(
                    set(str(k).lower().strip() for k in retrieval_keywords)
                )
                relevance_score += min(len(keyword_intersection) * 6.0, 30.0)
                
            # 6. Planner Summary Similarity Boost (+3 per token match, max 15)
            if search_tokens and doc.planner_summary:
                summary_tokens = set(re.findall(r'\b\w{3,}\b', str(doc.planner_summary).lower()))
                summary_intersection = search_tokens.intersection(summary_tokens)
                if summary_intersection:
                    relevance_score += min(len(summary_intersection) * 3.0, 15.0)

            # 7. 🎯 IMPROVEMENT 1: Authority & Importance scaled down to a non-dominating bonus
            # Combines authority (max 100) and importance (max 100) into a max +20 points bonus
            doc_authority = float(doc.authority_score or 50)
            doc_importance = float(doc.importance_score or 50)
            authority_bonus = (doc_authority + doc_importance) / 10.0
            
            # 8. Freshness Bonus (Scaled to max 10 points)
            freshness_bonus = float(doc.freshness or 0.5) * 10.0
            
            # Approved Document Baseline Boost (+5)
            approved_bonus = 5.0 if getattr(doc, "approved", False) else 0.0

            # Combined total score
            final_calculated_score = relevance_score + authority_bonus + freshness_bonus + approved_bonus

            scored_candidates.append({
                "doc_obj": doc,
                "calculated_score": final_calculated_score,
                "keywords": retrieval_keywords
            })
            
        # Phase 3: Sort by calculated score descending and select Top 15 Candidates
        scored_candidates.sort(key=lambda x: x["calculated_score"], reverse=True)
        top_candidates = scored_candidates[:15]
        
        # 🔍 Debug telemetry loop showing ranking details
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
        
        # Serialize into clean dictionary nodes for the Planner AI
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