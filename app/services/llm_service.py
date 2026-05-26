import requests


OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_llm_response(
    prompt: str,
    model: str = "phi3"
):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    return data["response"]