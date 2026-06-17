from fastapi import HTTPException
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.models.durable_step import DurableStep
from app.models.workspace_subscription import WorkspaceSubscription


def require_feature(
    workspace,
    feature_name: str
):
    
    # INTERNAL ADMIN BYPASS
    if getattr(workspace, "is_internal", False):

        return True

    subscription = (
        workspace.subscription
    )

    if not subscription:

        raise HTTPException(
            status_code=403,
            detail="No active subscription"
        )

    plan = subscription.plan

    if not plan:

        raise HTTPException(
            status_code=403,
            detail="No active plan"
        )

    features = (
        plan.features or {}
    )

    if not features.get(
        feature_name,
        False
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                f"{feature_name} "
                "not enabled"
            )
        )

    return True


def has_feature(
    workspace,
    feature_name: str
):

    subscription = (
        workspace.subscription
    )

    if not subscription:

        return False

    plan = subscription.plan

    if not plan:

        return False

    features = (
        plan.features or {}
    )

    return features.get(
        feature_name,
        False
    )


def get_feature_limit(
    workspace,
    limit_name: str,
    default=None
):

    subscription = (
        workspace.subscription
    )

    if not subscription:

        return default

    plan = subscription.plan

    if not plan:

        return default

    limits = (
        plan.limits or {}
    )

    return limits.get(
        limit_name,
        default
    )


def require_rag_access(
    workspace,
    db,
    limit_flag_name: str = "enable_rag_documents",
    limit_count_name: str = "max_rag_documents"
):
    """
    Validates that the workspace plan has active RAG capabilities 
    and checks if the current document count falls safely under their subscription limit quota.
    """
    # 1. Internal admin bypass rule
    if getattr(workspace, "is_internal", False):
        return True

    # 2. Extract the plan limits dictionary cleanly
    subscription = getattr(workspace, "subscription", None)
    plan = getattr(subscription, "plan", None) if subscription else None
    limits = getattr(plan, "limits", {}) if plan else {}
    
    if isinstance(limits, str):
        import json
        try:
            limits = json.loads(limits)
        except Exception:
            limits = {}

    # 3. Guard Core Check: See if RAG module access is enabled in limits
    is_rag_enabled = limits.get(limit_flag_name, False)
    if not is_rag_enabled:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="The Advanced Knowledge Base module is exclusively reserved for Pro and Enterprise spaces."
        )

    # 4. Limit Constraint Check: Enforce maximum document storage caps
    max_allowed_docs = limits.get(limit_count_name, 0)
    
    # Import the model inline to avoid circular dependency loops
    from app.models.uploaded_document import UploadedDocument

    current_doc_count = (
        db.query(UploadedDocument)
        .filter(UploadedDocument.workspace_id == workspace.id)
        .count()
    )

    if current_doc_count >= max_allowed_docs:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail=(
                f"Workspace RAG storage full. "
                f"Current={current_doc_count} files, Limit={max_allowed_docs} files. "
                f"Upgrade your plan to expand storage capacity."
            )
        )

    return True

def require_runtime_hours(db, workspace_id: str, plan) -> bool:
    """
    Thread-safe validator checking if a workspace has enough cumulative
    runtime compute hours left in its current monthly or yearly subscription window.
    """
    # 1. Fetch active subscription details to identify the current billing window start date
    subscription = (
        db.query(WorkspaceSubscription)
        .filter(
            WorkspaceSubscription.workspace_id == workspace_id,
            WorkspaceSubscription.status == "active"
        )
        .first()
    )
    
    if not subscription:
        raise HTTPException(status_code=403, detail="No active subscription found.")

    # Self-healing date boundary fallback if billing automation columns aren't populated yet
    billing_period_start = getattr(subscription, "current_period_start", None)
    if not billing_period_start:
        billing_period_start = datetime.utcnow() - timedelta(days=30)

    # 2. Query the relational engine to sum execution time box logs for this specific period
    total_ms_used = (
        db.query(func.sum(DurableStep.execution_time_ms))
        .filter(
            DurableStep.workspace_id == workspace_id,
            DurableStep.created_at >= billing_period_start
        )
        .scalar()
    ) or 0

    # Convert milliseconds back to total fractional compute hours
    total_hours_used = (total_ms_used / 1000) / 3600

    # 3. Pull threshold ceiling constraints directly from the injected plan parameters metadata
    max_allowed_hours = plan.limits.get("max_runtime_hours", 10)

    # 4. Strict Block Gate: If quota is filled, raise payload error immediately
    if total_hours_used >= max_allowed_hours:
        raise HTTPException(
            status_code=402,
            detail=(
                f"Workspace cumulative runtime hours limit exhausted. "
                f"Used: {round(total_hours_used, 2)} hrs, Limit: {max_allowed_hours} hrs. "
                f"Please upgrade your active workspace subscription tier to unlock capacity."
            )
        )
    
    return True