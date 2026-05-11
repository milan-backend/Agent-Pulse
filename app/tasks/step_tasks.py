from app.core.celery_app import celery
from app.db.session import SessionLocal
from app.models.durable_step import DurableStep
from app.models.agent import Agent

from datetime import datetime
import time


@celery.task(bind=True, max_retries=3)
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

        # Mark step as running
        step.status = "running"
        db.commit()

        # Re-fetch latest agent state
        db.refresh(agent)

        # Emergency stop check BEFORE execution
        if agent.is_killed:
            step.status = "failed"
            step.error_message = "Agent manually stopped"

            step.output_data = {
                "success": False,
                "reason": "killed"
            }

            step.completed_at = datetime.utcnow()

            db.commit()

            return {
                "status": "stopped",
                "message": "Agent execution halted"
            }

        # Dynamic max step check
        current_step_count = db.query(DurableStep).filter(
            DurableStep.agent_id == agent.id,
            DurableStep.status.in_(["pending", "running"])
        ).count()

        if current_step_count >= agent.max_steps:
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

        # Simulated task work
        time.sleep(2)

        # Re-fetch latest state AFTER execution starts
        db.refresh(agent)

        # Emergency stop DURING execution
        if agent.is_killed:
            step.status = "failed"
            step.error_message = "Agent manually stopped during execution"

            step.output_data = {
                "success": False,
                "reason": "killed_during_execution"
            }

            step.completed_at = datetime.utcnow()

            db.commit()

            return {
                "status": "stopped",
                "message": "Agent killed during execution",
                "agent_id": agent.id,
                "step_id": step.id
            }

        # Successful completion
        result = {
            "success": True,
            "result": "task completed"
        }

        step.output_data = result
        step.status = "completed"
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