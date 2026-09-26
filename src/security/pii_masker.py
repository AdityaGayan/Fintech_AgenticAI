import re
from typing import Tuple, List

class PIIMasker:
    # Regex patterns for sensitive financial and personal data
    PATTERNS = {
        "CREDIT_CARD": r'\b(?:\d[ -]*?){13,19}\b',
        "SSN": r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b',
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        "ACCOUNT_NUMBER": r'\b(?:Acct|Account)[\s:-]*\d{8,12}\b'
    }

    @classmethod
    def mask_text(cls, text: str) -> Tuple[str, List[str]]:
        """
        Scans input for sensitive patterns and replaces them with standard tokens.
        Returns the sanitized string and a list of detected threat types.
        """
        sanitized_text = text
        detected_types = set()

        for pii_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, sanitized_text, flags=re.IGNORECASE)
            if matches:
                # Extra validation for Credit Cards (strip hyphens and check length)
                if pii_type == "CREDIT_CARD":
                    for match in matches:
                        clean_match = re.sub(r'[\s-]', '', match)
                        if 13 <= len(clean_match) <= 19:
                            sanitized_text = sanitized_text.replace(match, f"[MASKED_{pii_type}]")
                            detected_types.add(pii_type)
                else:
                    sanitized_text = re.sub(pattern, f"[MASKED_{pii_type}]", sanitized_text, flags=re.IGNORECASE)
                    detected_types.add(pii_type)

        return sanitized_text, list(detected_types)

def sanitize_input(raw_text: str) -> Tuple[str, List[str]]:
    """Entry point for the data sanitization pipeline."""
    return PIIMasker.mask_text(raw_text)