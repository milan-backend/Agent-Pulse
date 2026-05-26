from fastapi import HTTPException


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