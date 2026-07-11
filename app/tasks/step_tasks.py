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

                # ========================================================
                # ADVANCED HIERARCHICAL CONTEXT RETRIEVAL (RAG LOOKUP)
                # ========================================================
                context_fragments = []
                documents_influencing_list = []
                
                rag_telemetry_node = {
                    "event_name": "KNOWLEDGE_RETRIEVAL",
                    "collection_human_name": "rag_enterprise_vectors_v1",
                    "similarity_threshold_used": 0.45,
                    "query_expansion_time_ms": 0.0,
                    "query_embedding_time_ms": 0.0,
                    "vector_search_time_ms": 0.0,
                    "reranking_and_decay_time_ms": 0.0,
                    "candidate_chunks_evaluated": 0,
                    "chunks_returned_count": 0,
                    "retrieval_similarity_hit_rate_percent": 0.0,
                    "documents": []
                }

                # 🟢 PERMANENT GUARD: Check relational PostgreSQL context before running heavy vector functions
                workspace_document_count = (
                    db.query(UploadedDocument)
                    .filter(UploadedDocument.workspace_id == uuid.UUID(current_workspace_id))
                    .count()
                )

                # 🎯 STRATEGIC OVERRIDE: Skip ChromaDB completely if the workspace has no files uploaded!
                if workspace_document_count == 0:
                    print(f"ℹ️ Workspace {current_workspace_id} has 0 documents. Skipping ChromaDB lookup lane entirely.")
                    rag_telemetry_node["collection_human_name"] = "rag_enterprise_vectors_v1 (No Uploads)"
                else:
                    try:
                        gemini_api_key = os.getenv("GEMINI_API_KEY")
                        
                        if not gemini_api_key and resolved_key_record:
                            from app.core.crypto import decrypt_api_key
                            gemini_api_key = decrypt_api_key(resolved_key_record.encrypted_api_key)

                        if not gemini_api_key:
                            raise ValueError("GEMINI_API_KEY is completely missing on worker container environment")
                            
                        ai_client = genai.Client(api_key=gemini_api_key)
                        
                        # 🚀 TRACK 1: DYNAMIC LOCAL ONTOLOGY QUERY EXPANSION METRIC
                        expansion_start = time.time()
                        enriched_prompt = dynamically_expand_query_intent_local(prompt)
                        rag_telemetry_node["query_expansion_time_ms"] = round((time.time() - expansion_start) * 1000, 3)
                        
                        # 🚀 TRACK 2: VECTOR EMBEDDING GENERATION AND CACHE CHECK METRIC
                        embed_start_time = time.time()
                        cache_hash_key = f"{current_workspace_id}_{hash(enriched_prompt)}"
                        
                        if cache_hash_key in GLOBAL_VECTOR_CACHE:
                            query_vector = GLOBAL_VECTOR_CACHE[cache_hash_key]
                        else:
                            try:
                                query_vector_resp = ai_client.models.embed_content(
                                    model="gemini-embedding-2",
                                    contents=enriched_prompt
                                )
                                query_vector = query_vector_resp.embeddings[0].values
                            except Exception:
                                try:
                                    query_vector_resp = ai_client.models.embed_content(
                                        model="text-embedding-004",
                                        contents=enriched_prompt
                                    )
                                    query_vector = query_vector_resp.embeddings[0].values
                                except Exception:
                                    query_vector_resp = ai_client.models.embed_content(
                                        model="text-embedding-005",
                                        contents=enriched_prompt
                                    )
                                    query_vector = query_vector_resp.embeddings[0].values
                            GLOBAL_VECTOR_CACHE[cache_hash_key] = query_vector
                                
                        rag_telemetry_node["query_embedding_time_ms"] = round((time.time() - embed_start_time) * 1000, 2)
                        
                        # Connect to Chroma DB Collection Space
                        chroma_client = get_chroma_client()
                        collection = chroma_client.get_collection(name="rag_enterprise_vectors_v1")
                        
                        if collection:
                            # 🚀 TRACK 3: CHROMADB RAW VECTOR SPACE RETRIEVAL QUERY
                            search_start_time = time.time()
                            agent_results = collection.query(
                                query_embeddings=[query_vector],
                                n_results=6,
                                where={
                                    "$and": [
                                        {"workspace_id": current_workspace_id},
                                        {"agent_id": str(agent_id_raw)}
                                    ]
                                }
                            )
                            rag_telemetry_node["vector_search_time_ms"] = round((time.time() - search_start_time) * 1000, 2)
                            
                            docs_list = agent_results.get("documents", [[]])[0] if agent_results.get("documents") else []
                            metas_list = agent_results.get("metadatas", [[]])[0] if agent_results.get("metadatas") else []
                            dists_list = agent_results.get("distances", [[]])[0] if agent_results.get("distances") else []
                            
                            rag_telemetry_node["candidate_chunks_evaluated"] = len(docs_list)
                            successful_hits_count = 0

                            if not docs_list:
                                search_start_time = time.time()
                                workspace_results = collection.query(
                                    query_embeddings=[query_vector],
                                    n_results=6,
                                    where={
                                        "$and": [
                                            {"workspace_id": current_workspace_id},
                                            {"agent_id": "None"}
                                        ]
                                    }
                                )
                                rag_telemetry_node["vector_search_time_ms"] += round((time.time() - search_start_time) * 1000, 2)
                                docs_list = workspace_results.get("documents", [[]])[0] if workspace_results.get("documents") else []
                                metas_list = workspace_results.get("metadatas", [[]])[0] if workspace_results.get("metadatas") else []
                                dists_list = workspace_results.get("distances", [[]])[0] if workspace_results.get("distances") else []
                                rag_telemetry_node["candidate_chunks_evaluated"] += len(docs_list)

                            # 🚀 TRACK 4: EXPONENTIAL RE-RANKING MATH ENGINE PERFORMANCE
                            rerank_start = time.time()
                            scored_candidates_list = []
                            for idx, encrypted_chunk in enumerate(docs_list):
                                meta_data = metas_list[idx] if idx < len(metas_list) else {}
                                raw_distance = dists_list[idx] if idx < len(dists_list) else 1.0
                                
                                base_similarity = max(0.0, (1.0 - float(raw_distance)))
                                doc_date_raw = meta_data.get("last_updated", "2026-01-01")
                                try:
                                    chunk_timestamp = datetime.strptime(doc_date_raw[:10], "%Y-%m-%d")
                                    age_hours = (datetime.utcnow() - chunk_timestamp).total_seconds() / 3600.0
                                except Exception:
                                    age_hours = 0.0
                                
                                lambda_decay = 0.005
                                freshness_multiplier = float(2.71828 ** (-lambda_decay * age_hours))
                                final_time_adjusted_score = base_similarity * freshness_multiplier

                                scored_candidates_list.append({
                                    "chunk": encrypted_chunk,
                                    "meta": meta_data,
                                    "base_similarity": base_similarity,
                                    "adjusted_score": final_time_adjusted_score
                                })

                            scored_candidates_list.sort(key=lambda x: x["adjusted_score"], reverse=True)

                            accumulated_chars = 0
                            strict_character_ceiling = 4000
                            
                            for item in scored_candidates_list:
                                normalized_similarity = round(item["base_similarity"] * 100, 2)
                                passes_cutoff = normalized_similarity >= (rag_telemetry_node["similarity_threshold_used"] * 100)
                                
                                if not passes_cutoff:
                                    continue

                                if accumulated_chars >= strict_character_ceiling:
                                    continue
                                    
                                plain_chunk = decrypt_text_string(item["chunk"], uuid.UUID(current_workspace_id))
                                if not plain_chunk:
                                    continue
                                    
                                context_fragments.append(plain_chunk)
                                accumulated_chars += len(plain_chunk)
                                successful_hits_count += 1
                                
                                if item["meta"].get("source_file") and item["meta"]["source_file"] not in documents_influencing_list:
                                    documents_influencing_list.append(str(item["meta"]["source_file"]))

                                rag_telemetry_node["documents"].append({
                                    "chunk_rank": len(context_fragments),
                                    "source_file": item["meta"].get("source_file", "Unknown Source Document"),
                                    "page_number": item["meta"].get("page_number", 1),
                                    "last_updated": item["meta"].get("last_updated", "2026-06-10"),
                                    "uploaded_by_user": item["meta"].get("uploaded_by", "System Operator"),
                                    "similarity_confidence_percentage": normalized_similarity,
                                    "freshness_decay_adjusted_score": round(item["adjusted_score"], 4),
                                    "context_contribution_indicator": True,
                                    "content_snippet": plain_chunk[:250] + "..." if len(plain_chunk) > 250 else plain_chunk
                                })

                            rag_telemetry_node["chunks_returned_count"] = len(rag_telemetry_node["documents"])
                            if rag_telemetry_node["chunks_returned_count"] > 0:
                                rag_telemetry_node["retrieval_similarity_hit_rate_percent"] = round(
                                    (successful_hits_count / rag_telemetry_node["chunks_returned_count"]) * 100, 2
                                )
                                
                            rag_telemetry_node["reranking_and_decay_time_ms"] = round((time.time() - rerank_start) * 1000, 2)

                    except Exception as chroma_err:
                        print(f"⚠️ Vector search exception caught in worker: {str(chroma_err)}")
                        rag_telemetry_node["error_log_report"] = str(chroma_err)

                # Inject decoded context pieces natively into the prompt block
                final_prompt_payload = prompt
                if context_fragments:
                    combined_context = "\n\n".join(context_fragments)
                    final_prompt_payload = (
                        f"CRITICAL CONTEXT DISCOVERED IN SECURITY CORE:\n"
                        f"==================================================\n"
                        f"{combined_context}\n"
                        f"==================================================\n\n"
                        f"USER INSTRUCTION TASK: {prompt}"
                    )

                # 🚀 TRACK 5: RAW LLM NETWORK WORKPLACE GENERATION METRIC
                llm_start_time = time.time()
                
                import redis
                import ssl
                # 🎯 REMOVED local 'import os' to prevent Python variable shadowing!
                
                raw_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                
                # Clean the URL string to strip the problematic query parameter
                if "?ssl_cert_reqs=CERT_NONE" in raw_redis_url:
                    redis_url_str = raw_redis_url.split("?")[0]
                else:
                    redis_url_str = raw_redis_url
                
                ssl_options = {}
                if redis_url_str.startswith("rediss://"):
                    ssl_options["ssl_cert_reqs"] = ssl.CERT_NONE
                
                redis_client = redis.Redis.from_url(redis_url_str, **ssl_options)
                
                # 🎯 Fix the unbound local variable error: Resolve key safely right here inline
                if 'gemini_api_key' not in locals() or not gemini_api_key:
                    gemini_api_key = os.getenv("GEMINI_API_KEY")
                    if not gemini_api_key and resolved_key_record:
                        from app.core.crypto import decrypt_api_key
                        gemini_api_key = decrypt_api_key(resolved_key_record.encrypted_api_key)

                if not gemini_api_key:
                    raise ValueError("CRITICAL: GEMINI_API_KEY could not be resolved for streaming pipeline initialization.")

                # Initialize the official GenAI streaming interface
                ai_client = genai.Client(api_key=gemini_api_key)
                
                try:
                    response_stream = ai_client.models.generate_content_stream(
                        model=active_model_target,
                        contents=final_prompt_payload
                    )
                    
                    # Iterate through individual chunks as they come from the Gemini GPU chips
                    output_fragments = []
                    for chunk in response_stream:
                        if chunk.text:
                            output_fragments.append(chunk.text)
                            # Broadcast the word token chunk immediately via Pub/Sub to the frontend listener
                            redis_client.publish(f"stream:{str(step.id)}", chunk.text)
                    
                    # Combine fragments into the full response string for your database tracking metrics
                    output = "".join(output_fragments)
                    
                    # Publish the special signature token indicating the stream has finished successfully
                    redis_client.publish(f"stream:{str(step.id)}", "[DONE]")
                    
                except Exception as stream_execution_error:
                    error_str = str(stream_execution_error)
                    # 🎯 BYOK Rate Limit Intercept Logic: Catch 429 only if running on system tier
                    if "429" in error_str and tier_source == "system":
                        friendly_msg = "⚠️ The system shared sandbox tier key has exhausted its rate limit bounds. Please add your own custom Gemini API Key inside your dashboard settings workspace panel to bypass cluster congestion."
                        redis_client.publish(f"stream:{str(step.id)}", friendly_msg)
                        redis_client.publish(f"stream:{str(step.id)}", "[DONE]")
                        raise ValueError(friendly_msg)
                    raise stream_execution_error
                
                llm_generation_latency_ms = round((time.time() - llm_start_time) * 1000, 2)
                
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
            "llm_generation_network_time_ms": llm_generation_latency_ms,
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