import argparse
import asyncio
from pathlib import Path

import aiohttp

SUPPORTED_TYPES = {".pdf", ".txt"}
API_URL = "http://localhost:8000/api/v1/documents"


async def upload_file(
    session: aiohttp.ClientSession, path: Path, subject_id: int
) -> int:
    data = aiohttp.FormData()
    data.add_field("file", path.read_bytes(), filename=path.name)
    data.add_field("subject_id", str(subject_id))

    async with session.post(API_URL, data=data) as resp:
        if resp.status != 200:
            print(f"✗ 上传失败: {path.name}, 状态码: {resp.status}")
            return None

        result = await resp.json()
        if not result["success"]:
            print(f"✗ 上传失败: {path.name}, 错误: {result['error']}")
            return None

        print(f"✓ 上传成功: {path.name}")
        return result["document"]["id"]


async def upload_files(
    session: aiohttp.ClientSession, paths: list[Path], subject_id: int
) -> list[int]:
    data = aiohttp.FormData()
    for path in paths:
        data.add_field(
            f"files",
            path.read_bytes(),
            filename=path.name,
        )
    data.add_field("subject_id", str(subject_id))

    doc_ids = []
    async with session.post(f"{API_URL}/batch", data=data) as resp:
        if resp.status != 200:
            error_text = await resp.text()
            print(f"✗ 上传失败: 状态码: {resp.status}, 错误信息: {error_text}")
            return []

        results = await resp.json()

        for result in results:
            if not result["success"]:
                print(f"✗ 上传失败: 错误: {result['error']}")
                continue

            print(f"✓ 上传成功: {result['document']['title']}")
            doc_ids.append(result["document"]["id"])

        print(f"✓ 上传成功: {len(doc_ids)}/{len(paths)} 个文件")
        return doc_ids


async def process_file(
    session: aiohttp.ClientSession, doc_id: int, subject_id: int
) -> bool:
    """上传并处理单个文件"""
    async with session.put(f"{API_URL}/{doc_id}/extract") as resp:
        if resp.status != 200:
            print(f"✗ 提取文本失败: {doc_id}")
            return False

    # 清洗文本
    async with session.put(f"{API_URL}/{doc_id}/normalize") as resp:
        if resp.status != 200:
            print(f"✗ 清洗文本失败: {doc_id}")
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

    async with aiohttp.ClientSession() as session:
        print("开始上传文档...")
        if path.is_file():
            if path.suffix.lower() in SUPPORTED_TYPES:
                doc_ids = [await upload_file(session, path, args.subject)]
        else:
            files = [f for f in path.iterdir() if f.suffix.lower() in SUPPORTED_TYPES]
            doc_ids = await upload_files(session, files, args.subject)

        doc_ids = [doc_id for doc_id in doc_ids if doc_id is not None]

        if not doc_ids:
            print("没有文件上传成功")
            return

        print(f"上传成功: {len(doc_ids)} 个文件")

        tasks = [process_file(session, doc_id, args.subject) for doc_id in doc_ids]

        results = await asyncio.gather(*tasks)

    success_count = sum(results)
    print(f"\n处理完成: {success_count}/{len(doc_ids)} 个文件成功")


if __name__ == "__main__":
    asyncio.run(main())
