import argparse
import asyncio
from pathlib import Path

import aiohttp
from tqdm import tqdm

SUPPORTED_TYPES = {".pdf", ".txt"}
API_URL = "http://localhost:8000/api/v1/documents"


async def process_file(
    session: aiohttp.ClientSession, file_path: Path, subject_id: int
) -> bool:
    """上传并处理单个文件"""
    file_content = file_path.read_bytes()

    data = aiohttp.FormData()
    data.add_field("file", file_content, filename=file_path.name)
    data.add_field("subject_id", str(subject_id))

    async with session.post(API_URL, data=data) as resp:
        if resp.status != 200:
            print(f"✗ 上传失败: {file_path.name}, 状态码: {resp.status}")
            return False
        doc = await resp.json()
        doc_id = doc["id"]

    async with session.post(f"{API_URL}/{doc_id}/extract") as resp_extract:
        if resp_extract.status != 200:
            print(f"✗ 提取文本失败: {file_path.name}, 状态码: {resp_extract.status}")
            return False

    async with session.post(f"{API_URL}/{doc_id}/normalize") as resp_normalize:
        if resp_normalize.status != 200:
            print(f"✗ 清洗文本失败: {file_path.name}, 状态码: {resp_normalize.status}")
            return False

    return True


async def main():
    parser = argparse.ArgumentParser(description="上传并处理文档")
    parser.add_argument("path", help="文件或文件夹路径")
    parser.add_argument("--subject", type=int, required=True, help="学科ID")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"路径不存在: {path}")
        return

    if path.is_file():
        files = [path] if path.suffix.lower() in SUPPORTED_TYPES else []
    else:
        files = [f for f in path.iterdir() if f.suffix.lower() in SUPPORTED_TYPES]

    if not files:
        print(f"没有找到支持的文件 (支持: {', '.join(SUPPORTED_TYPES)})")
        return

    results = []
    async with aiohttp.ClientSession() as session:
        tasks = [process_file(session, f, args.subject) for f in files]

        for task in tqdm(
            asyncio.as_completed(tasks), total=len(files), desc="uploading", unit="file"
        ):
            results.append(await task)

        print(f"\nProcessed: {sum(results)}/{len(files)} files successfully.")


if __name__ == "__main__":
    asyncio.run(main())
