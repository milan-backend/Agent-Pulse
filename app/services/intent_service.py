import os
import json
from google import genai
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class IntentAnalysisSchema(BaseModel):
    intent_type: str = Field(
        description="Strategy classification e.g., 'Direct Lookup', 'Workflow Explanation', 'Compliance Check', 'Audit'."
    )
    main_topic: str = Field(
        description="The primary domain subject matter being asked about."
    )
    retrieval_depth: str = Field(
        description="Granularity/depth of information required. MUST be one of: ['Shallow', 'Medium', 'Deep']."
    )
    target_document_ids: List[str] = Field(
        description="List of document UUIDs selected from the candidate pool that are highly relevant to the query."
    )
    target_section_codes: List[str] = Field(
        description="List of section codes or titles from the selected documents that are likely relevant."
    )
    include_sibling_sections: bool = Field(
        description="True if query depth requires pulling neighboring sections/chunks."
    )
    max_relationship_hops: int = Field(
        description="Maximum relationship hops (0 for direct fact, 1 for immediate context, 2-3 for deep multi-step workflows)."
    )
    depth_reasoning: str = Field(
        description="Brief reasoning for why this depth was selected, why lower is insufficient, and why higher is unnecessary."
    )


def analyze_user_query_intent(user_prompt: str, registry_candidates: List[Dict[str, Any]]) -> IntentAnalysisSchema:
    """
    Component 4 Intent Understanding AI (LLM-as-a-Judge): Evaluates the Registry Filter's top 
    document candidates (including their entities and sections) to determine exact targets.
    """
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME BREAKDOWN: API key for Intent Intelligence is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    system_instruction = (
        "You are AgentPulse Intent Analysis Engine.\n\n"
        "You NEVER answer the user's question.\n"
        "You ONLY determine the minimum information required for the Planner AI to retrieve.\n"
        "Your output directly controls retrieval cost.\n"
        "Incorrect depth selection wastes context window, increases token usage and reduces answer quality.\n"
        "Your objective is therefore to retrieve the SMALLEST amount of information capable of producing a complete answer.\n\n"
        "----------------------------------------\n"
        "PRIMARY RULE\n"
        "----------------------------------------\n"
        "Ignore wording style.\n"
        "Ignore politeness.\n"
        "Ignore sentence length.\n"
        "Ignore grammar.\n"
        "Ignore whether the user says:\n"
        "- 'Please'\n"
        "- 'Can you'\n"
        "- 'Could you'\n"
        "- 'I want to know'\n"
        "- 'Explain'\n"
        "- 'Tell me'\n"
        "- 'Help me'\n"
        "These NEVER affect retrieval depth.\n"
        "Intent is determined ONLY by the information requirement.\n"
        "Two semantically identical questions MUST always produce identical outputs.\n\n"
        "----------------------------------------\n"
        "Normalize the question first.\n"
        "----------------------------------------\n"
        "Before making any decision mentally reduce the query into its semantic intent.\n"
        "Examples:\n"
        "'How do I regenerate an API key?'\n"
        "'What is the process to regenerate an API key?'\n"
        "'Can you explain how API key regeneration works?'\n"
        "↓\n"
        "Normalized Intent: Regenerate API Key\n"
        "Depth is decided ONLY from the normalized intent. Never from wording.\n\n"
        "----------------------------------------\n"
        "DEPTH RULES\n"
        "----------------------------------------\n"
        "Retrieval depth depends only on how many independent pieces of information are required.\n"
        "NOT on wording. NOT on answer length. NOT on user vocabulary.\n\n"
        "SHALLOW:\n"
        "- Use when one chunk is sufficient.\n"
        "- Examples: Definition, Value lookup, Status lookup, Configuration lookup, Single setting, Single API, Single parameter, Single metric, Single event.\n"
        "- Relationship hops = 0\n"
        "- Sibling sections = False\n\n"
        "MEDIUM:\n"
        "- Use when multiple closely-related chunks are required.\n"
        "- Examples: How-to, Configuration, Single workflow, Feature explanation, Troubleshooting, Cause + Solution, One logical process.\n"
        "- Relationship hops = 1\n"
        "- Sibling sections = True\n\n"
        "DEEP:\n"
        "- Use ONLY if answering requires combining multiple independent document sections.\n"
        "- Examples: Architecture, End-to-end lifecycle, Cross-system workflow, Audit, Compliance, Comparison across documents, Multi-step reasoning.\n"
        "- Relationship hops = 2-3\n"
        "- Sibling sections = True\n"
        "- Never classify as Deep simply because the user asked for a detailed explanation.\n\n"
        "----------------------------------------\n"
        "Document Selection\n"
        "----------------------------------------\n"
        "Select only documents that directly contribute to the answer.\n"
        "Never select documents 'just in case.'\n"
        "If two documents contain identical information, select one.\n\n"
        "----------------------------------------\n"
        "Section Selection\n"
        "----------------------------------------\n"
        "Use only section names/codes from full_navigation_map / registry candidates.\n"
        "Never invent section names.\n"
        "Never broaden selection unnecessarily.\n\n"
        "----------------------------------------\n"
        "Cost Optimization\n"
        "----------------------------------------\n"
        "Always prefer fewer documents, fewer sections, lower hops, and lower retrieval depth if answer completeness is unchanged.\n\n"
        "----------------------------------------\n"
        "Consistency Rule\n"
        "----------------------------------------\n"
        "If the same semantic question is asked 100 different ways, the output MUST be identical.\n\n"
        "----------------------------------------\n"
        "Reasoning\n"
        "----------------------------------------\n"
        "Depth reasoning must explain:\n"
        "- Why this depth was selected\n"
        "- Why lower depth is insufficient\n"
        "- Why higher depth is unnecessary\n"
        "Do not describe the answer. Describe retrieval requirements only."
    )
    
    # Convert the Python list of dicts to a formatted JSON string for the LLM prompt
    candidates_json = json.dumps(registry_candidates, indent=2)
    
    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"TOP REGISTRY CANDIDATES (WITH ENTITIES & SECTIONS):\n{candidates_json}"
    )

    response = client.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": IntentAnalysisSchema,
            "temperature": 0.0
        }
    )
    
    return IntentAnalysisSchema.model_validate_json(response.text)