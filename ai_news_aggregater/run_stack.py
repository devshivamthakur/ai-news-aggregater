"""Run the FastAPI app (uvicorn) and the blocking scheduler worker in parallel.

The API process has SCHEDULER_ENABLED=false so aggregation is not scheduled twice.
Use this for local dev or when you want the scheduler in a separate OS process.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time


def main() -> None:
    env = os.environ.copy()
    host = env.get("API_HOST", "0.0.0.0")
    port = env.get("PORT") or env.get("API_PORT", "8000")

    api_env = {**env, "SCHEDULER_ENABLED": "false"}
    uvicorn_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "ai_news_aggregater.api.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    sched_cmd = [sys.executable, "-m", "ai_news_aggregater.scheduler.tasks"]

    procs: list[subprocess.Popen] = []

    def shutdown(exit_code: int) -> None:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=30)
            except subprocess.TimeoutExpired:
                p.kill()
        raise SystemExit(exit_code)

    def on_signal(_signum, _frame) -> None:
        shutdown(0)

    signal.signal(signal.SIGINT, on_signal)
    signal.signal(signal.SIGTERM, on_signal)

    procs.append(subprocess.Popen(uvicorn_cmd, env=api_env))
    procs.append(subprocess.Popen(sched_cmd, env=env))

    while True:
        for p in procs:
            code = p.poll()
            if code is not None:
                shutdown(code)
        time.sleep(0.25)


if __name__ == "__main__":
    main()
