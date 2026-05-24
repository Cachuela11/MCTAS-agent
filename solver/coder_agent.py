import json
from agno.agent import Agent
from solver.config import settings
from solver.models import create_model
from solver.db import ProblemSpec
from solver.utils import extract_code_block

CODER_SYSTEM = """You are an expert competitive programmer specializing in Python solutions.

Given a structured problem specification (JSON), write a complete, correct, and efficient Python solution.

Rules:
- Read input from stdin using input() or sys.stdin.
- Print the answer to stdout.
- Handle all edge cases described in the constraints.
- Use efficient algorithms appropriate for the given constraints.
- Return ONLY the Python code, wrapped in ```python ... ```. No explanations.
"""


def generate_code(spec: ProblemSpec) -> str:
    model = create_model(settings.google_model, settings.google_api_key)
    agent = Agent(model=model, system_prompt=CODER_SYSTEM, markdown=False)

    prompt = f"Solve the following problem:\n\n```json\n{json.dumps(spec.to_dict(), indent=2)}\n```"
    response = agent.run(prompt)
    raw = response.content if hasattr(response, "content") else str(response)

    return extract_code_block(raw)
