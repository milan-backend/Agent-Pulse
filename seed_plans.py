from app.db.session import SessionLocal
from app.models.plan import Plan

db = SessionLocal()

plans_data = [

    {
        "name": "free",
        "price": 0.0,

        "features": {

            # CORE
            "agent_execution": True,
            "background_agents": True,
            "live_websocket_updates": True,

            # RUNTIME
            "single_agent_pause": True,
            "single_agent_resume": True,
            "single_agent_kill": True,

            # OBSERVABILITY
            "analytics": True,
            "missions": True,
            "usage_logs": True,
            "audit_logs": True,

            # PREMIUM
            "mcp_access": False,
            "team_collaboration": False,
            "rbac": False,
            "priority_execution": False,
            "dedicated_runtime": False,
            "maintenance_mode": False
        },

        "limits": {
            "max_agents": 1,
            "max_monthly_usage": 5,
            "max_concurrent_runs": 1,
            "max_runtime_hours": 10
        }
    },

    {
        "name": "pro",
        "price": 29.0,

        "features": {

            # CORE
            "agent_execution": True,
            "background_agents": True,
            "live_websocket_updates": True,

            # RUNTIME
            "single_agent_pause": True,
            "single_agent_resume": True,
            "single_agent_kill": True,

            # TEAM
            "multi_workspace": True,
            "team_collaboration": True,
            "rbac": True,

            # MCP
            "mcp_access": True,

            # GOVERNANCE
            "priority_execution": True,
            "retry_control": True,
            "loop_detection": True,
            "budget_control": True,

            # OBSERVABILITY
            "analytics": True,
            "missions": True,
            "usage_logs": True,
            "audit_logs": True,

            # ENTERPRISE ONLY
            "dedicated_runtime": False,
            "maintenance_mode": False
        },

        "limits": {
            "max_agents": 10,
            "max_monthly_usage": 100,
            "max_concurrent_runs": 5,
            "max_team_members": 10,
            "max_runtime_hours": 100
        }
    },

    {
        "name": "enterprise",
        "price": 199.0,

        "features": {

            # EVERYTHING
            "agent_execution": True,
            "background_agents": True,
            "live_websocket_updates": True,

            "single_agent_pause": True,
            "single_agent_resume": True,
            "single_agent_kill": True,

            "multi_workspace": True,
            "team_collaboration": True,
            "rbac": True,

            "mcp_access": True,

            "priority_execution": True,
            "retry_control": True,
            "loop_detection": True,
            "budget_control": True,

            "analytics": True,
            "missions": True,
            "usage_logs": True,
            "audit_logs": True,

            # ENTERPRISE
            "dedicated_runtime": True,
            "maintenance_mode": True
        },

        "limits": {
            "max_agents": 100,
            "max_monthly_usage": 10000,
            "max_concurrent_runs": 100,
            "max_team_members": 100,
            "max_runtime_hours": 10000
        }
    }
]

for plan_data in plans_data:

    existing = (
        db.query(Plan)
        .filter(
            Plan.name == plan_data["name"]
        )
        .first()
    )

    if existing:

        existing.price = plan_data["price"]
        existing.features = plan_data["features"]
        existing.limits = plan_data["limits"]

        print(f"UPDATED: {existing.name}")

    else:

        plan = Plan(
            name=plan_data["name"],
            price=plan_data["price"],
            features=plan_data["features"],
            limits=plan_data["limits"]
        )

        db.add(plan)

        print(f"CREATED: {plan.name}")

db.commit()

print("\nPLANS SEEDED SUCCESSFULLY\n")

db.close()