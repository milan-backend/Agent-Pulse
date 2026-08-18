from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.usage import Usage


def get_workspace_monthly_cost(
    db: Session,
    workspace_id
):

    now = datetime.utcnow()

    month_start = datetime(
        now.year,
        now.month,
        1
    )

    total = (
        db.query(
            func.sum(Usage.cost)
        )
        .filter(
            Usage.workspace_id ==
            workspace_id,

            Usage.created_at >=
            month_start
        )
        .scalar()
    )

    return float(total or 0)


def is_workspace_over_budget(
    current_cost: float,
    monthly_limit: float
):

    return current_cost >= monthly_limit


def get_remaining_budget(
    current_cost: float,
    monthly_limit: float
):

    remaining = (
        monthly_limit - current_cost
    )

    return max(remaining, 0)


def get_budget_usage_percentage(
    current_cost: float,
    monthly_limit: float
):

    if monthly_limit <= 0:

        return 0

    return round(
        (current_cost / monthly_limit) * 100,
        2
    )