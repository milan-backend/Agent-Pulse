from typing import Dict, Any

from pydantic import BaseModel


class StepExecuteRequest(BaseModel):

    task_name: str

    input_data: Dict[str, Any]

    idempotency_key: str