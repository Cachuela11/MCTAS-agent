import json
import re


def parse_json_fenced(text: str) -> dict:
    """Extract JSON from a fenced code block or raw text."""
    # Try ```json ... ``` block first
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    # Fallback: find first { ... } spanning the whole JSON object
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    raise ValueError("No JSON found in response")


def extract_code_block(text: str) -> str:
    """Extract code from a ```python ... ``` block."""
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # Fallback: return as-is (model may have skipped the fence)
    return text.strip()
