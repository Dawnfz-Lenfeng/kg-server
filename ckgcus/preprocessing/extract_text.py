"""
Description:

- 本文件包含TextRecognizer类, 该类是为了支持不同文件类型的预处理而设计.
- 初始支持将PDF文件转换为文本, 预留了扩展接口以支持图像和纯文本的处理.
- 主要用途是为后续的数据分析和知识图谱构建提供预处理过的数据.

Dependencies:
以下是目前使用的库, 后期为了更好的处理效果, 可能会考虑调用更好的api.

- pdfplumber: 用于PDF文件处理.
- pytesseract: 使用Tesseract OCR引擎进行光学字符识别, 可从扫描的图像或PDF文件中提取文本.
- Tesseract: OCR引擎. 安装可参考 https://blog.csdn.net/qq_38463737/article/details/109679007.
- pdf2image: 将PDF文件页转换为图像, 便于OCR识别或进一步的图像处理.
"""

import pdfplumber
import pytesseract
from pdf2image import convert_from_path


def extract_text(
    file_path: str,
    first_page: int = 1,
    last_page: int = None,
    engine: str = "pdfplumber",
    language: str = "eng+chi_sim",
) -> str:
    engine = engine.lower()
    file_type = file_path.split(".")[-1].lower()

    if file_type == "pdf":
        if engine == "pdfplumber":
            return _process_pdf_pdfplumber(file_path, first_page, last_page)
        elif engine == "ocr":
            return _process_pdf_ocr(file_path, first_page, last_page, language)
    elif file_type == "txt":
        return _process_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type or engine: {file_type} with {engine}")


def _process_pdf_pdfplumber(
    file_path: str, first_page: int = 1, last_page: int = None
) -> str:
    text = []

    try:
        with pdfplumber.open(file_path, pages=[first_page, last_page]) as pdf:
            for page in pdf.pages:
                # 处理每一页
                text.append(page.extract_text())
    except Exception as e:
        print(f"Error processing PDF: {e}")

    except Exception as e:
        raise Exception(f"Error processing PDF file with pdfplumber: {e}")

    return "\n".join(text)


def _process_pdf_ocr(
    file_path: str,
    first_page: int = 1,
    last_page: int = None,
    language: str = "eng+chi_sim",
) -> str:
    text = []

    try:
        # 只加载指定范围内的页面
        images = convert_from_path(
            file_path, first_page=first_page, last_page=last_page
        )

        for idx, image in enumerate(images):
            page_num = first_page + idx

            try:
                page_text = pytesseract.image_to_string(image, lang=language)
                if page_text:
                    text.append(page_text)
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                continue

    except Exception as e:
        raise Exception(f"Error processing PDF file with OCR: {e}")

    return "\n".join(text)


def _process_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except Exception as e:
        raise Exception(f"Error processing TXT file: {e}")
