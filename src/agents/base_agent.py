import time
from typing import Type, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from src.config import DEFAULT_LLM_MODEL, GEMINI_API_KEY

def get_llm(temperature: float = 0.0, max_retries: int = 3):
    """
    Initializes the configured Gemini LLM.
    """
    if not GEMINI_API_KEY or not DEFAULT_LLM_MODEL:
        raise RuntimeError("GEMINI_API_KEY and GEMINI_MODEL must be configured")

    return ChatGoogleGenerativeAI(
        model=DEFAULT_LLM_MODEL,
        temperature=temperature,
        google_api_key=GEMINI_API_KEY,
        max_retries=max_retries
    )

def invoke_gemini_safely(
    schema: Type[BaseModel], 
    prompt: str, 
    temperature: float = 0.0,
    max_retries: int = 4
) -> Optional[Any]:
    """
    Invokes the configured Gemini model with structured output.
    Retries with increasing back-off on transient errors (high demand / 429 / 503).
    Returns None on persistent failure so the caller can provide seamless output.
    """
    for attempt in range(1, max_retries + 1):
        try:
            llm = get_llm(temperature=temperature, max_retries=2)
            structured_llm = llm.with_structured_output(schema)
            return structured_llm.invoke(prompt)
        except Exception as e:
            err_str = str(e).lower()
            is_transient = any(phrase in err_str for phrase in [
                "demand", "overload", "resourceexhausted", "429", "503",
                "quota", "busy", "rate", "temporarily", "unavailable",
                "capacity", "try again", "service_unavailable",
            ])
            if is_transient and attempt < max_retries:
                time.sleep(1.5 * attempt)      # 1.5s, 3s, 4.5s
            else:
                break
    return None
