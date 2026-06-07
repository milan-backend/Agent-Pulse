from celery import shared_task
from datetime import datetime
import uuid

from app.db.session import SessionLocal
from app.models.durable_step import DurableStep
from app.models.agent import Agent
from app.models.agent_policy import AgentPolicy
from app.models.user_api_key import UserAPIKey  # Imported safely for hierarchical routing

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
            Agent.workspace_id == current_workspace_id  # Enforces cross-workspace isolation protection
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
            else:
                # --- DYNAMIC STRUCTURAL MODEL TARGET RESOLUTION ---
                agent_id_raw = agent.id if agent else None
                agent_model = getattr(agent, "model_name", None)
                active_model_target = None

                # 1. Check for custom Agent-specific Dropdown Setup
                if agent_id_raw:
                    agent_specific_key = db.query(UserAPIKey).filter(
                        UserAPIKey.agent_id == agent_id_raw,
                        UserAPIKey.workspace_id == current_workspace_id
                    ).first()
                    if agent_specific_key and agent_specific_key.model_version:
                        active_model_target = str(agent_specific_key.model_version).strip()

                # 2. Fallback to General Agent Row Metadata Choice
                if not active_model_target and agent_model and str(agent_model).strip():
                    active_model_target = str(agent_model).strip()

                # 3. Fallback to Workspace Level Settings (Read directly from your user-configured column row)
                if not active_model_target:
                    default_key = db.query(UserAPIKey).filter(
                        UserAPIKey.workspace_id == current_workspace_id,
                        UserAPIKey.is_default == True,
                        UserAPIKey.agent_id == None
                    ).first()

                    if default_key and default_key.model_version:
                        active_model_target = default_key.model_version
                    else:
                        # Fallback directly to the last configured key model version for this workspace
                        any_workspace_key = db.query(UserAPIKey).filter(
                            UserAPIKey.workspace_id == current_workspace_id,
                            UserAPIKey.agent_id == None
                        ).order_by(UserAPIKey.updated_at.desc()).first()
                        
                        if any_workspace_key and any_workspace_key.model_version:
                            active_model_target = any_workspace_key.model_version

                # Run Handshake via the updated hierarchical engine layer 
                # (If active_model_target is None here, llm_service will dynamically resolve it via environment variables)
                output = generate_llm_response(
                    prompt=prompt,
                    db=db,
                    workspace_id=current_workspace_id,
                    agent_id=agent_id_raw,
                    model_name=active_model_target
                )
                
                completion_usage = calculate_usage(
                   prompt=prompt,
                   completion=output,
                   model_name=active_model_target if active_model_target else "gemini-2.5-flash-lite"
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
                # Increment the database tracking counter attribute safely
                step.retry_count = current_retries + 1
                step.status = "pending"
                step.error_message = f"Execution failed, attempting automatic retry ({step.retry_count}/{max_allowed_retries}): {error_message}"
                db.commit()

                # Re-queue the exact same task instance step execution wrapper block smoothly
                process_step.delay(str(step.id))
                
                return {
                    "status": "retrying",
                    "message": f"Step execution failed. Automatic retry tracking re-queued background loop."
                }

            # 3. If retries are disabled or exhausted, permanently fail the tracking node gracefully
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
        # SUCCESS
        # =========================================
        result = {
            "success": True,
            "result": output,
            "usage": completion_usage
        }

        step.output_data = result
        step.status = "completed"
        step.error_message = None  
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