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
    prompt: str
):

    try:

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