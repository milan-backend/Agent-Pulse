from celery import shared_task

from datetime import datetime

from app.db.session import SessionLocal

from app.models.durable_step import DurableStep
from app.models.agent import Agent
from app.models.agent_policy import AgentPolicy

from app.services.llm_service import (
    generate_llm_response
)

from app.services.tokenizer_service import (
    calculate_usage
)


@shared_task(bind=True, max_retries=3)
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

            step.error_message = (
                "Agent not found"
            )

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

        step.started_at = (
            datetime.utcnow()
        )

        db.commit()

        # REFRESH STATE

        db.refresh(agent)

        # =========================================
        # GLOBAL EMERGENCY STOP
        # =========================================

        if agent.is_killed:

            step.status = "failed"

            step.error_message = (
                "Agent manually stopped"
            )

            step.output_data = {
                "success": False,
                "reason": "global_killed"
            }

            step.completed_at = (
                datetime.utcnow()
            )

            db.commit()

            return {
                "status": "stopped",
                "message":
                    "Global agent execution halted"
            }

        # =========================================
        # MISSION LEVEL KILL
        # =========================================

        db.refresh(step)

        if step.status == "killed":

            step.error_message = (
                "Mission manually killed"
            )

            step.output_data = {
                "success": False,
                "reason": "mission_killed"
            }

            step.killed_at = (
                datetime.utcnow()
            )

            db.commit()

            return {
                "status": "killed",
                "message":
                    "Mission execution halted"
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

                DurableStep.status.in_([
                    "pending",
                    "running"
                ])
            )
            .count()
        )

        if (
            policy and
            current_step_count >= policy.max_steps
        ):

            step.status = "failed"

            step.error_message = (
                "Max step limit reached"
            )

            step.output_data = {
                "success": False,
                "reason": "max_steps_exceeded"
            }

            step.completed_at = (
                datetime.utcnow()
            )

            db.commit()

            return {
                "status": "failed",
                "message":
                    "Max step limit reached"
            }

        # =========================================
        # REAL AI EXECUTION
        # =========================================

        try:

            output = generate_llm_response(
                prompt=str(step.input_data),
                model_name="gemini-2.0-flash"
            )

            completion_usage = calculate_usage(
                prompt="",
                completion=output,
                model_name="gemini-2.0-flash"
            )

        except Exception as llm_error:

            step.status = "failed"

            step.error_message = (
                f"LLM execution failed: {str(llm_error)}"
            )

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

            step.error_message = (
                "Agent manually stopped during execution"
            )

            step.output_data = {
                "success": False,
                "reason":
                    "global_killed_during_execution"
            }

            step.completed_at = (
                datetime.utcnow()
            )

            db.commit()

            return {
                "status": "stopped",
                "message":
                    "Global runtime halted"
            }

        # =========================================
        # MISSION KILL DURING EXECUTION
        # =========================================

        if step.status == "killed":

            step.error_message = (
                "Mission killed during execution"
            )

            step.output_data = {
                "success": False,
                "reason":
                    "mission_killed_during_execution"
            }

            step.killed_at = (
                datetime.utcnow()
            )

            db.commit()

            return {
                "status": "killed",
                "message":
                    "Mission halted"
            }

        # =========================================
        # MISSION PAUSE DURING EXECUTION
        # =========================================

        if step.status == "paused":

            return {
                "status": "paused",
                "message":
                    "Mission paused during execution"
            }

        # =========================================
        # SUCCESS
        # =========================================

        result = {

            "success": True,

            "result": output
        }

        step.output_data = result

        step.status = "completed"

        step.completed_at = (
            datetime.utcnow()
        )

        db.commit()

        return {

            "status":
                "completed",

            "step_id":
                step.id,

            "agent_id":
                agent.id,

            "output":
                result
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

            step.completed_at = (
                datetime.utcnow()
            )

            db.commit()

        raise e

    finally:

        db.close()