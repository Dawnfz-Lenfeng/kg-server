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


def start_workers(root_dir: Path, num_workers: int = 4) -> list[subprocess.Popen]:
    """启动多个 worker 进程"""
    workers = []
    for _ in range(num_workers):
        worker = subprocess.Popen(
            [sys.executable, "-m", "arq", "app.core.arq.WorkerSettings"], cwd=root_dir
        )
        workers.append(worker)
    return workers


@cli.command()
def dev(
    init: bool = typer.Option(False, "--init", help="初始化数据库"),
    workers: int = typer.Option(4, "--workers", "-w", help="worker 进程数量"),
):
    """启动开发服务器和 workers"""
    root_dir = Path(__file__).parent.parent

    if init:
        init_database(root_dir)

    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"], cwd=root_dir
    )

    worker_processes = start_workers(root_dir, workers)

    def handle_sigterm():
        print("\nShutting down gracefully...")
        api_process.terminate()
        for i, worker in enumerate(worker_processes):
            worker.terminate()
            print(f"Worker {i} terminated")
        api_process.wait()
        for worker in worker_processes:
            worker.wait()
        sys.exit(0)

    signal.signal(signal.SIGINT, lambda s, f: handle_sigterm())

    while True:
        # 检查 worker 进程
        for i, worker in enumerate(worker_processes):
            if worker.poll() is not None:
                print(f"Worker {i} terminated, restarting...")
                worker_processes[i] = start_worker(root_dir)
        time.sleep(1)


@cli.command()
def api():
    """只启动 API 服务器"""
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--reload"])


@cli.command()
def worker():
    """只启动 worker"""
    subprocess.run([sys.executable, "-m", "arq", "app.core.arq.WorkerSettings"])


def main():
    cli()


if __name__ == "__main__":
    main()
