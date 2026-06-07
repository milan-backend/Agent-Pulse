import os
from google import genai
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
    db: Optional[Session] = None,            
    user_id: Optional[any] = None,           
    workspace_id: Optional[any] = None,      
    agent_id: Optional[any] = None,          
    model_name: str = "gemini-2.5-flash-lite" # Safe system fallback name
):
    if not prompt or not str(prompt).strip():
        return "No prompt provided. Generation skipped."

    # Standardize string inputs to UUIDs safely for the DB query
    clean_user_id = UUID(user_id.strip()) if isinstance(user_id, str) else user_id
    clean_workspace_id = UUID(workspace_id.strip()) if isinstance(workspace_id, str) else workspace_id
    clean_agent_id = UUID(agent_id.strip()) if isinstance(agent_id, str) else agent_id

    active_key = None
    target_model = model_name
    provider_type = "gemini" # Default type tracking

    # --------------------------------------------
    # DIRECT DATABASE LOOKUP (Takes model and key straight from your table!)
    # --------------------------------------------
    if db:
        query = db.query(UserAPIKey)
        if clean_agent_id:
            query = query.filter(UserAPIKey.agent_id == clean_agent_id)
        elif clean_workspace_id:
            query = query.filter(UserAPIKey.workspace_id == clean_workspace_id)
            # If the background worker passes down a targeted model choice, match it
            if model_name and model_name not in ["gemini", "openai", "gemini-2.5-flash-lite"]:
                query = query.filter(UserAPIKey.model_version == model_name)
            else:
                query = query.filter(UserAPIKey.is_default == True)
        else:
            query = query.filter(UserAPIKey.user_id == clean_user_id, UserAPIKey.is_default == True)

        key_record = query.first()

        if key_record:
            from app.core.crypto import decrypt_api_key
            active_key = decrypt_api_key(key_record.encrypted_api_key)
            provider_type = str(key_record.provider).lower().strip()
            
            # Direct hit! If the database row has a custom model name, use it directly!
            if key_record.model_version:
                target_model = key_record.model_version

    # --------------------------------------------
    # SERVER ENVIRONMENT VARIABLE FALLBACK
    # --------------------------------------------
    if not active_key:
        if "openai" in str(model_name).lower() or "gpt" in str(model_name).lower():
            active_key = os.getenv("OPENAI_API_KEY")
            provider_type = "openai"
        else:
            active_key = os.getenv("GEMINI_API_KEY")
            provider_type = "gemini"

    if not active_key:
        raise ValueError("No valid API credentials found in database or environment configuration.")

    # --------------------------------------------
    # EXECUTE CLIENT HANDSHAKE BASED ON PROVIDER TYPE
    # --------------------------------------------
    if "openai" in provider_type:
        client = OpenAI(api_key=active_key)
        response = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    else:
        client = genai.Client(api_key=active_key)
        response = client.models.generate_content(
            model=target_model,
            contents=prompt
        )
        return response.text