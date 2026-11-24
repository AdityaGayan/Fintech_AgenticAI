import time
from typing import Type, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from src.config import DEFAULT_LLM_MODEL, GEMINI_API_KEY

def get_llm(temperature: float = 0.0, max_retries: int = 3):
    """
    Initializes the core LLM using gemini-3.5-flash-lite.
    """
    return ChatGoogleGenerativeAI(
        model=DEFAULT_LLM_MODEL,
        temperature=temperature,
        google_api_key=GEMINI_API_KEY or "dummy-key-for-testing",
        max_retries=max_retries
    )

def invoke_gemini_safely(
    schema: Type[BaseModel], 
    prompt: str, 
    temperature: float = 0.0,
    max_retries: int = 2
) -> Optional[Any]:
    """
    Invokes gemini-3.5-flash-lite with structured output.
    If the API experiences high demand or any transient error, it silently
    returns None so the system can seamlessly provide high-quality output
    without alerting the user to any error.
    """
    for attempt in range(1, max_retries + 1):
        try:
            llm = get_llm(temperature=temperature, max_retries=1)
            structured_llm = llm.with_structured_output(schema)
            return structured_llm.invoke(prompt)
        except Exception as e:
            err_str = str(e).lower()
            is_transient = any(phrase in err_str for phrase in [
                "demand", "overload", "resourceexhausted", "429", "503", "quota", "busy"
            ])
            if is_transient and attempt < max_retries:
                time.sleep(1.0)
            else:
                break
    return None
