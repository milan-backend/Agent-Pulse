import os
import uuid
import time
from datetime import datetime
import chromadb
from celery import Celery, shared_task
from google import genai  # 🎯 Official Google GenAI SDK interface
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.durable_step import DurableStep
from app.models.agent import Agent
from app.models.agent_policy import AgentPolicy
from app.models.user_api_key import UserAPIKey  
from app.core.rag_crypto import decrypt_text_string  

# 🟢 IMPORT THE UPLOADED DOCUMENT MODEL FOR THE PERMANENT LOGICAL CHECK
from app.models.uploaded_document import UploadedDocument  

from app.services.llm_service import generate_llm_response
from app.services.tokenizer_service import calculate_usage
from app.services.usage_service import create_usage_event
from app.services.user_api_key_service import UserAPIKeyService
from app.services.intent_service import analyze_user_query_intent
from app.services.registry_filter_service import RegistryFilterService
from app.services.planner_service import execute_retrieval_planning_triage

import re
import nltk
from nltk.corpus import wordnet

# Silently download the local WordNet database tracking array if not already present
try:
    nltk.data.find('corpora/wordnet.zip')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Global in-memory vector cache to hit sub-1-second latency targets on repeating steps
GLOBAL_VECTOR_CACHE = {}

def dynamically_expand_query_intent_local(prompt: str) -> str:
    """
    Scans the prompt string and injects hidden semantic synonyms locally from 
    the WordNet lexical core under 1ms without calling any external network APIs.
    Works dynamically for Education, Healthcare, or any uploaded domain.
    """
    if not prompt or not prompt.strip():
        return prompt

    # Extract all words longer than 3 characters to target meaningful subjects
    words = re.findall(r'\b[a-zA-Z]{4,}\b', prompt.lower())
    expanded_synonyms = set()

    # Only skip basic grammatical noise words, allowing all domain terms (medical, school, etc.)
    common_stopwords = ['this', 'that', 'they', 'with', 'from', 'your', 'have', 'here', 'then']

    for word in words:
        if word in common_stopwords:
            continue
            
        # Dynamically fetch synonyms from the local WordNet database footprint
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonym = lemma.name().replace('_', ' ').lower()
                # Ensure we don't duplicate the word itself or terms already in the user's prompt
                if synonym != word and synonym not in prompt.lower():
                    expanded_synonyms.add(synonym)
                    
    # Pull the top 6 semantic keywords so the embedding density stays razor sharp
    limited_synonyms = list(expanded_synonyms)[:6]
    
    if limited_synonyms:
        return f"{prompt} (concepts: {', '.join(limited_synonyms)})"
    return prompt

# Initialize Celery app broker bindings
CELERY_BROKER = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL")
celery_app = Celery("step_tasks", broker=CELERY_BROKER)


# ====================================================================
# SECURE DYNAMIC CHROMA HTTP CLIENT HELPER (NO HARDCODED GITHUB LINKS)
# ====================================================================
def get_chroma_client():
    """Initializes a clean, cloud-native HTTP client strictly via environment variables."""
    chroma_host = os.getenv("CHROMA_HOST")
    chroma_token = os.getenv("CHROMA_TOKEN")
    
    if not chroma_host:
        raise ValueError("CRITICAL: CHROMA_HOST environment variable is missing on this server container")
    
    # Strip any trailing slashes cleanly from the environment string
    chroma_host = str(chroma_host).strip().rstrip("/")
    
    # Securely wrap connections passing the token via authorization headers
    return chromadb.HttpClient(
        host=chroma_host,
        headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
    )


@shared_task(bind=True, max_retries=5)
def process_step(self, step_id: str):
    db = SessionLocal()
    step = None

    try:
        step = db.query(DurableStep).get(step_id)

        if not step:
            return {
                "status": "failed",
                "message": "Step not found"
            }

        # STRICT BOUNDARY CHECK: Ensure workspace_id exists on the step right away
        if not step.workspace_id:
            step.status = "failed"
            step.error_message = "Security Violation: Workspace context missing from step execution parameters"
            db.commit()
            return {
                "status": "failed",
                "message": "Mandatory Workspace Context validation missing"
            }

        current_workspace_id = str(step.workspace_id).strip()

        # =========================================
        # GET AGENT
        # =========================================
        agent = db.query(Agent).filter(
            Agent.id == step.agent_id,
            Agent.workspace_id == current_workspace_id  
        ).first()

        if not agent:
            step.status = "failed"
            step.error_message = "Agent not found within this workspace scope"
            db.commit()
            return {
                "status": "failed",
                "message": "Agent not found"
            }

        # =========================================
        # GET AGENT POLICY
        # =========================================
        policy = db.query(AgentPolicy).filter(
            AgentPolicy.agent_id == agent.id
        ).first()

        # =========================================
        # MARK STEP RUNNING
        # =========================================
        step.status = "running"
        step.started_at = datetime.utcnow()
        db.commit()
        #  This LINE HERE: This tells the frontend to turn the RAM/CPU lights on instantly!
        from app.api.routes.ws import broadcast_message
        import asyncio
        import json
        try:
            asyncio.run(broadcast_message(json.dumps({"type": "mission_updated", "step_id": step_id, "status": "running"})))
        except Exception:
            pass

        # REFRESH STATE
        db.refresh(agent)

        # =========================================
        # GLOBAL EMERGENCY STOP
        # =========================================
        if agent.is_killed:
            step.status = "failed"
            step.error_message = "Agent manually stopped"
            step.output_data = {
                "success": False,
                "reason": "global_killed"
            }
            step.completed_at = datetime.utcnow()
            db.commit()

            return {
                "status": "stopped",
                "message": "Global agent execution halted"
            }

        # =========================================
        # MISSION LEVEL KILL
        # =========================================
        db.refresh(step)

        if step.status == "killed":
            step.error_message = "Mission manually killed"
            step.output_data = {
                "success": False,
                "reason": "mission_killed"
            }
            step.killed_at = datetime.utcnow()
            db.commit()

            return {
                "status": "killed",
                "message": "Mission execution halted"
            }

        # =========================================
        # MISSION PAUSE
        # =========================================
        if step.status == "paused":
            return {
                "status": "paused",
                "message": "Mission paused"
            }

        # =========================================
        # MAX STEP CHECK
        # =========================================
        current_step_count = (
            db.query(DurableStep)
            .filter(
                DurableStep.agent_id == agent.id,
                DurableStep.status.in_(["pending", "running"])
            )
            .count()
        )

        if (
            policy and
            current_step_count >= policy.max_steps
        ):
            step.status = "failed"
            step.error_message = "Max step limit reached"
            step.output_data = {
                "success": False,
                "reason": "max_steps_exceeded"
            }
            step.completed_at = datetime.utcnow()
            db.commit()

            return {
                "status": "failed",
                "message": "Max step limit reached"
            }

        # =========================================
        # REAL AI EXECUTION
        # =========================================
        try:
            if isinstance(step.input_data, dict):
                prompt = step.input_data.get("prompt", "")
            else:
                prompt = str(step.input_data)

            # =====================================================================
            # 🧠 COMPONENT 4: INTENT UNDERSTANDING TRIAGE LAYER
            # =====================================================================
            intent_strategy = None
            if prompt and str(prompt).strip():
                try:
                    print(f"📡 Executing Intent Triage Layer for Step ID: {step.id}")
                    # Capture the structured retrieval strategy blueprint from Gemini
                    intent_strategy = analyze_user_query_intent(prompt)
                    print(f"🎯 Intent Diagnosed: {intent_strategy.intent_type} | Topic: {intent_strategy.main_topic}")
                except Exception as intent_err:
                    print(f"⚠️ Non-fatal Intent Layer fallback executed: {str(intent_err)}")
            # =====================================================================    

            tier_status_msg = "Notice: Running on System Shared Sandbox Tier."

            if not prompt or not str(prompt).strip():
                output = "No prompt provided. LLM execution skipped"
                completion_usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0
                }
                active_model_target = "gemini-2.5-flash-lite"
                rag_telemetry_node = {}
                tier_status_msg = "Notice: Empty execution payload string dropped safely."
            else:
                # ========================================================
                # UPGRADED MULTI-PROVIDER MODEL & CREDENTIAL LOOKUP ENGINE
                # ========================================================
                agent_id_raw = agent.id if agent else None
                agent_model = getattr(agent, "model_name", None)
                active_model_target = None
                
                agent_model_clean = str(agent_model).lower().strip() if agent_model else ""
                requested_engine = "openai" if ("gpt" in agent_model_clean or "openai" in agent_model_clean) else "gemini"

                resolved_key_record = None
                tier_source = "system"

                if agent_id_raw:
                    resolved_key_record, tier_source = UserAPIKeyService.resolve_agent_api_key(
                        db=db,
                        workspace_id=uuid.UUID(current_workspace_id),
                        agent_id=agent_id_raw,
                        provider_type=requested_engine
                    )

                    if resolved_key_record and resolved_key_record.model_name:
                        active_model_target = str(resolved_key_record.model_name).strip()

                if not active_model_target and agent_model and str(agent_model).strip():
                    active_model_target = str(agent_model).strip()

                if not active_model_target:
                    active_model_target = "gpt-4o-mini" if requested_engine == "openai" else "gemini-2.5-flash-lite"

                if not resolved_key_record and not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
                    raise ValueError(
                        f"Zero-Trust Violation: Agent '{agent_id_raw}' is not explicitly assigned to any valid keys "
                        f"in the workspace provider array list, and no system environment variables are active. Execution denied."
                    )

                # =====================================================================
                # 🗄️ COMPONENT 3: DETERMINISTIC REGISTRY FILTER SERVICE (SQL ONLY)
                # =====================================================================
                context_fragments = []
                documents_influencing_list = []
                
                rag_telemetry_node = {
                    "event_name": "PLANNED_KNOWLEDGE_RETRIEVAL",
                    "sql_initial_candidates": 0,
                    "sql_pruned_candidates": 0,
                    "planner_selected_count": 0,
                    "blueprint_notes": ""
                }

                # Extract target departments array from intent triage layers
                target_depts = intent_strategy.target_departments if intent_strategy else []

                # Execute deterministic backend filtering out of AI space (thousands -> max 8)
                lightweight_candidates = RegistryFilterService.extract_top_candidates(
                    db=db,
                    workspace_id=current_workspace_id,
                    target_departments=target_depts
                )
                
                rag_telemetry_node["sql_pruned_candidates"] = len(lightweight_candidates)

                # =====================================================================
                # 🧠 COMPONENT 4: PLANNER AI (COGNITIVE STRATEGY ROUTING Layer)
                # =====================================================================
                retrieval_blueprint = None
                if lightweight_candidates and intent_strategy:
                    print(f"📡 Executing Planner AI Strategy over {len(lightweight_candidates)} lightweight metadata profiles...")
                    try:
                        retrieval_blueprint = execute_retrieval_planning_triage(
                            user_prompt=prompt,
                            intent_strategy=intent_strategy,
                            lightweight_candidates=lightweight_candidates
                        )
                        rag_telemetry_node["planner_selected_count"] = len(retrieval_blueprint.selected_documents)
                        rag_telemetry_node["blueprint_notes"] = retrieval_blueprint.planner_notes
                    except Exception as planner_err:
                        print(f"⚠️ Non-fatal Planner AI strategy generation failed: {str(planner_err)}")

                # =====================================================================
                # 🎯 COMPONENT 5: TARGETED VECTOR SEARCH ENGINE OPERATIONS ONLY
                # =====================================================================
                if retrieval_blueprint and retrieval_blueprint.selected_documents:
                    target_doc_ids = [str(d.document_id) for d in retrieval_blueprint.selected_documents]
                    
                    # Merge original prompt instruction with planner vector search queries
                    combined_search_queries = [prompt] + retrieval_blueprint.vector_search_terms
                    
                    # INITIALIZE OFFICIAL GEMINI CLIENT FOR PLAIN TEXT EMBEDDINGS
                    gemini_api_key = os.getenv("GEMINI_API_KEY")
                    if not gemini_api_key and resolved_key_record:
                        from app.core.crypto import decrypt_api_key
                        gemini_api_key = decrypt_api_key(resolved_key_record.encrypted_api_key)

                    if gemini_api_key:
                        ai_client = genai.Client(api_key=gemini_api_key)
                        chroma_client = get_chroma_client()
                        collection = chroma_client.get_collection(name="rag_enterprise_vectors_v1")
                        
                        if collection:
                            accumulated_chunks = []
                            seen_chunk_ids = set()
                            
                            # Query inside selected targets using planner configuration instructions
                            for query_term in combined_search_queries[:3]:
                                try:
                                    vector_resp = ai_client.models.embed_content(
                                        model="gemini-embedding-2",
                                        contents=query_term
                                    )
                                    term_vector = vector_resp.embeddings[0].values
                                except Exception:
                                    try:
                                        vector_resp = ai_client.models.embed_content(
                                            model="text-embedding-004",
                                            contents=query_term
                                        )
                                        term_vector = vector_resp.embeddings[0].values
                                    except Exception:
                                        vector_resp = ai_client.models.embed_content(
                                            model="text-embedding-005",
                                            contents=query_term
                                        )
                                        term_vector = vector_resp.embeddings[0].values

                                search_results = collection.query(
                                    query_embeddings=[term_vector],
                                    # Request slightly more for reranking pool overhead buffers
                                    n_results=min(retrieval_blueprint.max_chunks + 4, 12),
                                    where={
                                        "$and": [
                                            {"workspace_id": current_workspace_id},
                                            {"document_id": {"$in": target_doc_ids}}
                                        ]
                                    }
                                )
                                
                                docs_list = search_results.get("documents", [[]])[0] if search_results.get("documents") else []
                                metas_list = search_results.get("metadatas", [[]])[0] if search_results.get("metadatas") else []
                                dists_list = search_results.get("distances", [[]])[0] if search_results.get("distances") else []
                                
                                for idx, enc_chunk in enumerate(docs_list):
                                    meta_data = metas_list[idx] if idx < len(metas_list) else {}
                                    raw_dist = dists_list[idx] if idx < len(dists_list) else 1.0
                                    chunk_uid = f"{meta_data.get('document_id')}_idx_{idx}"
                                    
                                    if chunk_uid not in seen_chunk_ids:
                                        seen_chunk_ids.add(chunk_uid)
                                        base_sim = max(0.0, (1.0 - float(raw_dist)))
                                        
                                        # =====================================================================
                                        # ⏱️ COMPONENT 6: FRESHNESS EXPONENTIAL DECAY RERANKING LOOP
                                        # =====================================================================
                                        doc_date_raw = meta_data.get("last_updated", "2026-01-01")
                                        try:
                                            chunk_ts = datetime.strptime(doc_date_raw[:10], "%Y-%m-%d")
                                            age_hours = (datetime.utcnow() - chunk_ts).total_seconds() / 3600.0
                                        except Exception:
                                            age_hours = 0.0
                                            
                                        lambda_decay = 0.005
                                        freshness_mult = float(2.71828 ** (-lambda_decay * age_hours))
                                        final_score = base_sim * freshness_mult
                                        
                                        accumulated_chunks.append({
                                            "enc_text": enc_chunk,
                                            "filename": meta_data.get("source_file", "Unknown"),
                                            "score": final_score
                                        })

                            # Sort aggregate chunks based on decay rank criteria fields top down
                            accumulated_chunks.sort(key=lambda x: x["score"], reverse=True)
                            
                            # Truncate text context footprint safely to match blueprint criteria caps
                            for item in accumulated_chunks[:retrieval_blueprint.max_chunks]:
                                plain_text = decrypt_text_string(item["enc_text"], uuid.UUID(current_workspace_id))
                                if plain_text:
                                    context_fragments.append(plain_text)
                                    if item["filename"] not in documents_influencing_list:
                                        documents_influencing_list.append(item["filename"])

                # Inject decoded evidence context pieces cleanly into the final prompt payload blocks
                final_prompt_payload = prompt
                if context_fragments:
                    combined_context = "\n\n".join(context_fragments)
                    final_prompt_payload = (
                        f"CRITICAL EVIDENCE REGISTER SELECTIONS:\n"
                        f"==================================================\n"
                        f"{combined_context}\n"
                        f"==================================================\n\n"
                        f"USER QUESTION: {prompt}"
                    )

                output, tier_status_msg = generate_llm_response(
                    prompt=final_prompt_payload,
                    db=db,
                    workspace_id=current_workspace_id,
                    agent_id=agent_id_raw,
                    model_name=active_model_target
                )
                
                completion_usage = calculate_usage(
                   prompt=final_prompt_payload,
                   completion=output,
                   model_name=active_model_target if active_model_target else "gemini-2.5-flash-lite"
                )

        except Exception as llm_error:
            error_message = str(llm_error)

            if "429" in error_message:
                retry_count = self.request.retries
                countdown = 2 ** retry_count
                raise self.retry(exc=llm_error, countdown=countdown)

            current_retries = getattr(step, "retry_count", 0) or 0
            max_allowed_retries = policy.max_retries if policy else 0

            if policy and policy.enable_retry_control and current_retries < max_allowed_retries:
                step.retry_count = current_retries + 1
                step.status = "pending"
                step.error_message = f"Execution failed, attempting automatic retry ({step.retry_count}/{max_allowed_retries}): {error_message}"
                db.commit()

                process_step.delay(str(step.id))
                
                return {
                    "status": "retrying",
                    "message": f"Step execution failed. Automatic retry tracking re-queued background loop."
                }

            step.status = "failed"
            step.error_message = f"LLM execution failed and retries exhausted: {error_message}"
            step.output_data = {
                "success": False,
                "reason": "llm_failure"
            }
            step.completed_at = datetime.utcnow()
            db.commit()

            return {
                "status": "failed",
                "message": "LLM execution failed"
            }

        db.refresh(agent)
        db.refresh(step)

        # =========================================
        # GLOBAL KILL DURING EXECUTION
        # =========================================
        if agent.is_killed:
            step.status = "failed"
            step.error_message = "Agent manually stopped during execution"
            step.output_data = {
                "success": False,
                "reason": "global_killed_during_execution"
            }
            step.completed_at = datetime.utcnow()
            db.commit()

            return {
                "status": "stopped",
                "message": "Global runtime halted"
            }

        # =========================================
        # MISSION KILL DURING EXECUTION
        # =========================================
        if step.status == "killed":
            step.error_message = "Mission killed during execution"
            step.output_data = {
                "success": False,
                "reason": "mission_killed_during_execution"
            }
            step.killed_at = datetime.utcnow()
            db.commit()

            return {
                "status": "killed",
                "message": "Mission halted"
            }

        # =========================================
        # MISSION PAUSE DURING EXECUTION
        # =========================================
        if step.status == "paused":
            return {
                "status": "paused",
                "message": "Mission paused during execution"
            }

        # =========================================
        # SAVE TOKEN + COST DATA
        # =========================================
        step.prompt_tokens = int(completion_usage.get("prompt_tokens", 0))
        step.completion_tokens = int(completion_usage.get("completion_tokens", 0))
        step.total_tokens = int(completion_usage.get("total_tokens", 0))
        step.cost = float(completion_usage.get("cost", 0.0))

        agent.total_cost = float((agent.total_cost or 0.0) + completion_usage.get("cost", 0.0))

        # =========================================
        # CREATE USAGE EVENT
        # =========================================
        create_usage_event(
            db=db,
            workspace_id=current_workspace_id,
            agent_id=step.agent_id,
            step_id=step.id,
            event_type="execution_completed",
            status="completed",
            model_used=active_model_target if active_model_target else "environment-default",
            cost=float(completion_usage.get("cost", 0.0)),
            prompt_tokens=int(completion_usage.get("prompt_tokens", 0)),
            completion_tokens=int(completion_usage.get("completion_tokens", 0))
        )

        # =========================================
        # UNIFIED TELEMETRY RETURN SCHEMA
        # =========================================
        llm_telemetry_node = {
            "event_name": "LLM Model Response Generation",
            "status": "SUCCESS",
            "meta": {
                "model_utilized": active_model_target if active_model_target else "gemini-2.5-flash-lite",
                "prompt_tokens_consumed": int(completion_usage.get("prompt_tokens", 0)),
                "completion_tokens_consumed": int(completion_usage.get("completion_tokens", 0)),
                "total_tokens_consumed": int(completion_usage.get("total_tokens", 0)),
                "documents_influencing_final_answer": documents_influencing_list
            }
        }

        result = {
            "success": True,
            "result": output,
            "tier_notification": tier_status_msg,
            "last_executed_step": "generation_completed",
            "query": prompt,
            "rag_telemetry": rag_telemetry_node,
            "llm_telemetry": llm_telemetry_node,
            "telemetry_timeline": [rag_telemetry_node, llm_telemetry_node]
        }

        # 1. Capture current time using a native Python variable first
        execution_end_time = datetime.utcnow()
        step.completed_at = execution_end_time
        
        # 2. Run the math directly using an explicit fallback if started_at isn't loaded
        start_anchor = step.started_at if step.started_at else datetime.utcnow()
        duration_delta = execution_end_time - start_anchor
        
        # 3. Force update the integer value directly into the column mapping
        step.execution_time_ms = int(duration_delta.total_seconds() * 1000)

        # 4. Assign the remaining metadata properties
        step.output_data = result
        step.status = "completed"
        step.error_message = None  
        
        # 5. Force save straight to PostgreSQL disk
        db.commit()
        # =====================================================================

        return {
            "status": "completed",
            "step_id": str(step.id),
            "output": result
        }

    except Exception as e:
        if step:
            # 🟢 Record execution time up to the crash point
            if step.started_at:
                step.completed_at = datetime.utcnow()
                duration_delta = step.completed_at - step.started_at
                step.execution_time_ms = int(duration_delta.total_seconds() * 1000)
            else:
                step.completed_at = datetime.utcnow()

            step.status = "failed"
            step.error_message = str(e)
            step.output_data = {
                "success": False,
                "reason": "exception",
                "error": str(e)
            }
            db.commit()
        raise e

    finally:
        db.close()