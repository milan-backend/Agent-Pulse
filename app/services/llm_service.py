import os
from google import genai
from google.genai import types  # Imported to handle unconstrained configuration profiles
from openai import OpenAI
from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user_api_key import UserAPIKey
from app.services.user_api_key_service import UserAPIKeyService

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
    
    # -----------------------------------------------------------------
    # DETECT PROVIDER ENGINE TYPE REQUEST BASED ON TARGET MODEL NAME
    # -----------------------------------------------------------------
    model_str_check = str(model_name).lower().strip() if model_name else ""
    requested_provider_type = "gemini"
    if "openai" in model_str_check or "gpt" in model_str_check:
        requested_provider_type = "openai"

    # -----------------------------------------------------------------
    # UPGRADED RESOLUTION PIPELINE: RUN 4-STEP RECURSIVE RESOLUTION ENGINE
    # -----------------------------------------------------------------
    key_record = None
    if clean_agent_id:
        key_record = UserAPIKeyService.resolve_agent_api_key(
            db=db,
            workspace_id=clean_workspace_id,
            agent_id=clean_agent_id,
            provider_type=requested_provider_type
        )

    # -----------------------------------------------------------------
    # CRYPTOGRAPHIC DECRYPTION OR DROP TO SYSTEM DEFAULT (ENVIRONMENT VARIABLES)
    # -----------------------------------------------------------------
    if key_record:
        from app.core.crypto import decrypt_api_key
        active_key = decrypt_api_key(key_record.encrypted_api_key)
        provider_type = str(key_record.provider).lower().strip() # Reads clean lowercase 'gemini' or 'openai'
        
        # If the database row explicitly holds a saved dropdown selection, prioritize it
        if key_record.model_version and not target_model:
            target_model = key_record.model_version
    else:
        # PIPELINE STEP 4 FALLBACK: Absolute Last Resort Server Environment Fallback (Render variables)
        provider_type = requested_provider_type
        if provider_type == "openai":
            active_key = os.getenv("OPENAI_API_KEY")
            if not target_model:
                target_model = "gpt-4o-mini"
        else:
            active_key = os.getenv("GEMINI_API_KEY")
            if not target_model:
                target_model = "gemini-2.5-flash-lite"

    if not active_key:
        raise ValueError(f"No valid API credentials found for Agent, Workspace {clean_workspace_id}, or Server Environment configurations.")

    # --------------------------------------------
    # EXECUTE CLIENT HANDSHAKE BASED ON PROVIDER
    # --------------------------------------------
    if "openai" in provider_type:
        client = OpenAI(api_key=active_key)
        response = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}]
            # No max_tokens limit passed here: OpenAI defaults to its maximum possible window return size
        )
        return response.choices[0].message.content
    else:
        client = genai.Client(api_key=active_key)
        response = client.models.generate_content(
            model=target_model,
            contents=prompt,
            # Explicitly configuration assigned to clear out Gemini constraints
            config=types.GenerateContentConfig(
                max_output_tokens=8192  # Setting this explicitly large guarantees the full text prints entirely
            )
        )
        return response.text