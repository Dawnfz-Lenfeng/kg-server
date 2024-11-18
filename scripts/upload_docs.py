import argparse
from pathlib import Path

import requests


def upload_document(file_path: str, title: str, subject_id: int):
    """上传单个文档"""
    url = "http://localhost:8000/api/v1/documents"

    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"title": title, "subject_id": subject_id}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print(f"✓ Successfully uploaded: {title}")
            return response.json()
        else:
            print(f"✗ Upload failed: {title}")
            print(f"Error message: {response.text}")

            return None


def batch_upload(folder_path: str, subject_id: int):
    """批量上传文件夹中的文档"""
    docs_dir = Path(folder_path)
    if not docs_dir.exists():
        print(f"Error: folder path: '{folder_path}' does not exist")
        return

    for pdf_file in docs_dir.glob("*.pdf"):
        upload_document(
            file_path=str(pdf_file), title=pdf_file.stem, subject_id=subject_id
        )


def main():
    parser = argparse.ArgumentParser(description="文档上传工具")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="单个文件路径")
    group.add_argument("--folder", help="文件夹路径")

    parser.add_argument("--title", help="文档标题（仅用于单文件上传）")
    parser.add_argument(
        "--subject",
        type=int,
        required=True,
        help="学科ID (1=金融, 2=经济, 3=统计, 4=数据科学)",
    )

    args = parser.parse_args()

    if args.file:
        # 单文件上传
        title = args.title or Path(args.file).stem
        upload_document(args.file, title, args.subject)
    else:
        # 批量上传
        batch_upload(args.folder, args.subject)


if __name__ == "__main__":
    main()
