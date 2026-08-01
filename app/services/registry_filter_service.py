import uuid
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.uploaded_document import UploadedDocument
# 🟢 NEW ARCHITECTURE IMPORTS
from app.models.new_arch import ExtractedEntity

# Handle potential naming variations for the Navigation Map model
try:
    from app.models.new_arch import DocumentSection
except ImportError:
    try:
        from app.models.new_arch import NavigationMap as DocumentSection
    except ImportError:
        DocumentSection = None

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
        Registry Filter Service - Advanced Scoring & Ranking Engine
        Upgraded for Hierarchical RAG (Integrates Entities & Navigation Maps)
        """
        print("==================================================")
        print(f"DEBUG - current_workspace_id: {workspace_id}")
        print(f"DEBUG - target_departments  : {target_departments}")
        print(f"DEBUG - intent_time_scope   : {intent_time_scope}")
        print(f"DEBUG - intent_document_type: {intent_document_type}")
        print(f"DEBUG - intent_document_role: {intent_document_role}")
        print(f"DEBUG - expanded_keywords   : {expanded_search_keywords}")
        print("==================================================")

        workspace_uuid = uuid.UUID(workspace_id)

        # Phase 1: Fetch Ready Documents
        query = db.query(UploadedDocument).filter(
            UploadedDocument.workspace_id == workspace_uuid,
            UploadedDocument.status == "ready",
            or_(
                UploadedDocument.document_status == None,
                UploadedDocument.document_status != "Archived"
            )
        )
        all_workspace_docs = query.all()
        doc_ids = [doc.id for doc in all_workspace_docs]

        # 🟢 PRE-FETCH NEW ARCHITECTURE DATA (Entities & Sections)
        doc_entities = defaultdict(list)
        doc_sections = defaultdict(list)

        if doc_ids:
            # Fetch Entities
            entities = db.query(ExtractedEntity).filter(ExtractedEntity.document_id.in_(doc_ids)).all()
            for ent in entities:
                doc_entities[ent.document_id].append(ent)
                
            # Fetch Sections (Navigation Map)
            if DocumentSection:
                sections = db.query(DocumentSection).filter(DocumentSection.document_id.in_(doc_ids)).all()
                for sec in sections:
                    doc_sections[sec.document_id].append(sec)

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
            
            # Legacy Keyword Parsing
            raw_dynamic_meta = meta_blob.get("dynamic_metadata", [])
            retrieval_keywords = []
            
            if isinstance(raw_dynamic_meta, list):
                for item in raw_dynamic_meta:
                    if isinstance(item, dict):
                        retrieval_keywords.append(str(item.get("value", "")))
                    elif isinstance(item, str):
                        retrieval_keywords.append(item)
            
            retrieval_keywords.extend(meta_blob.get("global_retrieval_keywords", []))
            
            doc_departments = doc.departments if isinstance(doc.departments, list) and doc.departments else []
            doc_topics = doc.topics if isinstance(doc.topics, list) and doc.topics else []
            
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
                        
            # 4. Legacy Keyword Overlap (+6 per match, max 30)
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

            # 🟢 6. NEW ARCHITECTURE: Extracted Entities Overlap (+5 per matched entity, max 25)
            doc_extracted_entities = doc_entities.get(doc.id, [])
            matched_entity_names = []
            if search_tokens and doc_extracted_entities:
                for ent in doc_extracted_entities:
                    ent_tokens = set(re.findall(r'\b\w{3,}\b', str(ent.name).lower()))
                    if search_tokens.intersection(ent_tokens):
                        matched_entity_names.append(ent.name)
                
                if matched_entity_names:
                    relevance_score += min(len(matched_entity_names) * 5.0, 25.0)

            # 🟢 7. NEW ARCHITECTURE: Section/Navigation Map Overlap (+8 per matched section, max 24)
            doc_nav_sections = doc_sections.get(doc.id, [])
            matched_section_titles = []
            if search_tokens and doc_nav_sections:
                for sec in doc_nav_sections:
                    sec_tokens = set(re.findall(r'\b\w{3,}\b', str(sec.title).lower()))
                    if search_tokens.intersection(sec_tokens):
                        matched_section_titles.append(sec.title)
                
                if matched_section_titles:
                    relevance_score += min(len(matched_section_titles) * 8.0, 24.0)

            # 8. Authority, Freshness & Importance Bonus
            doc_authority = float(doc.authority_score or 50)
            doc_importance = float(doc.importance_score or 50)
            authority_bonus = (doc_authority + doc_importance) / 10.0
            
            freshness_bonus = float(doc.freshness or 0.5) * 10.0
            approved_bonus = 5.0 if getattr(doc, "approved", False) else 0.0

            final_calculated_score = relevance_score + authority_bonus + freshness_bonus + approved_bonus

            scored_candidates.append({
                "doc_obj": doc,
                "calculated_score": final_calculated_score,
                "keywords": retrieval_keywords,
                "matched_entities": list(set(matched_entity_names)),
                "matched_sections": list(set(matched_section_titles)),
                "created_at": doc.created_at
            })
            
        # Phase 3: Sort by calculated score DESC, fallback to created_at DESC
        scored_candidates.sort(key=lambda x: (x["calculated_score"], x["created_at"]), reverse=True)
        
        recent_docs = sorted(all_workspace_docs, key=lambda d: d.created_at, reverse=True)[:3]
        top_candidates = scored_candidates[:15]
        selected_ids = set(str(item["doc_obj"].id) for item in top_candidates)

        for r_doc in recent_docs:
            if str(r_doc.id) not in selected_ids:
                matched_item = next((item for item in scored_candidates if str(item["doc_obj"].id) == str(r_doc.id)), None)
                if matched_item:
                    top_candidates.append(matched_item)

        print("--- SCORING-RANKED CANDIDATE ROW DETAILS ---")
        for item in top_candidates:
            d = item["doc_obj"]
            print(
                f"FINAL SCORE: {item['calculated_score']:.2f} | "
                f"{d.filename} | "
                f"Matched Entities: {len(item['matched_entities'])} | "
                f"Matched Sections: {len(item['matched_sections'])}"
            )
        print("--------------------------------------------")
        print(f"DEBUG - SQL ROWS RETRIEVED: {len(all_workspace_docs)} | RANKED TOP CANDIDATES RETURNED: {len(top_candidates)}")
        print("==================================================")
        
        # Format the final output to pass down to the AI
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
                "relevant_entities": item["matched_entities"],      # 🟢 Exposes Entities to AI
                "relevant_sections": item["matched_sections"],      # 🟢 Exposes Sections to AI
                "questions_this_document_can_answer": questions,
                "retrieval_score": round(item["calculated_score"], 2)
            })
            
        return lightweight_candidates