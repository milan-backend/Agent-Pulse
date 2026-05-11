import time
from sqlalchemy.orm import Session
from app.models.durable_step import DurableStep


def execute_task(step: DurableStep, db: Session):
    try:
        #  simulate delay (real-world API call)
        time.sleep(3)

        if step.task_name == "fail_task":
            raise Exception("Simulated failure")

        result = {
            "status": "success",
            "task": step.task_name
        }

        step.status = "completed"
        step.output_data = result

    except Exception as e:
        step.status = "failed"
        step.error_message = str(e)
        step.retry_count += 1

    db.commit()