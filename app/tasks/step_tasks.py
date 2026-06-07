from celery import shared_task
from datetime import datetime
import uuid

from app.db.session import SessionLocal
from app.models.durable_step import DurableStep
from app.models.agent import Agent
from app.models.agent_policy import AgentPolicy
from app.models.user_api_key import UserAPIKey  # Imported safely for multi-tier routing

from app.services.llm_service import generate_llm_response
from app.services.tokenizer_service import calculate_usage
from app.services.usage_service import create_usage_event

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

        # =========================================
        # GET AGENT
        # =========================================
        agent = db.query(Agent).filter(
            Agent.id == step.agent_id
        ).first()

        if not agent:
            step.status = "failed"
            step.error_message = "Agent not found"
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
        # REAL MULTI-PROVIDER AI EXECUTION
        # =========================================
        try:
            prompt = ""
            if isinstance(step.input_data, dict):
                prompt = step.input_data.get("prompt", "")
            else:
                prompt = str(step.input_data)

            # --- DYNAMIC 3-TIER ROUTING RESOLUTION PIPELINE ---
            current_workspace_id = str(step.workspace_id).strip() if step.workspace_id else None
            agent_id_raw = agent.id if agent else None
            agent_model = getattr(agent, "model_name", None)
            
            active_model_target = None

            # -----------------------------------------------------------------
            # TIER 1: Check for explicit Private Agent-Specific API Credentials
            # -----------------------------------------------------------------
            if agent_id_raw:
                agent_specific_key = db.query(UserAPIKey).filter(
                    UserAPIKey.agent_id == agent_id_raw
                ).first()
                if agent_specific_key and agent_specific_key.model_version:
                    active_model_target = str(agent_specific_key.model_version).strip()

            # -----------------------------------------------------------------
            # TIER 2: Fallback to Tenant Workspace Level Configurations
            # -----------------------------------------------------------------
            if not active_model_target:
                if agent_model and str(agent_model).strip():
                    active_model_target = str(agent_model).strip()
                elif current_workspace_id:
                    # 1. Primary Check: Look up key marked default via active UI button state
                    default_key = db.query(UserAPIKey).filter(
                        UserAPIKey.workspace_id == current_workspace_id,
                        UserAPIKey.is_default == True,
                        UserAPIKey.agent_id == None
                    ).first()

                    if default_key:
                        # Grab chosen version completely dynamically from your saved column row!
                        active_model_target = default_key.model_version if default_key.model_version else (
                            "gpt-4o-mini" if "OPENAI" in default_key.provider.upper() else "gemini-2.5-flash-lite"
                        )
                    else:
                        # 2. Secondary Fallback Check: Use older sequential detection if no button is selected
                        has_openai = db.query(UserAPIKey).filter(
                            UserAPIKey.workspace_id == current_workspace_id,
                            UserAPIKey.provider.ilike("%OPENAI%"),
                            UserAPIKey.agent_id == None
                        ).first()
                        
                        has_gemini = db.query(UserAPIKey).filter(
                            UserAPIKey.workspace_id == current_workspace_id,
                            UserAPIKey.provider.ilike("%GEMINI%"),
                            UserAPIKey.agent_id == None
                        ).first()

                        if has_openai:
                            active_model_target = has_openai.model_version or "gpt-4o-mini"
                        elif has_gemini:
                            active_model_target = has_gemini.model_version or "gemini-2.5-flash-lite"

                # 3. Flat personal context layer fallback if workspace elements are empty
                if not active_model_target:
                    current_user_id = agent.user_id if hasattr(agent, 'user_id') else None
                    default_personal_key = db.query(UserAPIKey).filter(
                        UserAPIKey.user_id == current_user_id,
                        UserAPIKey.is_default == True,
                        UserAPIKey.agent_id == None,
                        UserAPIKey.workspace_id == None
                    ).first() if current_user_id else None

                    if default_personal_key:
                        active_model_target = default_personal_key.model_version or (
                            "gpt-4o-mini" if "OPENAI" in default_personal_key.provider.upper() else "gemini-2.5-flash-lite"
                        )
                    else:
                        has_personal_openai = db.query(UserAPIKey).filter(
                            UserAPIKey.user_id == current_user_id,
                            UserAPIKey.provider.ilike("%OPENAI%"),
                            UserAPIKey.agent_id == None,
                            UserAPIKey.workspace_id == None
                        ).first() if current_user_id else None

                        if has_personal_openai:
                            active_model_target = has_personal_openai.model_version or "gpt-4o-mini"
                        else:
                            has_personal_gemini = db.query(UserAPIKey).filter(
                                UserAPIKey.user_id == current_user_id,
                                UserAPIKey.provider.ilike("%GEMINI%"),
                                UserAPIKey.agent_id == None,
                                UserAPIKey.workspace_id == None
                            ).first() if current_user_id else None
                            if has_personal_gemini:
                                active_model_target = has_personal_gemini.model_version or "gemini-2.5-flash-lite"

            # -----------------------------------------------------------------
            # TIER 3: Absolute Last Resort Server Testing Variables Fallback
            # -----------------------------------------------------------------
            if not active_model_target:
                # If there are zero keys found across the tables, safely use testing targets
                active_model_target = "gemini-2.5-flash-lite"

            # Execute response collection loops
            if not prompt or not str(prompt).strip():
                output = "No prompt provided. LLM execution skipped"
                completion_usage = {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0
                }
            else:
                output = generate_llm_response(
                    prompt=prompt,
                    db=db,
                    user_id=agent.user_id if hasattr(agent, 'user_id') else None,
                    workspace_id=current_workspace_id,
                    agent_id=agent_id_raw,  # Passed cleanly to match Tier 1 keys inside services layer
                    model_name=active_model_target
                )
                
                completion_usage = calculate_usage(
                   prompt=prompt,
                   completion=output,
                   model_name=active_model_target
                )

        except Exception as llm_error:
            error_message = str(llm_error)

            # 1. Handle explicit 429 Rate Limits using Celery exponential backoff infrastructure
            if "429" in error_message:
                retry_count = self.request.retries
                countdown = 2 ** retry_count
                raise self.retry(exc=llm_error, countdown=countdown)

            # 2. Handle general exceptions matching the user's policy max_retries budget
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

            # 3. Permanent failure state mapping
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
        # CREATE USAGE EVENT (DYNAMIC MODEL RECORDING)
        # =========================================
        create_usage_event(
            db=db,
            workspace_id=current_workspace_id,
            agent_id=step.agent_id,
            step_id=step.id,
            event_type="execution_completed",
            status="completed",
            model_used=active_model_target,
            cost=float(completion_usage.get("cost", 0.0)),
            prompt_tokens=int(completion_usage.get("prompt_tokens", 0)),
            completion_tokens=int(completion_usage.get("completion_tokens", 0))
        )

        # =========================================
        # SUCCESS (UPDATED WITH AUTOMATIC ERROR WIPEOUT)
        # =========================================
        result = {
            "success": True,
            "result": output,
            "usage": completion_usage
        }

        step.output_data = result
        step.status = "completed"
        step.error_message = None  # Cleans up any old retry errors perfectly on final success!
        step.completed_at = datetime.utcnow()
        db.commit()

        return {
            "status": "completed",
            "step_id": step.id,
            "agent_id": agent.id,
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