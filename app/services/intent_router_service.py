import os
import json
from typing import List
from pydantic import BaseModel, Field
from google import genai

# =====================================================================
# 1. Output Schema for Pass 1
# =====================================================================
class QueryIntentClassification(BaseModel):
    data_route: str = Field(
        description="MUST be exactly one of: 'LIVE_DATA' (for user-specific database queries like orders, accounts), 'KNOWLEDGE_BASE' (for general policies, manuals), or 'HYBRID' (if both are explicitly needed)."
    )
    intent_summary: str = Field(
        description="A concise 1-sentence summary of the user's core request."
    )
    schema_keywords: List[str] = Field(
        default_factory=list,
        description="If LIVE_DATA or HYBRID, list 3-5 keywords to search the database schema (e.g., ['order', 'tracking', 'status']). If KNOWLEDGE_BASE only, leave empty."
    )
    routing_reasoning: str = Field(
        description="Brief explanation of why this route was chosen."
    )

class IntentRouterService:
    @classmethod
    def classify_intent(cls, user_prompt: str) -> QueryIntentClassification:
        """
        The Master Gatekeeper: Analyzes the user prompt and determines 
        if we need database schemas, document knowledge, or both.
        """
        gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=gemini_key)

        print(f"🚦 [GATEKEEPER] Analyzing intent for prompt: '{user_prompt}'")

        system_instruction = (
            "You are the Master Gatekeeper for an enterprise AI system.\n"
            "Your ONLY job is to route the user's query to the correct data pipeline.\n\n"
            "ROUTING RULES:\n"
            "- LIVE_DATA: User wants their personal account info (e.g., 'where is my order?', 'check my balance', 'cancel my subscription').\n"
            "- KNOWLEDGE_BASE: User wants general information (e.g., 'what is the return policy?', 'how do I reset a password?').\n"
            "- HYBRID: User asks for BOTH (e.g., 'Where is my order, and what is the return policy?').\n\n"
            "KEYWORD EXTRACTION:\n"
            "If the route includes LIVE_DATA, extract 3-5 technical keywords that would likely match database table or column names (e.g., 'orders', 'status', 'email', 'id').\n\n"
            "Respond STRICTLY with valid JSON matching the schema."
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite", # Using flash-lite for blazing fast routing
            contents=user_prompt,
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_schema": QueryIntentClassification,
                "temperature": 0.0 # Zero hallucination
            }
        )

        decision = QueryIntentClassification.model_validate_json(response.text)
        print(f"✅ [GATEKEEPER DECISION]: {decision.data_route} | Keywords: {decision.schema_keywords}")
        
        return decision