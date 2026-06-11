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

from app.services.llm_service import generate_llm_response
from app.services.tokenizer_service import calculate_usage
from app.services.usage_service import create_usage_event
from app.services.user_api_key_service import UserAPIKeyService

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
            prompt = ""
            if isinstance(step.input_data, dict):
                prompt = step.input_data.get("prompt", "")
            else:
                prompt = str(step.input_data)

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
            else:
                # ========================================================
                # UPGRADED MULTI-PROVIDER MODEL & CREDENTIAL LOOKUP ENGINE
                # ========================================================
                agent_id_raw = agent.id if agent else None
                agent_model = getattr(agent, "model_name", None)
                active_model_target = None
                
                # Identify engine provider target requested by agent row configuration
                agent_model_clean = str(agent_model).lower().strip() if agent_model else ""
                requested_engine = "openai" if ("gpt" in agent_model_clean or "openai" in agent_model_clean) else "gemini"

                resolved_key_record = None
                if agent_id_raw:
                    # Run the recursive priority check: Agent-Specific -> Assigned Workspace -> Global Workspace -> System
                    resolved_key_record = UserAPIKeyService.resolve_agent_api_key(
                        db=db,
                        workspace_id=uuid.UUID(current_workspace_id),
                        agent_id=agent_id_raw,
                        provider_type=requested_engine
                    )

                    if resolved_key_record and resolved_key_record.model_name:
                        active_model_target = str(resolved_key_record.model_name).strip()

                # Fallback to Agent Meta Configuration Choice if resolver did not explicitly lock model names
                if not active_model_target and agent_model and str(agent_model).strip():
                    active_model_target = str(agent_model).strip()

                # Absolute baseline structural fallback if completely unconfigured
                if not active_model_target:
                    active_model_target = "gpt-4o-mini" if requested_engine == "openai" else "gemini-2.5-flash-lite"

                # 🛡️ SECURITY CONTROL UPGRADE BLOCK: ENFORCE ZERO-TRUST TASK ISOLATION BOUNDARY
                # If a specific agent task execution loop is running, and the database tracking resolver returns None,
                # and no server system variables are present, we must block the loop right here before calling generation.
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
                
                # Base structure matching your observability requirements without ID noise
                rag_telemetry_node = {
                    "event_name": "KNOWLEDGE_RETRIEVAL",
                    "collection_human_name": "rag_enterprise_vectors_v1",
                    "similarity_threshold_used": 0.45,  # 🎯 Lowered to 45% production gate to accept dense matches
                    "query_embedding_time_ms": 0.0,
                    "vector_search_time_ms": 0.0,
                    "candidate_chunks_evaluated": 0,
                    "chunks_returned_count": 0,
                    "retrieval_similarity_hit_rate_percent": 0.0,
                    "documents": []
                }

                try:
                    # Initialize the official Google GenAI SDK client for the query vector match
                    gemini_api_key = os.getenv("GEMINI_API_KEY")
                    
                    # Fallback to the resolved database credential string if the environment is empty for RAG lookups
                    if not gemini_api_key and resolved_key_record:
                        from app.core.crypto import decrypt_api_key
                        gemini_api_key = decrypt_api_key(resolved_key_record.encrypted_api_key)

                    if not gemini_api_key:
                        raise ValueError("GEMINI_API_KEY is completely missing on worker container environment")
                        
                    ai_client = genai.Client(api_key=gemini_api_key)
                    
                    # -----------------------------------------------------------------
                    # 🚀 STEP A: Self-Healing Multi-Model Fallback Vector Query Engine
                    # -----------------------------------------------------------------
                    embed_start_time = time.time()
                    query_vector = None
                    
                    try:
                        query_vector_resp = ai_client.models.embed_content(
                            model="gemini-embedding-2",
                            contents=prompt
                        )
                        query_vector = query_vector_resp.embeddings[0].values
                    except Exception:
                        try:
                            query_vector_resp = ai_client.models.embed_content(
                                model="text-embedding-004",
                                contents=prompt
                            )
                            query_vector = query_vector_resp.embeddings[0].values
                        except Exception:
                            query_vector_resp = ai_client.models.embed_content(
                                model="text-embedding-005",
                                contents=prompt
                            )
                            query_vector = query_vector_resp.embeddings[0].values
                            
                    rag_telemetry_node["query_embedding_time_ms"] = round((time.time() - embed_start_time) * 1000, 2)
                    
                    # -----------------------------------------------------------------
                    # 🚀 STEP B: Connect to Chroma DB Collection Space
                    # -----------------------------------------------------------------
                    chroma_client = get_chroma_client()
                    collection = chroma_client.get_collection(name="rag_enterprise_vectors_v1")
                    
                    if collection:
                        search_start_time = time.time()
                        # Multi-tenant scoping logic filter queries
                        agent_results = collection.query(
                            query_embeddings=[query_vector],
                            n_results=4,
                            where={
                                "$and": [
                                    {"workspace_id": current_workspace_id},
                                    {"agent_id": str(agent_id_raw)}
                                ]
                            }
                        )
                        rag_telemetry_node["vector_search_time_ms"] = round((time.time() - search_start_time) * 1000, 2)
                        
                        # Unpack internal arrays safely
                        docs_list = agent_results.get("documents", [[]])[0] if agent_results.get("documents") else []
                        metas_list = agent_results.get("metadatas", [[]])[0] if agent_results.get("metadatas") else []
                        dists_list = agent_results.get("distances", [[]])[0] if agent_results.get("distances") else []
                        
                        rag_telemetry_node["candidate_chunks_evaluated"] = len(docs_list)
                        successful_hits_count = 0

                        # Check general fallback workspace pool if agent query returned zero records
                        if not docs_list:
                            search_start_time = time.time()
                            workspace_results = collection.query(
                                query_embeddings=[query_vector],
                                n_results=4,
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

                        # -----------------------------------------------------------------
                        # 🚀 STEP C: Evaluate True Cosine Similarities & Extract Text Data
                        # -----------------------------------------------------------------
                        for idx, encrypted_chunk in enumerate(docs_list):
                            meta_data = metas_list[idx] if idx < len(metas_list) else {}
                            raw_distance = dists_list[idx] if idx < len(dists_list) else 1.0
                            
                            normalized_similarity = round(max(0.0, (1.0 - float(raw_distance))) * 100, 2)
                            passes_cutoff = normalized_similarity >= (rag_telemetry_node["similarity_threshold_used"] * 100)
                            
                            plain_chunk = "Decryption Suppressed"
                            if passes_cutoff:
                                plain_chunk = decrypt_text_string(encrypted_chunk, uuid.UUID(current_workspace_id))
                                if not plain_chunk:
                                    continue
                                    
                                context_fragments.append(plain_chunk)
                                successful_hits_count += 1
                                if meta_data.get("source_file") and meta_data["source_file"] not in documents_influencing_list:
                                    documents_influencing_list.append(str(meta_data["source_file"]))

                            # Append itemized logs profile maps
                            rag_telemetry_node["documents"].append({
                                "chunk_rank": idx + 1,
                                "source_file": meta_data.get("source_file", "Unknown Source Document"),
                                "page_number": meta_data.get("page_number", 1),
                                "last_updated": meta_data.get("last_updated", "2026-06-10"),
                                "uploaded_by_user": meta_data.get("uploaded_by", "System Operator"),
                                "similarity_confidence_percentage": normalized_similarity,
                                "context_contribution_indicator": passes_cutoff,
                                "content_snippet": plain_chunk[:250] + "..." if len(plain_chunk) > 250 else plain_chunk
                            })

                        rag_telemetry_node["chunks_returned_count"] = len(rag_telemetry_node["documents"])
                        
                        if rag_telemetry_node["chunks_returned_count"] > 0:
                            rag_telemetry_node["retrieval_similarity_hit_rate_percent"] = round(
                                (successful_hits_count / rag_telemetry_node["chunks_returned_count"]) * 100, 2
                            )

                except Exception as chroma_err:
                    print(f"⚠️ Vector search bypassed or uninitialized safely: {str(chroma_err)}")
                    rag_telemetry_node["error_log_report"] = str(chroma_err)

                # Inject decoded context pieces natively into the instruction system prompt block
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

                # Run Handshake via the updated hierarchical engine layer 
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

        # REFRESH STATES
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
            "telemetry_timeline": [rag_telemetry_node, llm_telemetry_node]
        }

        step.output_data = result
        step.status = "completed"
        step.error_message = None  
        step.completed_at = datetime.utcnow()
        db.commit()

        return {
            "status": "completed",
            "step_id": str(step.id),
            "output": result
        }

    except Exception as e:
        if step:
            step.status = "failed"
            step.error_message = str(e)
            step.output_data = {
                "success": False,
                "reason": "exception",
                "error": str(e)
            }
            step.completed_at = datetime.utcnow()
            db.commit()
        raise e

    finally:
        db.close()