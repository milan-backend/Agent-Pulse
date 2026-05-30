from app.db.session import SessionLocal
from app.models.durable_step import DurableStep

db = SessionLocal()

try:
    count = (
        db.query(DurableStep)
        .filter(
            DurableStep.task_name == "ping"
        )
        .count()
    )

    print(f"Ping steps: {count}")

finally:
    db.close()