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

1. 安装本库
    这里要仔细看。
    ```bash
    git clone https://github.com/Dawnfz-Lenfeng/CKG_CUS.git
    cd ./CKG_CUS
    pip install -e .
    ```
    此时是动态的安装，你可以任意修改源码，无需重新安装。源码在`CKG_CUS/ckgcus/`目录下。
2. 安装其他依赖项：
    OCR引擎会默认会使用 `cnOCR` ，识别精度较高，但是速度中等，不过无需额外安装。

    另外可选的 OCR 引擎分别为 `paddleOCR` 和 `tesseract`。 
    `paddleOCR`识别精度高，但是速度慢；`tesseract` 识别精度较低，但是速度最快。

    - 如果选择使用 `tesseract` 作为 OCR 引擎，可以按照以下步骤安装 Tesseract：

        - Windows 用户：[Tesseract OCR Windows 安装指南](https://github.com/UB-Mannheim/tesseract/wiki)
        - macOS 用户：
            ```bash
            brew install tesseract
            ```

        再使用`pip install -e .[tesseract]` 安装。
    - 如果选择使用 `paddleOCR` 作为 OCR 引擎，可以按照以下步骤安装 PaddleOCR：
        ```bash
        pip install -e .[paddleocr]
        ```
        如果用户名称为中文名导致无法使用，参考[这里](https://github.com/PaddlePaddle/PaddleOCR/issues/11794)。
    - 如果全部安装，使用`pip install -e .[all]` 。


## 使用示例

以下是一些主要功能的简单使用示例，注意在OCR中使用了多进程，必须仿照此形式定义main()函数！！

- 默认情况（优先使用 pdfplumber，失败时回退到 OCR 引擎）：
```python
from ckgcus.preprocessing import TextPreprocessor

def main():
    text_processor = TextPreprocessor.read_file(
        'path/to/file.pdf', 
        first_page=3, 
        ocr_engine='cnocr',
    )
    text_processor.clean()  # 清洗
    text_processor.save_to_file('output.txt')

if __name__ == '__main__':
    main()
```

- 强制使用 OCR 引擎：
此时不会使用 pdfplumber，而是直接使用 OCR 引擎。
```python
from ckgcus.preprocessing import TextPreprocessor

def main():
    text_processor = TextPreprocessor.read_file(
        'path/to/file.pdf', 
        first_page=3, 
        ocr_engine='cnocr', 
        force_ocr=True
    )
    text_processor.clean()  # 清洗
    text_processor.save_to_file('output.txt')

if __name__ == '__main__':
    main()
```

## 贡献

欢迎对本项目进行贡献，包括但不限于：

- 提交代码修复和功能改进。
- 添加新的预处理接口。
- 提供更多使用示例和文档。

## 许可证

本项目遵循 MIT 许可证。请查看 `LICENSE` 文件了解更多信息。
