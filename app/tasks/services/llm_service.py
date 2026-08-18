import os
from google import genai
from google.genai import types  # Imported to handle unconstrained configuration profiles
from openai import OpenAI
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user_api_key import UserAPIKey
from app.services.user_api_key_service import UserAPIKeyService

# ============================================
# MULTI-PROVIDER LLM RESPONSE GENERATOR
# ============================================

def generate_llm_response(
    prompt: str,                             
    db: Session,                                # Mandated for secure configuration lookups
    workspace_id: any,                        # STRICT SECURITY BOUNDARY: MANDATORY
    agent_id: Optional[any] = None,          
    model_name: Optional[str] = None          # Completely dynamic dropdown selection passed from step_tasks
) -> Tuple[str, str]:
    """
    Hierarchical Resolution Engine with Dynamic Attribution Alerts:
    1. Looks for an Agent-Specific API key override in the database. (agent tier)
    2. Looks for a Workspace Key explicitly restricted to the active agent. (workspace tier)
    3. Looks for a Workspace Key open for ALL agents. (workspace tier)
    4. Drops down last resort to Server Environment Variables. (system tier)
    
    Returns a Tuple of: (generated_text_response, status_attribution_message)
    """
    if not prompt or not str(prompt).strip():
        return "No prompt provided. Generation skipped.", "Notice: Empty execution payload string dropped safely."

    if not workspace_id:
        raise ValueError("Security Violation: workspace_id is strictly mandatory for executing LLM generations.")

    # Standardize string inputs to UUIDs safely for database query matching
    clean_workspace_id = UUID(workspace_id.strip()) if isinstance(workspace_id, str) else workspace_id
    clean_agent_id = UUID(agent_id.strip()) if isinstance(agent_id, str) else agent_id

    active_key = None
    target_model = model_name
    tier_source = "system" # Baseline default fallback assignment variable
    
    # -----------------------------------------------------------------
    # DETECT PROVIDER ENGINE TYPE REQUEST BASED ON TARGET MODEL NAME
    # -----------------------------------------------------------------
    model_str_check = str(model_name).lower().strip() if model_name else ""
    requested_provider_type = "gemini"
    if "openai" in model_str_check or "gpt" in model_str_check:
        requested_provider_type = "openai"

    # -----------------------------------------------------------------
    # RUN ARCHITECTURAL BLUEPRINT HIERARCHICAL RESOLUTION LOOKUPS
    # -----------------------------------------------------------------
    key_record = None
    if clean_agent_id:
        # ✅ UPDATED: Capturing both the database record row and the assigned string tracking tag parameter
        key_record, tier_source = UserAPIKeyService.resolve_agent_api_key(
            db=db,
            workspace_id=clean_workspace_id,
            agent_id=clean_agent_id,
            provider_type=requested_provider_type
        )

    # -----------------------------------------------------------------
    # EVALUATE CREDENTIAL SECURITY MATRIX AND COMPUTE DECRYPTION HOOKS
    # -----------------------------------------------------------------
    if key_record:
        from app.core.crypto import decrypt_api_key
        active_key = decrypt_api_key(key_record.encrypted_api_key)
        provider_type = str(key_record.provider).lower().strip() # Reads clean lowercase 'gemini' or 'openai'
        
        # If the database row explicitly holds a saved dropdown selection, prioritize it
        if hasattr(key_record, 'model_version') and key_record.model_version and not target_model:
            target_model = key_record.model_version
    else:
        # --- FINAL FALLBACK LAYER: System Environment Variables ---
        provider_type = requested_provider_type
        tier_source = "system" # Explicit boundary re-assertion flag
        if provider_type == "openai":
            active_key = os.getenv("OPENAI_API_KEY")
            if not target_model:
                target_model = "gpt-4o-mini"
        else:
            active_key = os.getenv("GEMINI_API_KEY")
            if not target_model:
                target_model = "gemini-2.5-flash-lite"

    # 🛡️ SYSTEM SECURITY GUARD: Explicit isolation boundary check
    if not active_key:
        raise ValueError(
            f"Credential Isolation Fault: Agent '{clean_agent_id}' is not authorized to use any workspace key "
            f"allocations, and no baseline fallback keys were found inside the server environment configurations."
        )

    # -----------------------------------------------------------------
    # CONSTRUCT BEAUTIFUL ENTERPRISE ATTRÌBUTION NOTIFICATION ALERTS
    # -----------------------------------------------------------------
    if tier_source == "agent":
        status_message = "Success: Runtime execution isolated securely via Agent Private Credentials. Dedicated tier routing active."
    elif tier_source == "workspace":
        status_message = "Success: Runtime execution completed using Workspace Shared Provider resources. Global pooling active."
    else:
        status_message = (
            "Notice: Running on System Shared Sandbox Tier. To guarantee production-grade uptime, "
            "unlock maximum concurrent throughput, and completely bypass community rate limits (429), "
            "connect your personal API key in Workspace Settings."
        )

    # --------------------------------------------
    # EXECUTE CLIENT HANDSHAKE BASED ON PROVIDER
    # --------------------------------------------
    try:
        if "openai" in provider_type:
            client = OpenAI(api_key=active_key)
            response = client.chat.completions.create(
                model=target_model,
                messages=[{"role": "user", "content": prompt}]
            )
            output_text = response.choices[0].message.content
            return output_text, status_message
        else:
            client = genai.Client(api_key=active_key)
            response = client.models.generate_content(
                model=target_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=8192  
                )
            )
            output_text = response.text
            return output_text, status_message

    except Exception as llm_exception:
        error_str = str(llm_exception)
        
        # 🎯 SMART PROTECTION INTERCEPTOR GATES:
        # If execution crashes on a 429 Too Many Requests rate limit block, and it is using your 
        # personal system wallet variables, trap it immediately and provide a high-conversion call-to-action message.
        if "429" in error_str and tier_source == "system":
            cta_message = (
                "Resource Exhausted: The community shared system engine has reached its temporary throughput "
                "capacity threshold. To instantly activate an unthrottled, isolated execution lane for your "
                "AI pipelines without interruption, please connect your dedicated provider credentials under Workspace Settings."
            )
            # Raise the exception with our beautiful message so step_tasks catches it and updates error_message
            raise ValueError(cta_message) from llm_exception
            
        # Fallback to standard exception mapping for other errors or authorized tiers
        raise llm_exception