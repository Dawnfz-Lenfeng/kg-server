# CKG-CUS: 中文知识图谱构建与更新系统

## 项目描述

CKG-CUS（Chinese Knowledge Graph Construction and Update System，中文知识图谱构建与更新系统）是一个用于从各种中文语料中构建和更新知识图谱的系统，旨在推动中文自然语言处理和学术探索。该系统提供了一整套工具链，从数据收集和预处理到知识图谱的构建与实时更新。它支持从 PDF 文件、图像文件等多种格式中提取数据，并集成了 OCR 和高级自然语言处理技术。

## 主要功能

- 从 PDF 文件中提取结构化或非结构化数据。
- 使用 OCR 技术从图像或扫描的 PDF 中提取文本。
- 提供多种文件预处理接口以供未来扩展。
- 支持中英文混合文本的处理。
- 自动更新和构建知识图谱。

## 安装

请确保已安装 Python 3.10 及以上版本。使用以下步骤安装项目及其依赖项：

1. 安装 Tesseract OCR（用于图像识别）：
    - Windows 用户：[Tesseract OCR Windows 安装指南](https://github.com/UB-Mannheim/tesseract/wiki)
    - macOS 用户：
        ```bash
        brew install tesseract
        ```

## 使用示例

以下是一些主要功能的简单使用示例：

1. **从 PDF 文件中提取文本**
    ```python
    from ckgcus.preprocessing import FilePreprocessor

    # 初始化 PDF 预处理器并提取文本
    preprocessor = FilePreprocessor('path/to/file.pdf', file_type='pdf')
    text = preprocessor.process(engine='pdfplumber')
    print(text)
    ```

2. **从使用OCR技术提取文本**
    ```python
    from ckgcus.preprocessing import FilePreprocessor

    # 初始化图像预处理器并使用 OCR 提取文本
    preprocessor = FilePreprocessor('path/to/image.png', file_type='image')
    text = preprocessor.process(engine='ocr', language='eng+chi_sim')
    print(text)
    ```

## 依赖项

- `pdfplumber`：从 PDF 文件中提取文本和结构化数据
- `pytesseract`：Tesseract OCR 引擎的 Python 接口
- `pdf2image`：将 PDF 文件转换为图像
