import os
from google import genai
from google.genai import types # Added to handle formal configuration class allocations
from openai import OpenAI
from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user_api_key import UserAPIKey

# ============================================
# MULTI-PROVIDER LLM RESPONSE GENERATOR
# ============================================

def generate_llm_response(
    prompt: str,                             
    db: Session,                               # Mandated for secure configuration lookups
    workspace_id: any,                        # STRICT SECURITY BOUNDARY: MANDATORY
    agent_id: Optional[any] = None,          
    model_name: Optional[str] = None          # Completely dynamic dropdown selection passed from step_tasks
):
    if not prompt or not str(prompt).strip():
        return "No prompt provided. Generation skipped."

    if not workspace_id:
        raise ValueError("Security Violation: workspace_id is strictly mandatory for executing LLM generations.")

    # Standardize string inputs to UUIDs safely for database query matching
    clean_workspace_id = UUID(workspace_id.strip()) if isinstance(workspace_id, str) else workspace_id
    clean_agent_id = UUID(agent_id.strip()) if isinstance(agent_id, str) else agent_id

    active_key = None
    target_model = model_name
    provider_type = "gemini" # Base tracking default

    key_record = None

    # -----------------------------------------------------------------
    # PIPELINE TIER 1: Check Agent-Specific API Key inside this Workspace
    # -----------------------------------------------------------------
    if clean_agent_id:
        key_record = db.query(UserAPIKey).filter(
            UserAPIKey.agent_id == clean_agent_id,
            UserAPIKey.workspace_id == clean_workspace_id
        ).first()

    # -----------------------------------------------------------------
    # PIPELINE TIER 2: Fallback to Tenant Workspace Level Configurations
    # -----------------------------------------------------------------
    if not key_record:
        # Step A: Look up the key explicitly set as default by the active UI toggle button
        key_record = db.query(UserAPIKey).filter(
            UserAPIKey.workspace_id == clean_workspace_id,
            UserAPIKey.agent_id == None,
            UserAPIKey.is_default == True
        ).first()
        
        # Step B: If no explicit default button state exists, grab the latest configured workspace row
        if not key_record:
            key_record = db.query(UserAPIKey).filter(
                UserAPIKey.workspace_id == clean_workspace_id,
                UserAPIKey.agent_id == None
            ).order_by(UserAPIKey.updated_at.desc()).first()

    # -----------------------------------------------------------------
    # CRYPTOGRAPHIC DECRYPTION OR DROP TO TIER 3 (ENVIRONMENT VARIABLES)
    # -----------------------------------------------------------------
    if key_record:
        from app.core.crypto import decrypt_api_key
        active_key = decrypt_api_key(key_record.encrypted_api_key)
        provider_type = str(key_record.provider).lower().strip() # Reads clean lowercase 'gemini' or 'openai'
        
        # If the database row explicitly holds a saved dropdown selection, prioritize it
        if key_record.model_version:
            target_model = key_record.model_version
    else:
        # PIPELINE TIER 3: Absolute Last Resort Server Environment Fallback (Render variables)
        model_str_check = str(model_name).lower() if model_name else ""
        
        if "openai" in model_str_check or "gpt" in model_str_check:
            active_key = os.getenv("OPENAI_API_KEY")
            provider_type = "openai"
            if not target_model:
                target_model = "gpt-4o-mini"
        else:
            active_key = os.getenv("GEMINI_API_KEY")
            provider_type = "gemini"
            if not target_model:
                target_model = "gemini-2.5-flash-lite"

    if not active_key:
        raise ValueError(f"No valid API credentials found for Agent, Workspace {clean_workspace_id}, or Server Environment configurations.")

    # -----------------------------------------------------------------
    # 🎯 SYSTEM INSTRUCTION: CRISP, ACCURATE, SHORT SUMMARIES ALWAYS
    # -----------------------------------------------------------------
    system_instruction = (
        "You are a concise engineering core assistant. When the user queries technical details from "
        "the injected context, do not write a massive textbook or repeat everything line-by-line. "
        "Provide a short, direct, high-impact technical response using clean markdown bullet points."
    )

    # --------------------------------------------
    # EXECUTE CLIENT HANDSHAKE BASED ON PROVIDER
    # --------------------------------------------
    if "openai" in provider_type:
        client = OpenAI(api_key=active_key)
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": system_instruction}, # Enforces short responses
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.2
        )
        return response.choices[0].message.content
    else:
        client = genai.Client(api_key=active_key)
        response = client.models.generate_content(
            model=target_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction, # Enforces short responses on Gemini
                max_output_tokens=2048,
                temperature=0.2
            )
        )
        return response.text