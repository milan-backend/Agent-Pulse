GLOBAL_MAX_STEPS = 100000
GLOBAL_MAX_RETRIES = 1000
GLOBAL_MAX_COST = 100000.0
GLOBAL_MAX_REPEATED_TASKS = 10000

def evaluate_agent_runtime(
    total_steps: int,
    retry_count: int,
    total_cost: float,
    repeated_task_count: int,
    execution_time_seconds: int,

    max_steps: int,
    max_retries: int,
    max_cost: float,
    max_repeated_tasks: int,
    max_execution_time_seconds: int,

    enable_budget_control: bool,
    enable_retry_control: bool,
    enable_loop_detection: bool,
):
    # Effective runtime limits validation matching fallback thresholds
    effective_max_steps = min(max_steps, GLOBAL_MAX_STEPS)
    effective_max_retries = min(max_retries, GLOBAL_MAX_RETRIES)
    effective_max_cost = min(max_cost, GLOBAL_MAX_COST)
    effective_max_repeated_tasks = min(max_repeated_tasks, GLOBAL_MAX_REPEATED_TASKS)

    # Step explosion evaluation
    if total_steps > effective_max_steps:
        return {
            "stop": True,
            "reason": "Step limit exceeded",
            "severity": "high",
            "metric": "steps",
            "current": total_steps,
            "limit": effective_max_steps
        }

    # Retry explosion check (Now safely capturing automatic loops)
    if (
        enable_retry_control
        and retry_count > effective_max_retries
    ):
        return {
            "stop": True,
            "reason": "Retry limit exceeded",
            "severity": "high",
            "metric": "retries",
            "current": retry_count,
            "limit": effective_max_retries
        }

    # Cost spike tracker
    if (
        enable_budget_control
        and total_cost > effective_max_cost
    ):
        return {
            "stop": True,
            "reason": "Cost limit exceeded",
            "severity": "critical",
            "metric": "cost",
            "current": total_cost,
            "limit": effective_max_cost
        }

    # Infinite loop anomaly detection matching repeated limits
    if (
        enable_loop_detection
        and repeated_task_count > effective_max_repeated_tasks
    ):
        return {
            "stop": True,
            "reason": "Infinite loop detected",
            "severity": "critical",
            "metric": "repeated_tasks",
            "current": repeated_task_count,
            "limit": effective_max_repeated_tasks
        }

    # Execution timeouts validation boundaries
    if execution_time_seconds > max_execution_time_seconds:
        return {
            "stop": True,
            "reason": "Execution timeout exceeded",
            "severity": "critical",
            "metric": "execution_time",
            "current": execution_time_seconds,
            "limit": max_execution_time_seconds
        }

    # Composite risk scoring calculation metric checks
    risk_score = (
        total_steps * 0.1
        + retry_count * 0.3
        + total_cost * 0.5
        + repeated_task_count * 0.4
    )

    # Abnormal behavior detection verification
    if risk_score > 1000000:
        return {
            "stop": True,
            "reason": "Abnormal agent behavior detected",
            "severity": "critical",
            "risk_score": round(risk_score, 2)
        }

    # Healthy state recovery response
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
