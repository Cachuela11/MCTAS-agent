import io
import tarfile
import time
import threading
from dataclasses import dataclass
from typing import Optional

from solver.config import settings

_active_containers: list = []
_lock = threading.Lock()


@dataclass
class RunResult:
    stdout: str
    stderr: str
    exit_code: int
    elapsed_ms: int


def _get_client():
    import docker
    return docker.from_env()


def _check_docker():
    try:
        import docker
    except ImportError:
        raise RuntimeError("Install docker SDK: pip install docker")
    try:
        _get_client().ping()
    except Exception as e:
        raise RuntimeError(f"Docker daemon not reachable: {e}")


def _make_tar(filename: str, content: str) -> bytes:
    """Pack a single text file into an in-memory tar archive."""
    data = content.encode("utf-8")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        info = tarfile.TarInfo(name=filename)
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def run_in_sandbox(code: str, test_cases: list, time_limit_sec: Optional[int] = None) -> list:
    """
    Run `code` against each test case in a fresh Docker container.
    Returns a RunResult per test case.
    """
    _check_docker()
    client = _get_client()
    limit = time_limit_sec or settings.time_limit_sec
    mem = settings.memory_limit_mb

    container = client.containers.run(
        image="python:3.11-slim",
        command="sleep infinity",
        detach=True,
        mem_limit=f"{mem}m",
        nano_cpus=1_000_000_000,
        network_disabled=True,
    )
    with _lock:
        _active_containers.append(container)

    results: list[RunResult] = []
    try:
        # Upload solution.py once
        container.put_archive("/tmp", _make_tar("solution.py", code))

        for tc in test_cases:
            stdin_data = tc.get("input", "")
            # Write input file
            container.put_archive("/tmp", _make_tar("input.txt", stdin_data))

            start = time.monotonic()
            exec_result = container.exec_run(
                cmd=["bash", "-c", "python /tmp/solution.py < /tmp/input.txt"],
                workdir="/tmp",
            )
            elapsed_ms = int((time.monotonic() - start) * 1000)

            stdout = exec_result.output.decode("utf-8", errors="replace") if exec_result.output else ""
            results.append(RunResult(
                stdout=stdout,
                stderr="",
                exit_code=exec_result.exit_code,
                elapsed_ms=elapsed_ms,
            ))
    finally:
        with _lock:
            try:
                _active_containers.remove(container)
            except ValueError:
                pass
        try:
            container.kill()
        except Exception:
            pass
        try:
            container.remove(force=True)
        except Exception:
            pass

    return results


def kill_all_containers():
    with _lock:
        snapshot = list(_active_containers)
        _active_containers.clear()
    for c in snapshot:
        try:
            c.kill()
        except Exception:
            pass
        try:
            c.remove(force=True)
        except Exception:
            pass
