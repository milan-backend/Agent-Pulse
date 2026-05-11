def should_stop_agent(
    total_steps: int,
    retry_count: int,
    total_cost: float,
    repeated_task_count: int,
    max_steps: int,
    max_retries: int,
    max_cost: float,
    max_repeated_tasks: int,
):

    # Global safety limits
    GLOBAL_MAX_STEPS = 100000
    GLOBAL_MAX_RETRIES = 1000
    GLOBAL_MAX_COST = 100000.0
    GLOBAL_MAX_REPEATED_TASKS = 10000

    # Effective runtime limits
    effective_max_steps = min(
        max_steps,
        GLOBAL_MAX_STEPS
    )

    effective_max_retries = min(
        max_retries,
        GLOBAL_MAX_RETRIES
    )

    effective_max_cost = min(
        max_cost,
        GLOBAL_MAX_COST
    )

    effective_max_repeated_tasks = min(
        max_repeated_tasks,
        GLOBAL_MAX_REPEATED_TASKS
    )

    # Step explosion
    if total_steps > effective_max_steps:
        return {
            "stop": True,
            "reason": "Step limit exceeded",
            "severity": "high",
            "metric": "steps",
            "current": total_steps,
            "limit": effective_max_steps
        }

    # Retry explosion
    if retry_count > effective_max_retries:
        return {
            "stop": True,
            "reason": "Retry limit exceeded",
            "severity": "high",
            "metric": "retries",
            "current": retry_count,
            "limit": effective_max_retries
        }

    # Cost spike
    if total_cost > effective_max_cost:
        return {
            "stop": True,
            "reason": "Cost limit exceeded",
            "severity": "critical",
            "metric": "cost",
            "current": total_cost,
            "limit": effective_max_cost
        }

    # Infinite loop detection
    if repeated_task_count > effective_max_repeated_tasks:
        return {
            "stop": True,
            "reason": "Infinite loop detected",
            "severity": "critical",
            "metric": "repeated_tasks",
            "current": repeated_task_count,
            "limit": effective_max_repeated_tasks
        }

    # Risk scoring
    risk_score = (
        total_steps * 0.1
        + retry_count * 0.3
        + total_cost * 0.5
        + repeated_task_count * 0.4
    )

    # Abnormal behavior detection
    if risk_score > 1000000:
        return {
            "stop": True,
            "reason": "Abnormal agent behavior detected",
            "severity": "critical",
            "risk_score": round(risk_score, 2)
        }

    # Healthy state
    return {
        "stop": False,
        "reason": "Agent operating normally",
        "severity": "low",
        "risk_score": round(risk_score, 2),
        "limits": {
            "steps": effective_max_steps,
            "retries": effective_max_retries,
            "cost": effective_max_cost,
            "repeated_tasks": effective_max_repeated_tasks
        }
    }