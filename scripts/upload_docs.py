import requests
from pathlib import Path


def upload_document(file_path: str, title: str, subject_id: int):
    """上传单个文档"""
    url = "http://localhost:8000/api/v1/documents"

    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"title": title, "subject_id": subject_id}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            print(f"✓ 成功上传: {title}")
            return response.json()
        else:
            print(f"✗ 上传失败: {title}")
            print(f"错误信息: {response.text}")
            return None


# 使用示例
if __name__ == "__main__":
    # 单个文件上传
    upload_document(file_path="docs/金融市场.pdf", title="金融市场分析", subject_id=1)  # 金融

    # 批量上传
    docs_dir = Path("docs/金融文献")
    for pdf_file in docs_dir.glob("*.pdf"):
        upload_document(
            file_path=str(pdf_file),
            title=pdf_file.stem,  # 使用文件名作为标题
            subject_id=1,  # 金融
        )
