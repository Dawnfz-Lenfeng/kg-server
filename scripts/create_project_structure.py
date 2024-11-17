import os
from pathlib import Path


def create_structure():
    """创建项目目录结构"""
    # 基础目录
    base_dirs = [
        "backend/app/models",
        "backend/app/schemas",
        "backend/app/api",
        "backend/app/services",
        "backend/tests",
        "frontend/src/components",
        "frontend/src/views",
        "frontend/src/api",
        "frontend/src/store",
        "frontend/tests",
    ]

    # Python文件
    py_files = [
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/app/config.py",
        "backend/app/database.py",
        "backend/app/models/__init__.py",
        "backend/app/models/document.py",
        "backend/app/models/keyword.py",
        "backend/app/models/subject.py",
        "backend/app/schemas/__init__.py",
        "backend/app/schemas/document.py",
        "backend/app/schemas/keyword.py",
        "backend/app/schemas/subject.py",
        "backend/app/api/__init__.py",
        "backend/app/api/documents.py",
        "backend/app/api/keywords.py",
        "backend/app/api/graph.py",
        "backend/app/services/__init__.py",
        "backend/app/services/document.py",
        "backend/app/services/graph.py",
    ]

    # Vue文件
    vue_files = [
        "frontend/src/components/FileUpload.vue",
        "frontend/src/components/GraphView.vue",
    ]

    # 创建目录
    for dir_path in base_dirs:
        (Path("CKG_CUS/ckgcus") / Path(dir_path)).mkdir(parents=True, exist_ok=True)

    # 创建文件
    for file_path in py_files + vue_files:
        (Path("CKG_CUS/ckgcus") / Path(file_path)).touch()


if __name__ == "__main__":
    create_structure()
