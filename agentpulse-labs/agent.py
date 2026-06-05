import os
import json
import time
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from langgraph.graph import StateGraph, START, END
from db_client import tracked_vector_query

ai = genai.Client()

class AgentState(TypedDict):
    user_query: str
    current_step: str
    retrieved_context: List[str]
    tool_outputs: List[Dict[str, Any]]
    llm_response: str
    telemetry_timeline: List[Dict[str, Any]]

def retrieve_knowledge_node(state: AgentState) -> Dict[str, Any]:
    print("[Agent Workflow] Executing Step: Knowledge Retrieval with Context Reasons...")
    timeline = list(state.get("telemetry_timeline", []))
    
    raw_results, telemetry_payload = tracked_vector_query(state["user_query"], n_results=2)
    
    context_strings = []
    processed_documents = []
    
    # 1. Dynamically classify the reason for retrieval for each document chunk
    for doc in telemetry_payload["documents"]:
        snippet_lower = doc["content_snippet"].lower()
        query_lower = telemetry_payload["retrieval_query"].lower()
        
        reasons = []
        if "cost" in query_lower or "premium" in query_lower or "pricing" in query_lower:
            if "cost" in snippet_lower or "premium" in snippet_lower or "plan" in snippet_lower:
                reasons.append("Matched pricing keywords")
        if "refund" in query_lower or "window" in query_lower or "policy" in query_lower:
            if "refund" in snippet_lower or "policy" in snippet_lower or "days" in snippet_lower:
                reasons.append("Matched refund rules context")
                
        # Fallback if it was a general semantic match
        reason_string = " | ".join(reasons) if reasons else "Semantic similarity text match"
        
        # Inject the reason metric directly into the document object block
        doc_with_reason = dict(doc)
        doc_with_reason["reason_for_retrieval"] = reason_string
        processed_documents.append(doc_with_reason)

    if raw_results and 'documents' in raw_results and len(raw_results['documents'][0]) > 0:
        context_strings = raw_results['documents'][0]
        
    timeline.append({
        "step_index": len(timeline) + 1,
        "event_name": telemetry_payload["event_type"],
        "retrieval_query": telemetry_payload["retrieval_query"], # <--- Logs targeted query parameters
        "latency_ms": telemetry_payload["latency_ms"],
        "status": telemetry_payload["status"],
        "meta": {
            "error_log": telemetry_payload["error_log"],
            "total_documents_found": telemetry_payload["total_documents_found"],
            "retrieval_hit_rate_percent": telemetry_payload["retrieval_hit_rate_percent"],
            "documents": processed_documents # Includes the custom reason keys!
        }
    })
    
    return {
        "retrieved_context": context_strings,
        "telemetry_timeline": timeline,
        "current_step": "knowledge_retrieved"
    }

def crm_lookup_node(state: AgentState) -> Dict[str, Any]:
    print("[Agent Workflow] Executing Step: CRM Enterprise Verification...")
    timeline = list(state.get("telemetry_timeline", []))
    
    start_time = time.time()
    time.sleep(0.08) 
    mock_crm_data = {"status": "Active Enterprise", "account_tier": "Premium Partner"}
    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    timeline.append({
        "step_index": len(timeline) + 1,
        "event_name": "CRM Lookup Tool",
        "latency_ms": latency_ms,
        "status": "SUCCESS",
        "meta": mock_crm_data
    })
    
    return {
        "tool_outputs": [mock_crm_data],
        "telemetry_timeline": timeline,
        "current_step": "tools_executed"
    }

def generate_response_node(state: AgentState) -> Dict[str, Any]:
    print("[Agent Workflow] Executing Step: Gemini Core Inference with Influence Tracking...")
    timeline = list(state.get("telemetry_timeline", []))
    
    context_payload = "\n".join(state["retrieved_context"])
    crm_payload = json.dumps(state["tool_outputs"])
    
    system_instruction = (
        "You are an observability assistant. Answer the user query using only the provided context documents.\n"
        "CRITICAL: At the very end of your response, output a single raw JSON block exactly formatted like this:\n"
        "CITATION: {\"influenced_by_files\": [\"filename.pdf\"]}\n"
        "List only the files that directly provided facts used in your text answer."
    )
    
    prompt = (
        f"Context Documents:\n{context_payload}\n\n"
        f"CRM Data:\n{crm_payload}\n\n"
        f"User Query: {state['user_query']}"
    )
    
    start_time = time.time()
    
    response = ai.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1,
        )
    )
    
    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    raw_text = response.text if response.text else ""
    clean_response = raw_text
    influenced_files = []
    
    if "CITATION:" in raw_text:
        try:
            parts = raw_text.split("CITATION:")
            clean_response = parts[0].strip()
            citation_json = json.loads(parts[1].strip())
            influenced_files = citation_json.get("influenced_by_files", [])
        except Exception:
            pass
            
    prompt_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
    completion_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
    
    timeline.append({
        "step_index": len(timeline) + 1,
        "event_name": "Gemini Response Generation",
        "latency_ms": latency_ms,
        "status": "SUCCESS",
        "meta": {
            "model_utilized": "gemini-2.5-flash",
            "prompt_tokens_consumed": prompt_tokens,
            "completion_tokens_consumed": completion_tokens,
            "total_tokens_consumed": prompt_tokens + completion_tokens,
            "documents_influencing_final_answer": influenced_files
        }
    })
    
    return {
        "llm_response": clean_response,
        "telemetry_timeline": timeline,
        "current_step": "generation_completed"
    }

workflow = StateGraph(AgentState)
workflow.add_node("retrieve_knowledge", retrieve_knowledge_node)
workflow.add_node("execute_crm_tool", crm_lookup_node)
workflow.add_node("generate_response", generate_response_node)

workflow.add_edge(START, "retrieve_knowledge")
workflow.add_edge("retrieve_knowledge", "execute_crm_tool")
workflow.add_edge("execute_crm_tool", "generate_response")
workflow.add_edge("generate_response", END)

compiled_agent = workflow.compile()

def run_experimental_agent(query: str) -> Dict[str, Any]:
    initial_state: AgentState = {
        "user_query": query,
        "current_step": "init",
        "retrieved_context": [],
        "tool_outputs": [],
        "llm_response": "",
        "telemetry_timeline": []
    }
    return compiled_agent.invoke(initial_state)