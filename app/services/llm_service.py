import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)

def generate_llm_response(
    prompt: str,
    model_name: str = "gemini"
):

    response = model.generate_content(
        prompt
    )

    return response.text