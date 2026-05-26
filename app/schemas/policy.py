# ============================================
# app/schemas/policy.py
# ============================================

from pydantic import BaseModel


class AgentPolicyUpdateRequest(
    BaseModel
):

    max_steps: int

    max_retries: int

    max_cost: float

    max_repeated_tasks: int