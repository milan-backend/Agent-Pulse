from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header
)

from sqlalchemy.orm import Session
from sqlalchemy import func  # 🟢 NEW: Imported safely for cumulative step runtime metrics aggregation

from app.db.session import get_db

from app.models.user import User
from app.models.agent import Agent
from app.models.workspace import Workspace
from app.models.agent_policy import AgentPolicy
from app.models.durable_step import DurableStep
from app.models.usage import Usage
from app.tasks.step_tasks import process_step

from app.api.deps_user import (
    get_current_user
)

from app.core.workspace_access import (
    get_workspace_membership
)

from app.services.feature_access import (
    require_feature
)

from app.services.analytics_service import (
    get_workspace_agent_ids,
    get_total_cost,
    get_token_analytics
)

router = APIRouter()


# ============================================
# VALIDATE FEATURE ACCESS
# ============================================

def validate_feature_access(
    db,
    workspace_id,
    feature_name
):

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if not workspace:

        raise HTTPException(
            status_code=404,
            detail="Workspace not found"
        )

    require_feature(
        workspace,
        feature_name
    )


# ============================================
# DASHBOARD SUMMARY
# ============================================

@router.get("/summary")
def dashboard_summary(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    validate_feature_access(
        db,
        workspace_id,
        "analytics"
    )

    # GET AGENT IDS

    agent_ids = get_workspace_agent_ids(
        db,
        workspace_id
    )

    # TOTAL STEPS

    total_steps = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(
                agent_ids
            )
        )
        .count()
    )

    # COMPLETED

    completed = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(
                agent_ids
            ),

            DurableStep.status ==
            "completed"
        )
        .count()
    )

    # FAILED

    failed = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(
                agent_ids
            ),

            DurableStep.status ==
            "failed"
        )
        .count()
    )

    # PENDING

    pending = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(
                agent_ids
            ),

            DurableStep.status.in_([
                "pending",
                "running"
            ])
        )
        .count()
    )

    # SUCCESS RATE

    success_rate = (
        (completed / total_steps) * 100
        if total_steps > 0
        else 0
    )

    return {

        "total_steps":
            total_steps,

        "completed":
            completed,

        "failed":
            failed,

        "pending":
            pending,

        "success_rate":
            round(
                success_rate,
                2
            )
    }


# ============================================
# USAGE SUMMARY
# ============================================

@router.get("/usage")
def usage_summary(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    validate_feature_access(
        db,
        workspace_id,
        "usage_logs"
    )

    # GET AGENT IDS

    agent_ids = get_workspace_agent_ids(
        db,
        workspace_id
    )

    # TOTAL CALLS

    total_calls = (
        db.query(Usage)
        .filter(
            Usage.agent_id.in_(
                agent_ids
            )
        )
        .count()
    )

    # EXECUTIONS

    executions = (
        db.query(Usage)
        .filter(
            Usage.agent_id.in_(
                agent_ids
            ),

            Usage.action ==
            "execute"
        )
        .count()
    )

    # RETRIES

    retries = (
        db.query(Usage)
        .filter(
            Usage.agent_id.in_(
                agent_ids
            ),

            Usage.action ==
            "retry"
        )
        .count()
    )

    # CACHE HITS

    cache_hits = (
        db.query(Usage)
        .filter(
            Usage.agent_id.in_(
                agent_ids
            ),

            Usage.action ==
            "cache_hit"
        )
        .count()
    )

    # TOTAL COST

    total_cost = get_total_cost(
        db,
        agent_ids
    )

    # TOKEN ANALYTICS

    token_data = get_token_analytics(
        db,
        agent_ids
    )

    return {

        "total_calls":
            total_calls,

        "executions":
            executions,

        "retries":
            retries,

        "cache_hits":
            cache_hits,

        "total_cost":
            round(
                total_cost,
                4
            ),

        "prompt_tokens":
            token_data[
                "prompt_tokens"
            ],

        "completion_tokens":
            token_data[
                "completion_tokens"
            ],

        "total_tokens":
            token_data[
                "total_tokens"
            ]
    }


# ============================================
# LIST STEPS
# ============================================

@router.get("/steps")
def list_steps(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    validate_feature_access(
        db,
        workspace_id,
        "missions"
    )

    # GET AGENT IDS

    agent_ids = get_workspace_agent_ids(
        db,
        workspace_id
    )

    # GET STEPS

    steps = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id.in_(
                agent_ids
            )
        )
        .order_by(
            DurableStep.created_at.desc()
        )
        .limit(20)
        .all()
    )

    return steps


# ============================================
# USAGE LOGS
# ============================================

@router.get("/usage/logs")
def usage_logs(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    validate_feature_access(
        db,
        workspace_id,
        "usage_logs"
    )

    # GET AGENT IDS

    agent_ids = get_workspace_agent_ids(
        db,
        workspace_id
    )

    # GET LOGS

    logs = (
        db.query(Usage)
        .filter(
            Usage.agent_id.in_(
                agent_ids
            )
        )
        .order_by(
            Usage.created_at.desc()
        )
        .limit(50)
        .all()
    )

    return logs


# ============================================
# SINGLE AGENT DETAILS
# ============================================

@router.get("/agent/{agent_id}")
def get_agent_by_id(

    agent_id: str,

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # FIND AGENT

    agent = (
        db.query(Agent)
        .filter(
            Agent.id == agent_id,

            Agent.workspace_id ==
            workspace_id
        )
        .first()
    )

    if not agent:

        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    policy = (
        db.query(AgentPolicy)
        .filter(
            AgentPolicy.agent_id ==
            agent.id
        )
        .first()
    )

    # TOTAL MISSIONS

    mission_count = (
        db.query(DurableStep)
        .filter(
            DurableStep.agent_id ==
            agent.id
        )
        .count()
    )

    # TOTAL COST

    usage_records = (
        db.query(Usage)
        .filter(
            Usage.agent_id ==
            agent.id
        )
        .all()
    )

    total_cost = sum(
        record.cost or 0
        for record in usage_records
    )

    return {

        "agent": {

        "id":
            str(agent.id),

        "name":
            agent.name,

        "status":
            agent.status,

        "is_active":
            agent.is_active,

        "created_at":
            agent.created_at
        },

        "policy":{
            "max_cost":
                policy.max_cost
                if policy else 5,

            "max_steps":
                policy.max_steps
                if policy else 20,

            "max_retries":
                policy.max_retries
                if policy else 3,

            "max_repeated_tasks":
                policy.max_repeated_tasks
                if policy else 3
        },

        "mission_count":
            mission_count,

        "total_cost":
            round(total_cost,4)
    }


# ============================================
# GET AGENTS (DYNAMIC SUBSCRIBER BOUNDARIES ADJUSTED)
# ============================================

@router.get("/agents")
def get_agents(

    workspace_id: str = Header(...),

    db: Session = Depends(get_db),

    current_user: User = Depends(
        get_current_user
    )
):

    # VALIDATE MEMBERSHIP

    membership = (
        get_workspace_membership(
            db=db,
            user_id=current_user.id,
            workspace_id=workspace_id
        )
    )

    # GET AGENTS

    agents = (
        db.query(Agent)
        .filter(
            Agent.workspace_id ==
            workspace_id
        )
        .all()
    )

    # 🟢 NEW: CALCULATE AGGREGATED CONSUMED RUNTIME FOR THE WORKSPACE AGENTS
    agent_ids = get_workspace_agent_ids(db, workspace_id)
    
    workspace_runtime_ms = 0
    if agent_ids:
        workspace_runtime_ms = (
            db.query(func.sum(DurableStep.execution_time_ms))
            .filter(DurableStep.agent_id.in_(agent_ids))
            .scalar() or 0
        )

    # =========================================================================
    # EXTRACT TRUE SUBSCRIBER BUDGET EXTRACTION FROM INTER-LINKED TABLES
    # =========================================================================
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace data context not found")

    runtime_limit_hours = 10.0
    plan_tier_name = "FREE"

    # Navigate the real schema layers: Workspace -> WorkspaceSubscription -> Plan
    if getattr(workspace, "subscription", None) and workspace.subscription.status == "active":
        active_sub = workspace.subscription
        if getattr(active_sub, "plan", None):
            linked_plan = active_sub.plan
            plan_tier_name = str(getattr(linked_plan, "name", "FREE")).upper()
            
            # Extract out of the database limits JSON structure safely
            plan_limits = getattr(linked_plan, "limits", {}) or {}
            runtime_limit_hours = float(plan_limits.get("max_runtime_hours", 10.0))

    return {
        "total_agents": len(agents),
        "role": membership.role,
        "workspace_total_runtime_ms": workspace_runtime_ms,
        "workspace_runtime_limit_hours": runtime_limit_hours,
        "plan_tier": plan_tier_name,
        "agents": [
            {
                "id": str(agent.id),
                "name": agent.name,
                "status": agent.status
            }
            for agent in agents
        ]
    }

@router.post("/missions/{step_id}/retry")
def retry_mission(
    step_id: str,
    workspace_id: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # MEMBERSHIP
    membership = get_workspace_membership(
        db=db,
        user_id=current_user.id,
        workspace_id=workspace_id
    )

    # ROLE CHECK
    if membership.role not in [
        "admin",
        "operator"
    ]:

        return {
            "error":
            "Insufficient permissions"
        }

    # FEATURE ACCESS
    validate_feature_access(
        db,
        workspace_id,
        "missions"
    )

    # STEP
    step = (
        db.query(DurableStep)
        .filter(
            DurableStep.id == step_id,
            DurableStep.workspace_id == workspace_id
        )
        .first()
    )

    if not step:

        return {
            "error":
            "Mission not found"
        }

    # STATUS CHECK
    if step.status != "failed":

        return {
            "message":
            "Mission is not failed"
        }

    # RESET
    step.status = "pending"

    db.commit()

    process_step.delay(str(step.id))

    return {
        "message":
        "Mission retry scheduled"
    }