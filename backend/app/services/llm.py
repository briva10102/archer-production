from google import genai

from app.core.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def generate_answer(
    question: str,
    context: str,
    history: str = ""
) -> str:

    prompt = f"""
You are an AI assistant for a solar company.

Use ONLY the information provided in the context below.

If the answer is not present in the context, reply exactly:
"I couldn't find that information in the uploaded document."

Conversation History:
{history}

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text