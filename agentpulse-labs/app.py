import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Ensure the Python environment knows where to look for your root files
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the graph entrypoint from your newly created agent.py file
from agent import run_experimental_agent

# Initialize the experimental FastAPI backend instance
app = FastAPI(
    title="AgentPulse Labs - Observability Research Server",
    description="Isolated prototype API layer to capture next-gen retrieval and tool call telemetry events.",
    version="1.0.0"
)

# Set up open CORS policies for your experimental labs environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the incoming request payload shape
class QueryRequest(BaseModel):
    user_query: str

@app.get("/")
def read_root():
    return {
        "status": "online",
        "workspace": "agentpulse-labs",
        "purpose": "Observability Event Tracking Research Cluster"
    }

@app.post("/query")
async def execute_query_endpoint(payload: QueryRequest):
    """
    Core experimental endpoint. Runs the LangGraph system, 
    tracks performance metrics across every single node execution step, 
    and outputs a unified chronological telemetry stream.
    """
    if not payload.user_query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")
        
    try:
        print(f"\n[Labs API] Received incoming research query: '{payload.user_query}'")
        
        # Invoke the compiled LangGraph workflow graph
        graph_output = run_experimental_agent(payload.user_query)
        
        # Construct a clean response payload capturing exactly what your Research Plan demands:
        # Combined view of Responses, Tools, RAG stats, and LLM Token Metrics.
        return {
            "query": graph_output.get("user_query"),
            "final_agent_response": graph_output.get("llm_response"),
            "last_executed_step": graph_output.get("current_step"),
            # This is your raw timeline goldmine for future dashboard charts!
            "telemetry_timeline": graph_output.get("telemetry_timeline", [])
        }
        
    except Exception as e:
        print(f"[-] API Execution Layer crashed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Agent Trace Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Start local testing server matching your installed requirements choice
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)