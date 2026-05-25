from agno.agent import Agent
from solver.config import settings
from solver.models import create_model
from solver.db import ProblemSpec
from solver.utils import parse_json_fenced

PARSER_SYSTEM = """You are an expert competitive programming problem parser.

Given a problem statement, extract the following fields and return ONLY a JSON object (no extra text):
{
  "title": "<short problem title>",
  "time_limit": <seconds as integer, default 1>,
  "memory_limit": <MB as integer, default 256>,
  "constraints": ["<constraint string>", ...],
  "input_format": "<description of input format>",
  "output_format": "<description of output format>",
  "test_cases": [
    {"input": "<exact input string with \\n for newlines>", "output": "<exact expected output>"},
    ...
  ]
}

Rules:
- Include ALL sample test cases from the problem.
- Use actual newline characters (\\n) inside the input/output strings.
- If time/memory limits are not stated, use defaults (1s / 256MB).
- Return ONLY the JSON, wrapped in ```json ... ```.
"""


def parse_problem(problem_text: str) -> ProblemSpec:
    model = create_model(settings.deepseek_model, settings.deepseek_api_key)
    agent = Agent(model=model, instructions=PARSER_SYSTEM, markdown=False)

    response = agent.run(problem_text)
    raw = response.content if hasattr(response, "content") else str(response)

    data = parse_json_fenced(raw)
    return ProblemSpec(
        title=data.get("title", "problem"),
        time_limit=int(data.get("time_limit", 1)),
        memory_limit=int(data.get("memory_limit", 256)),
        constraints=data.get("constraints", []),
        input_format=data.get("input_format", ""),
        output_format=data.get("output_format", ""),
        test_cases=data.get("test_cases", []),
    )
