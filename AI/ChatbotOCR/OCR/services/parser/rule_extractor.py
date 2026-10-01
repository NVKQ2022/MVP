"""Rule-Based Extractor: Deterministic regex and pattern parsing for error screenshots."""

import re
from typing import Any, Optional
from pydantic import BaseModel, Field


class ExtractedIssue(BaseModel):
    """Structured issue extracted deterministically from raw OCR text without LLM."""

    error_codes: list[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    details: Optional[str] = None
    product: Optional[str] = None
    module: Optional[str] = None
    raw_text: str = ""

    @property
    def primary_error_code(self) -> Optional[str]:
        return self.error_codes[0] if self.error_codes else None


# Known error code patterns in support screenshots
ERROR_CODE_REGEX = re.compile(
    r"\b("
    r"AUTH-\d+|ACCOUNT-LOCKED|EMAIL-VERIFY-\d+|"
    r"TIMEOUT|SERVICE-\d+|DNS-\d+|"
    r"DB-\d+|SQLSTATE\[[A-Za-z0-9]+\]|DB-CONN-\d+|DB-DEADLOCK-\d+|"
    r"FILE-\d+|RESOURCE-\d+|HTTP\s*\d{3}"
    r")\b",
    re.IGNORECASE,
)


class RuleBasedExtractor:
    """Deterministic extractor parsing key-value pairs and error codes from OCR lines."""

    def extract(self, full_text: str, lines: list[str] | None = None) -> ExtractedIssue:
        """
        Extract structured error information using regular expressions and heuristics.
        Does NOT rely on an LLM.
        """
        raw = full_text or ""
        text_lines = lines if lines is not None else [l.strip() for l in raw.split("\n") if l.strip()]

        error_codes: list[str] = []
        error_message: Optional[str] = None
        details: Optional[str] = None
        product: Optional[str] = None
        module: Optional[str] = None

        # 1. Detect explicit 'Error Code:', 'Message:', 'Details:' key-value pairs
        for line in text_lines:
            line_clean = line.strip()

            # Error Code: ...
            if re.search(r"Error\s*Code\s*[:：]", line_clean, re.IGNORECASE):
                val = re.sub(r"^.*?Error\s*Code\s*[:：]\s*", "", line_clean, flags=re.IGNORECASE).strip()
                matches = ERROR_CODE_REGEX.findall(val)
                if matches:
                    for m in matches:
                        code_norm = m.strip().upper()
                        if code_norm not in error_codes:
                            error_codes.append(code_norm)
                elif val:
                    error_codes.append(val)

            # Message: ...
            elif re.search(r"^Message\s*[:：]", line_clean, re.IGNORECASE):
                val = re.sub(r"^Message\s*[:：]\s*", "", line_clean, flags=re.IGNORECASE).strip()
                if val:
                    error_message = val

            # Details: ...
            elif re.search(r"^Details\s*[:：]", line_clean, re.IGNORECASE):
                val = re.sub(r"^Details\s*[:：]\s*", "", line_clean, flags=re.IGNORECASE).strip()
                if val:
                    details = val

            # Product / Portal Detection
            if "customer portal" in line_clean.lower():
                product = "Customer Portal"
            elif "admin portal" in line_clean.lower():
                product = "Admin Portal"

        # 2. Fallback regex scan for error codes if not caught by label
        if not error_codes:
            for match in ERROR_CODE_REGEX.findall(raw):
                code_norm = match.strip().upper()
                if code_norm not in error_codes:
                    error_codes.append(code_norm)

        # 3. Fallback message detection for 'no_error_code' variants
        # If Message label was missing or blurred, look for error dialog subtitle
        if not error_message:
            for idx, line in enumerate(text_lines):
                if re.search(r"\bError\b", line, re.IGNORECASE) and idx + 1 < len(text_lines):
                    next_line = text_lines[idx + 1].strip()
                    # Skip generic boilerplate "The operation could not be completed"
                    if "operation could not be completed" in next_line.lower() and idx + 2 < len(text_lines):
                        candidate = text_lines[idx + 2].strip()
                        if not re.search(r"^(Error Code|Details|OK)\b", candidate, re.IGNORECASE):
                            error_message = candidate
                    elif not re.search(r"^(Error Code|Details|OK)\b", next_line, re.IGNORECASE):
                        error_message = next_line
                    break

        return ExtractedIssue(
            error_codes=error_codes,
            error_message=error_message,
            details=details,
            product=product,
            module=module,
            raw_text=raw,
        )


rule_extractor = RuleBasedExtractor()
