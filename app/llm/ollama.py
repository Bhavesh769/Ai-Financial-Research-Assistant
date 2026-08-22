import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:latest"

def generate_answer(query: str, context: str) -> str:

    prompt = f"""
You are a financial research assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not invent financial figures or facts.
- Do not use outside knowledge.
- If the context does not contain enough information, say:
  "The provided evidence is insufficient to answer this question."
- Give a concise and factual answer.
- When a financial number is available, preserve its exact value and unit.
- Mention the relevant period when applicable.

Context:
{context}

Question:
{query}

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()["response"].strip()