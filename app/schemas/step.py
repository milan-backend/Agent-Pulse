from pydantic import BaseModel
from typing import Dict


class StepExecuteRequest(BaseModel):
    task_name: str
    input_data: Dict
    idempotency_key: str