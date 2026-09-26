import re

class PromptInjectionDetector:
    # Common adversarial phrases used to jailbreak LLMs
    INJECTION_SIGNATURES = [
        r"(?i)ignore\s+(all\s+)?(previous\s+)?instructions",
        r"(?i)disregard\s+(all\s+)?(previous\s+)?instructions",
        r"(?i)forget\s+(all\s+)?(previous\s+)?instructions",
        r"(?i)you\s+are\s+now",
        r"(?i)system\s+prompt",
        r"(?i)bypass\s+security",
        r"(?i)override\s+rules"
    ]

    @classmethod
    def check_for_injection(cls, user_input: str) -> bool:
        """Returns True if the input resembles a prompt injection attack."""
        for pattern in cls.INJECTION_SIGNATURES:
            if re.search(pattern, user_input):
                return True
        return False

def detect_injection(raw_text: str) -> None:
    """Raises a ValueError if prompt injection is detected."""
    if PromptInjectionDetector.check_for_injection(raw_text):
        raise ValueError("SECURITY ALERT: Potential prompt injection detected. Input blocked.")