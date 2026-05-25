import sys


BANNER = """
╔══════════════════════════════════════════╗
║          Auto Solver — 单轮模式          ║
║   Parser → Coder → Sandbox → Judge      ║
╚══════════════════════════════════════════╝
"""


def read_problem_text() -> str:
    print("粘贴题面（输入单独一行 --- 结束）:")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "---":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main():
    print(BANNER)

    # --- Load config ---
    from solver.config import settings
    if not settings.deepseek_api_key:
        print("[错误] 未设置 DEEPSEEK_API_KEY，请在 .env 中填入密钥。")
        sys.exit(1)

    # --- Read problem ---
    problem_text = read_problem_text()
    if not problem_text:
        print("[错误] 题面为空。")
        sys.exit(1)

    # --- Init DB ---
    from solver.db import SolverDB
    db = SolverDB()

    # --- Stage 1: Parse ---
    print("\n[Parser]  解析题面...")
    from solver.parser_agent import parse_problem
    try:
        spec = parse_problem(problem_text)
    except Exception as e:
        print(f"[Parser]  解析失败: {e}")
        sys.exit(1)

    session_id = db.create_session(spec.title)
    db.save_problem(spec)
    print(f"[Parser]  标题: {spec.title}")
    print(f"[Parser]  测试用例数: {len(spec.test_cases)}  时限: {spec.time_limit}s  内存: {spec.memory_limit}MB")

    if not spec.test_cases:
        print("[Parser]  警告: 未解析到任何测试用例，跳过执行。")
        sys.exit(1)

    # --- Stage 2: Generate code ---
    print("\n[Coder]   生成代码...")
    from solver.coder_agent import generate_code
    try:
        code = generate_code(spec)
    except Exception as e:
        print(f"[Coder]   代码生成失败: {e}")
        sys.exit(1)

    db.save_solution(code)
    print(f"[Coder]   代码已生成 ({len(code.splitlines())} 行)")

    # --- Stage 3: Run in sandbox ---
    print("\n[Sandbox] 在 Docker 沙箱中执行...")
    from solver.sandbox import run_in_sandbox
    try:
        run_results = run_in_sandbox(code, spec.test_cases, time_limit_sec=spec.time_limit)
    except RuntimeError as e:
        print(f"[Sandbox] {e}")
        sys.exit(1)

    # --- Stage 4: Judge ---
    print("\n[Judge]   评测结果:")
    from solver.judge import judge
    judge_results = judge(run_results, spec.test_cases, time_limit_sec=spec.time_limit)

    passed = 0
    for jr in judge_results:
        print(f"  {jr}")
        if jr.passed():
            passed += 1

    db.save_judge([
        {
            "case": r.case_idx,
            "status": r.status,
            "actual": r.actual,
            "expected": r.expected,
            "elapsed_ms": r.elapsed_ms,
        }
        for r in judge_results
    ])

    # --- Summary ---
    total = len(judge_results)
    print(f"\n{'='*44}")
    print(f"结果: {passed}/{total} 通过", end="")
    if passed == total:
        print("  ✓ 全部 AC！")
    else:
        print()
    print(f"产物已保存至 results/{session_id}/")
    print('='*44)


if __name__ == "__main__":
    main()
