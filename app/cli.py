import subprocess
import sys
from pathlib import Path

import typer

cli = typer.Typer()


def init_database(root_dir: Path):
    """初始化数据库"""
    print("Initializing database...")
    subprocess.run([sys.executable, "scripts/init_db.py"], cwd=root_dir, check=True)


@cli.command()
def dev(init: bool = typer.Option(False, "--init", help="初始化数据库")):
    """启动开发服务器和 worker"""
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent

    # 如果需要初始化数据库
    if init:
        init_database(root_dir)

    # 启动 FastAPI 服务
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload"], cwd=root_dir
    )

    # 启动 Arq worker
    worker_process = subprocess.Popen(
        [sys.executable, "-m", "arq", "app.core.arq.WorkerSettings"], cwd=root_dir
    )

    try:
        # 等待任意一个进程结束
        api_process.wait()
        worker_process.wait()
    finally:
        # 确保两个进程都被终止
        api_process.terminate()
        worker_process.terminate()


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
