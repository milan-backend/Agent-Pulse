import os
from google import genai
from openai import OpenAI

def execute_provider_stream(active_model_target: str, final_prompt_payload: str, gemini_api_key: str, redis_client, step_id: str, tier_source: str):
    """
    Centralized Multi-Provider Streaming Engine: Dynamically checks the requested
    model name, binds credentials, and flushes chunks directly to Redis.
    """
    model_lower = active_model_target.lower()
    
    # 🎯 ROUTE 1: GEMINI STREAMING CORE
    if "gemini" in model_lower:
        if not gemini_api_key:
            raise ValueError("CRITICAL: Gemini API Key could not be resolved for streaming pipeline initialization.")
            
        ai_client = genai.Client(api_key=gemini_api_key)
        
        try:
            response_stream = ai_client.models.generate_content_stream(
                model=active_model_target,
                contents=final_prompt_payload
            )
            output_fragments = []
            for chunk in response_stream:
                if chunk.text:
                    output_fragments.append(chunk.text)
                    # Instant broadcast down the isolated Redis Pub/Sub lane
                    redis_client.publish(f"stream:{step_id}", chunk.text)
            return "".join(output_fragments)
            
        except Exception as stream_err:
            error_str = str(stream_err)
            # Catch 429 bounds only if running on shared system credentials to protect platform limits
            if "429" in error_str and tier_source == "system":
                friendly_msg = "⚠️ The system shared sandbox tier key has exhausted its rate limit bounds. Please add your own custom Gemini API Key inside your dashboard settings workspace panel to bypass cluster congestion."
                redis_client.publish(f"stream:{step_id}", friendly_msg)
                raise ValueError(friendly_msg)
            raise stream_err

    # 🎯 ROUTE 2: OPENAI (GPT) STREAMING CORE
    elif "gpt" in model_lower or "openai" in model_lower:
        # Fall back to your decrypted workspace key sequence or grab the system environment array
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            raise ValueError("CRITICAL: OpenAI API Key could not be resolved for streaming pipeline initialization.")
            
        openai_client = OpenAI(api_key=openai_api_key)
        
        try:
            response_stream = openai_client.chat.completions.create(
                model=active_model_target,
                messages=[{"role": "user", "content": final_prompt_payload}],
                stream=True
            )
            output_fragments = []
            for chunk in response_stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    output_fragments.append(token)
                    redis_client.publish(f"stream:{step_id}", token)
            return "".join(output_fragments)
            
        except Exception as stream_err:
            error_str = str(stream_err)
            if "429" in error_str and tier_source == "system":
                friendly_msg = "⚠️ The system shared sandbox tier key has exhausted its OpenAI rate limits. Please add your own custom OpenAI API Key inside your dashboard settings workspace panel."
                redis_client.publish(f"stream:{step_id}", friendly_msg)
                raise ValueError(friendly_msg)
            raise stream_err

    else:
        raise ValueError(f"Unsupported provider engine mapping context for target model: {active_model_target}")