import os

import google.generativeai as genai


# ============================================
# CONFIGURE GEMINI
# ============================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

print(
    "GEMINI API KEY:",
    GEMINI_API_KEY
)

genai.configure(
    api_key=GEMINI_API_KEY
)


# ============================================
# LOAD MODEL
# ============================================

model = genai.GenerativeModel(
    "gemini-1.5-flash-latest"
)


# ============================================
# GENERATE LLM RESPONSE
# ============================================

def generate_llm_response(
    prompt: str,
    model_name: str = "gemini"
):

    try:

        print(
            "GENERATING GEMINI RESPONSE..."
        )

        response = model.generate_content(
            prompt
        )

        print(
            "FULL GEMINI RESPONSE:",
            response
        )

        if not response:

            raise Exception(
                "Empty response from Gemini"
            )

        if not hasattr(response, "text"):

            raise Exception(
                "No text field in Gemini response"
            )

        output = response.text

        print(
            "GEMINI OUTPUT:",
            output
        )

        return output

    except Exception as e:

        print(
            "GEMINI ERROR:",
            str(e)
        )

        raise Exception(
            f"Gemini execution failed: {str(e)}"
        )