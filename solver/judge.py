from dataclasses import dataclass
from typing import Optional, List
from solver.sandbox import RunResult
from solver.config import settings


@dataclass
class JudgeResult:
    status: str        # AC | WA | TLE | RE | MLE
    case_idx: int
    actual: str
    expected: str
    elapsed_ms: int

    def passed(self) -> bool:
        return self.status == "AC"

    def __str__(self) -> str:
        if self.status == "AC":
            return f"用例 {self.case_idx + 1}: AC ({self.elapsed_ms}ms)"
        elif self.status == "WA":
            actual_preview = repr(self.actual[:80])
            expected_preview = repr(self.expected[:80])
            return (
                f"用例 {self.case_idx + 1}: WA ({self.elapsed_ms}ms)\n"
                f"  实际输出: {actual_preview}\n"
                f"  期望输出: {expected_preview}"
            )
        elif self.status == "TLE":
            return f"用例 {self.case_idx + 1}: TLE ({self.elapsed_ms}ms, 限制 {settings.time_limit_sec * 1000}ms)"
        elif self.status == "RE":
            return f"用例 {self.case_idx + 1}: RE (运行时错误, exit_code != 0)"
        else:
            return f"用例 {self.case_idx + 1}: {self.status} ({self.elapsed_ms}ms)"


def judge(run_results: List[RunResult], test_cases: list, time_limit_sec: Optional[int] = None) -> List[JudgeResult]:
    limit_ms = (time_limit_sec or settings.time_limit_sec) * 1000
    results = []
    for i, (run, tc) in enumerate(zip(run_results, test_cases)):
        expected = tc.get("output", "").strip()
        actual = run.stdout.strip()

        if run.exit_code != 0:
            status = "RE"
        elif run.elapsed_ms > limit_ms:
            status = "TLE"
        elif actual == expected:
            status = "AC"
        else:
            status = "WA"

        results.append(JudgeResult(
            status=status,
            case_idx=i,
            actual=actual,
            expected=expected,
            elapsed_ms=run.elapsed_ms,
        ))
    return results
