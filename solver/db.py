import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class ProblemSpec:
    title: str
    time_limit: int = 1
    memory_limit: int = 256
    constraints: list = field(default_factory=list)
    input_format: str = ""
    output_format: str = ""
    test_cases: list = field(default_factory=list)  # [{"input": ..., "output": ...}]

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "time_limit": self.time_limit,
            "memory_limit": self.memory_limit,
            "constraints": self.constraints,
            "input_format": self.input_format,
            "output_format": self.output_format,
            "test_cases": self.test_cases,
        }


class SolverDB:
    """File-based storage for a single solver run."""

    def __init__(self, base_dir: str = "results"):
        self._base = Path(base_dir)
        self._root: Path | None = None
        self._lock = threading.Lock()

    def create_session(self, title: str) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in title)[:40]
        session_id = f"{safe_title}_{ts}"
        self._root = self._base / session_id
        self._root.mkdir(parents=True, exist_ok=True)
        return session_id

    @property
    def root(self) -> Path:
        if self._root is None:
            raise RuntimeError("Session not created yet")
        return self._root

    def save_problem(self, spec: ProblemSpec):
        with self._lock:
            (self.root / "problem.json").write_text(
                json.dumps(spec.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
            )

    def save_solution(self, code: str):
        with self._lock:
            (self.root / "solution.py").write_text(code, encoding="utf-8")

    def save_judge(self, results: list):
        with self._lock:
            (self.root / "judge.json").write_text(
                json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
            )
