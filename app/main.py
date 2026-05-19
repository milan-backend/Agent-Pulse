from fastapi import FastAPI

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

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "DAG Backend Running "}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development (later restrict)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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