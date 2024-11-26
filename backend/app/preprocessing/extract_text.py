import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Callable

import pdfplumber
import pytesseract
from cnocr import CnOcr
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL.Image import Image
from tqdm import tqdm

if TYPE_CHECKING:
    import numpy as np
    from paddleocr import PaddleOCR


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

THREAD_LOCK = threading.Lock()


def extract_text(
    file_path: str,
    file_type: str,
    first_page: int = 1,
    last_page: int | None = None,
    ocr_engine: str = "cnocr",
    num_workers: int = 4,
    force_ocr: bool = False,
) -> str:
    """提取文本内容. 如果文件是 pdf, 会优先使用 pdfolumber 提取文本, 否则使用 OCR 提取文本.

    :param file_path: 需要处理的文件路径
    :param file_type: 需要处理的文件类型
    :param first_page: 需要处理的起始页码, 默认为1
    :param last_page: 需要处理的结束页码, 默认为None, 表示处理到最后一页
    :param ocr_engine: OCR引擎, 默认为 'cnocr', 可选 'tesseract', 'paddleocr'
        - cnocr: 精度和速度都适中
        - paddleocr: 精度最高但是最慢
        - tesseract: 精度最低但是最快
    :param num_workers: 用于并行处理的线程数, 默认为4
    :param force_ocr: 是否强制使用 OCR 引擎, 默认为 False
    """
    ocr_engine = ocr_engine.lower()

    if ocr_engine not in OCR_ENGINES:
        raise ValueError(f"Unsupported OCR engine: {ocr_engine}")

    if file_type not in {"pdf", "txt"}:
        raise ValueError(f"Unsupported file type: {file_type}")

    if file_type == "txt":
        return read_txt(file_path)

    pages = get_pdf_pages(file_path, first_page, last_page)

    if not force_ocr:
        if text := extract_pdf_text(file_path, pages):
            return text
        logger.info("PDFplumber extraction failed, trying OCR...")

    if ocr_engine == "tesseract":
        os.environ["OMP_THREAD_LIMIT"] = "1"

    text = OCR_ENGINES[ocr_engine](file_path, pages, num_workers)

    if not text:
        logger.warning("No text content extracted")

    return text


def read_txt(file_path: str) -> str:
    """读取TXT文本"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_pdf_text(file_path: str, pages: list[int]) -> str:
    """使用PDFplumber从PDF中提取文本"""
    logger.info("Starting PDFplumber extraction...")
    texts = []

    with pdfplumber.open(file_path, pages=pages) as pdf:
        for page in tqdm(pdf.pages, total=len(pages), unit="page"):
            if text := page.extract_text():
                texts.append(text)

    return "".join(texts)


def extract_with_ocr(
    file_path: str,
    pages: list[int],
    num_workers: int,
    ocr_engine: str,
    extract_page: Callable[[str, int], str | None],
) -> str:
    """使用OCR提取文本的通用函数，支持多线程处理"""
    logger.info(f"Starting {ocr_engine} extraction with {num_workers} workers...")
    results = []

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(extract_page, file_path, num): num for num in pages}

        for future in tqdm(as_completed(futures), total=len(pages), unit="page"):
            page_num = futures[future]
            try:
                if page_text := future.result():
                    results.append((page_num, page_text))
            except Exception as e:
                logger.warning(f"Error processing page {page_num}: {e}")

    return "\n".join(text for _, text in sorted(results))


def extract_with_cnocr(file_path: str, pages: list[int], num_workers: int) -> str:
    """使用CnOCR提取文本"""
    ocr = CnOcr()

    def extract_page(file_path: str, page_num: int) -> str | None:
        if img := convert_page_to_image(file_path, page_num):
            try:
                res = ocr.ocr(img)
                return "\n".join(line["text"] for line in res).strip()
            except Exception as e:
                logger.warning(f"Error processing page {page_num}: {e}")
        return None

    return extract_with_ocr(file_path, pages, num_workers, "cnocr", extract_page)


def extract_with_tesseract(file_path: str, pages: list[int], num_workers: int) -> str:
    """使用Tesseract提取文本"""

    def extract_page(file_path: str, page_num: int) -> str | None:
        img = convert_page_to_image(file_path, page_num)
        if img is None:
            return None

        try:
            text = pytesseract.image_to_string(img, lang="chi_sim")
            return text.strip()
        except Exception as e:
            logger.warning(f"Error processing page {page_num}: {e}")
            return None

    return extract_with_ocr(file_path, pages, num_workers, "tesseract", extract_page)


def extract_with_paddle(file_path: str, pages: list[int], num_workers: int) -> str:
    """使用PaddleOCR提取文本"""
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="ch",
        show_log=False,
        use_mp=True,
    )

    def extract_page(file_path: str, page_num: int) -> str | None:
        img = convert_page_to_image(file_path, page_num, "RGB")
        if img is None:
            return None

        try:
            with THREAD_LOCK:
                result = ocr.ocr(np.array(img))
            return "\n".join(line[1][0] for line in result[0]).strip()
        except Exception as e:
            logger.warning(f"Error processing page {page_num}: {e}")
            return None

    return extract_with_ocr(file_path, pages, num_workers, "paddleocr", extract_page)


def convert_page_to_image(
    file_path: str, page_num: int, convert_mode: str = "L"
) -> Image | None:
    """将PDF页面转换为图像"""
    try:
        images = convert_from_path(file_path, first_page=page_num, last_page=page_num)
        return images[0].convert(convert_mode)
    except Exception as e:
        logger.warning(f"Error converting page {page_num} to image: {e}")
        return None


def get_pdf_pages(file_path: str, first_page: int, last_page: int | None) -> list[int]:
    """获取PDF页面范围"""
    pdf_info = pdfinfo_from_path(file_path)
    total_pages: int = pdf_info["Pages"]
    last_page = min(last_page, total_pages) if last_page is not None else total_pages

    return list(range(first_page, last_page + 1))


OCR_ENGINES = {
    "cnocr": extract_with_cnocr,
    # "paddleocr": extract_with_paddle,
    "tesseract": extract_with_tesseract,
}
