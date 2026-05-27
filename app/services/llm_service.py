import os

from google import genai


# ============================================
# GEMINI CLIENT
# ============================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================
# GENERATE LLM RESPONSE
# ============================================

def generate_llm_response(
    prompt: str,
    model_name: str = "gemini-2.0-flash"
):

    try:

        response = client.models.generate_content(

            model=model_name,

            contents=prompt

        )

        return response.text

    except Exception as e:

        print("GEMINI ERROR:")
        print(str(e))

        raise Exception(
            "LLM execution failed"
        )