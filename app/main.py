from fastapi import FastAPI,Request,Response

from app.db.session import Base, engine

from app.models.agent import Agent
from app.models.durable_step import DurableStep
from app.api.routes import steps
from app.api.routes import agents
from app.api.routes import mcp
from app.api.routes import auth
from app.api.routes import dashboard
from app.api.routes import ws
from app.api.routes import kill
from app.api.routes import mission_control
from app.api.routes import workspace
from app.api.routes.analytics import router as analytics_router
from app.api.routes import missions
from app.api.routes import usage
from app.api.routes import tasks
from app.api.routes import user_api_key
from app.api.routes import documents

from app.api.routes import billing, webhooks

import os
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "DAG Backend Running "}

frontend_url_env = os.getenv("FRONTEND_URL")

if not frontend_url_env:
    allowed_origins_list = []

else:
    allowed_origins_list = [url.strip() for url in frontend_url_env.split(",")]

# =====================================================================
# 🔴 TEMPORARY VIDEO RECORDING PATCH: LOCAL OVERRIDES (REMOVE AFTER TESTING)
# =====================================================================
# This ensures that your deployed app accepts requests from your game canvas local server ports
for local_url in ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000", "http://127.0.0.1:3000"]:
    if local_url not in allowed_origins_list:
        allowed_origins_list.append(local_url)
# =====================================================================    

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================================
# 🔴 TEMPORARY VIDEO RECORDING PATCH: PREFLIGHT INTERCEPTOR (REMOVE AFTER TESTING)
# =====================================================================
@app.middleware("http")
async def force_preflight_approval_catch(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        origin = request.headers.get("Origin")
        
        if origin in allowed_origins_list:
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = allowed_origins_list[0] if allowed_origins_list else "*"
            
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
        
        requested_headers = request.headers.get("Access-Control-Request-Headers", "X-API-Key, Content-Type, Authorization, Accept, Origin, workspace-id")
        response.headers["Access-Control-Allow-Headers"] = requested_headers
        return response
        
    return await call_next(request)
# =====================================================================


app.include_router(steps.router, prefix="/steps", tags=["Steps"])
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(mcp.router, prefix="/mcp", tags=["MCP"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=['Dashboard'])
app.include_router(ws.router)
app.include_router(analytics_router)
app.include_router(kill.router)
app.include_router(mission_control.router, prefix="/mission-control", tags=["Mission Control"])
app.include_router(workspace.router, prefix= "/workspace", tags=["Workspace"]) 
app.include_router(missions.router)
app.include_router(usage.router)
app.include_router(tasks.router)
app.include_router(billing.router, prefix="/billing", tags=["Billing"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(user_api_key.router, prefix="/api-keys", tags=["API Keys"])
app.include_router(documents.router)