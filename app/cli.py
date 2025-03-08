import signal
import subprocess
import sys
import time
from pathlib import Path

import typer

cli = typer.Typer()


def init_database(root_dir: Path):
    """初始化数据库"""
    print("Initializing database...")
    subprocess.run([sys.executable, "scripts/init_db.py"], cwd=root_dir, check=True)


def start_worker(root_dir: Path) -> subprocess.Popen:
    """启动 worker 进程"""
    return subprocess.Popen(
        [sys.executable, "-m", "arq", "app.core.arq.WorkerSettings"], cwd=root_dir
    )


def handle_sigterm(api_process: subprocess.Popen, worker_process: subprocess.Popen):
    """处理终止信号"""

    def handler(signum, frame):
        print("\nShutting down gracefully...")
        api_process.terminate()
        worker_process.terminate()
        api_process.wait()
        worker_process.wait()
        sys.exit(0)

    return handler


@cli.command()
def dev(init: bool = typer.Option(False, "--init", help="初始化数据库")):
    """启动开发服务器和 worker"""
    root_dir = Path(__file__).parent.parent

    if init:
        init_database(root_dir)

    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"], cwd=root_dir
    )

    worker_process = start_worker(root_dir)

    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_sigterm(api_process, worker_process))

    # 监控进程状态
    while True:
        # 检查 worker 进程
        if worker_process.poll() is not None:
            print("Worker process terminated, restarting...")
            worker_process = start_worker(root_dir)

        time.sleep(1)  # 避免过于频繁的检查


@cli.command()
def api():
    """只启动 API 服务器"""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ]
    )


@cli.command()
def worker():
    """只启动 worker"""
    subprocess.run([sys.executable, "-m", "arq", "app.core.arq.WorkerSettings"])


def main():
    cli()


if __name__ == "__main__":
    main()
