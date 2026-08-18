import time

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.durable_step import DurableStep


def execute_step(
    step: DurableStep,
    db: Session
):

    started_at = time.time()

    step.started_at = datetime.utcnow()

    step.status = "running"

    db.commit()

    try:

        # simulate delay (real-world API call)
        time.sleep(1)

        execution_seconds = (
            time.time() - started_at
        )

        policy = step.agent.policy

        if (
            execution_seconds >
            policy.max_execution_time_seconds
        ):

            raise Exception(
                "Execution timeout exceeded"
            )

        if step.task_name == "fail_task":

            raise Exception(
                "Simulated failure"
            )

        result = {
            "status": "success",
            "task": step.task_name
        }

        step.status = "completed"

        step.output_data = result

        execution_time_ms = int(
            (time.time() - started_at) * 1000
        )

        step.execution_time_ms = (
            execution_time_ms
        )

        step.completed_at = (
            datetime.utcnow()
        )

        step.cost = 0.2

    except Exception as e:

        step.status = "failed"

        step.error_message = str(e)

        step.retry_count += 1

        policy = step.agent.policy

        if (
            policy.enable_retry_control
            and
            step.retry_count >
            policy.max_retries
        ):

            step.status = "killed"

            step.runtime_controlled = True

            step.pause_reason = (
                "Retry limit exceeded"
            )

        step.completed_at = (
            datetime.utcnow()
        )

        step.execution_time_ms = int(
            (time.time() - started_at) * 1000
        )

    db.commit()