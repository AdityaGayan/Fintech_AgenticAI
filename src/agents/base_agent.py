from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import DEFAULT_LLM_MODEL, GEMINI_API_KEY

def get_llm(temperature: float = 0.0):
    """
    Initializes the core LLM using the Gemini API.
    Temperature is set to 0.0 to ensure deterministic, highly analytical outputs.
    """
    return ChatGoogleGenerativeAI(
        model=DEFAULT_LLM_MODEL,
        temperature=temperature,
        google_api_key=GEMINI_API_KEY or "dummy-key-for-testing",
        max_retries=2
    )