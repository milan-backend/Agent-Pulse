import os
from google import genai
from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID

from app.services.user_api_key_service import UserAPIKeyService

# ============================================
# GENERATE LLM RESPONSE (PRODUCTION BYOK READY)
# ============================================

def generate_llm_response(
    prompt: str,                            # Kept as first parameter for full backward compatibility
    db: Optional[Session] = None,           # Optional fallback context
    user_id: Optional[UUID] = None,         # Optional fallback context
    workspace_id: Optional[UUID] = None     # Optional fallback context
):
    if not prompt or not str(prompt).strip():
        return "No prompt provided. Gemini skipped."

    try:
        active_key = None

        # 1. Look up custom key ONLY if a database session context is explicitly active
        if db:
            active_key = UserAPIKeyService.fetch_decrypted_key(
                db=db,
                provider="gemini",
                user_id=user_id,
                workspace_id=workspace_id
            )

        # 2. Fallback: If no custom database credentials exist or no session was provided, use system master key
        if not active_key:
            active_key = os.getenv("GEMINI_API_KEY")

        if not active_key:
            raise ValueError("No valid Gemini API key configuration found for this execution runtime.")

        # 3. Dynamic thread-safe client instantiation
        client = genai.Client(api_key=active_key)

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("========== GEMINI ERROR ==========")
        print(str(e))
        print("==================================")
        raise Exception(str(e))