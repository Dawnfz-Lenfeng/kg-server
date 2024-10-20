import logging
import math
from functools import partial
from multiprocessing import Pool, cpu_count
from typing import Optional

import pdfplumber
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text(
    file_path: str,
    first_page: int = 1,
    last_page: Optional[int] = None,
    engine: str = "pdfplumber",
    language: str = "chi_sim",
    max_workers: Optional[int] = None,
) -> str:
    engine = engine.lower()
    file_type = file_path.split(".")[-1].lower()

    # 获取 PDF 的总页数
    pdf_info = pdfinfo_from_path(file_path, userpw=None, poppler_path=None)
    total_pages = pdf_info["Pages"]
    last_page = last_page or total_pages

    if first_page < 1 or last_page > total_pages:
        raise ValueError("Page range is out of bounds.")

    page_numbers = list(range(first_page, last_page + 1))

    if max_workers is None:
        # 设置线程数为 CPU 核心数的 2 倍，最多 32 个线程
        cpu_cores = cpu_count()
        max_workers = min(math.ceil(total_pages / 10), cpu_cores * 2, 32)

    if file_type == "pdf":
        if engine == "pdfplumber":
            return process_pdf_pdfplumber(
                file_path,
                page_numbers,
                max_workers,
            )
        elif engine == "ocr":
            return process_pdf_ocr(
                file_path,
                page_numbers,
                language,
                max_workers,
            )
    elif file_type == "txt":
        return process_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type or engine: {file_type} with {engine}")


def process_pdf_pdfplumber(
    file_path: str, page_numbers: list[int], max_workers: int
) -> str:
    text = []

    with pdfplumber.open(file_path) as pdf:
        for page_num in page_numbers:
            page = pdf.pages[page_num - 1]
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
            else:
                logger.info(f"Page {page_num} has no extractable text.")

    return "\n".join(text)


def process_pdf_ocr(
    file_path: str, page_numbers: list[int], language: str, max_workers: int
) -> str:
    text = []

    try:
        with Pool(processes=max_workers) as pool:
            convert_partial = partial(_convert_page_to_image, file_path)
            images = pool.map(convert_partial, page_numbers)

            ocr_partial = partial(_ocr_image, language)
            ocr_results = pool.map(ocr_partial, images)

        for page_num, ocr_text in zip(page_numbers, ocr_results):
            if ocr_text:
                text.append((page_num, ocr_text))

        # 按页码排序文本
        text.sort(key=lambda x: x[0])
        text = [content for _, content in text]

    except Exception as e:
        raise Exception(f"Error processing PDF file with OCR: {e}")

    return "\n".join(text)


def process_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except Exception as e:
        raise Exception(f"Error processing TXT file: {e}")


def _convert_page_to_image(file_path, page_num):
    try:
        images = convert_from_path(file_path, first_page=page_num, last_page=page_num)
        return images[0]
    except Exception as e:
        logger.warning(f"Error converting page {page_num}: {e}")
        return None


def _ocr_image(language: str, image):
    if image is None:
        return None
    try:
        return pytesseract.image_to_string(image, lang=language)
    except Exception as e:
        logger.warning(f"Error processing OCR: {e}")
        return None


def _extract_page_text(file_path: str, page_num: int):
    try:
        with pdfplumber.open(file_path, pages=[page_num]) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
            if text is None:
                logger.warning(f"No text found on page {page_num}.")
            return text
    except Exception as e:
        logger.error(f"Error extracting text from page {page_num}: {e}")
        return None
