import os
from google import genai
from openai import OpenAI  # Added OpenAI SDK support cleanly
from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.services.user_api_key_service import UserAPIKeyService

# ============================================
# MULTI-PROVIDER LLM RESPONSE GENERATOR (FIXED)
# ============================================

def generate_llm_response(
    prompt: str,                             # Kept as first parameter for full backward compatibility
    db: Optional[Session] = None,            # Optional fallback context
    user_id: Optional[any] = None,           # Flex-type validation compatibility override
    workspace_id: Optional[any] = None,      # Flex-type validation compatibility override
    model_name: str = "gemini"               # New parameter: defaults to gemini to prevent breaking current code
):
    if not prompt or not str(prompt).strip():
        return "No prompt provided. Generation skipped."

    # Standardize our provider router flags
    model_lower = str(model_name).lower()
    is_openai = any(x in model_lower for x in ["gpt", "openai"])

    # Safe data parsing type transformations before running DB queries
    clean_user_id = user_id
    if user_id and isinstance(user_id, str):
        try:
            clean_user_id = UUID(user_id.strip())
        except ValueError:
            pass

    clean_workspace_id = workspace_id
    if workspace_id and isinstance(workspace_id, str):
        try:
            clean_workspace_id = UUID(workspace_id.strip())
        except ValueError:
            pass

    try:
        active_key = None

        # --------------------------------------------
        # BRANCH A: OPENAI ROUTING ENGINE
        # --------------------------------------------
        if is_openai:
            # 1. Fetch from workspace database using your true encryption provider key
            if db:
                active_key = UserAPIKeyService.fetch_decrypted_key(
                    db=db,
                    provider="OPENAI_API_KEY", 
                    user_id=clean_user_id,
                    workspace_id=clean_workspace_id
                )

            # 2. Infrastructure Fallback: System environment backup
            if not active_key:
                active_key = os.getenv("OPENAI_API_KEY")

            if not active_key:
                raise ValueError("No valid OpenAI API key configuration found for this execution runtime.")

            # 3. Instantiate thread-safe OpenAI core client
            client = OpenAI(api_key=active_key)
            
            # Map specific model variations dynamically (defaults to gpt-4o-mini if generic string passed)
            target_model = model_name if "gpt" in model_lower else "gpt-4o-mini"

            response = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        # --------------------------------------------
        # BRANCH B: GOOGLE GEMINI ROUTING ENGINE
        # --------------------------------------------
        else:
            # 1. Fetch from workspace database using your true encryption provider key
            if db:
                active_key = UserAPIKeyService.fetch_decrypted_key(
                    db=db,
                    provider="GEMINI_API_KEY", 
                    user_id=clean_user_id,
                    workspace_id=clean_workspace_id
                )

            # 2. Infrastructure Fallback: System environment backup
            if not active_key:
                active_key = os.getenv("GEMINI_API_KEY")

            if not active_key:
                raise ValueError("No valid Gemini API key configuration found for this execution runtime.")

            # 3. Instantiate thread-safe Google GenAI client
            client = genai.Client(api_key=active_key)
            
            # Keep your production model layout active
            target_model = model_name if "gemini" in model_lower else "gemini-2.5-flash-lite"

            response = client.models.generate_content(
                model=target_model,
                contents=prompt
            )
            return response.text

    except Exception as e:
        print(f"========== LLM SERVICE ERROR [{model_name.upper()}] ==========")
        print(str(e))
        print("==============================================================")
        raise Exception(str(e))