import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional

import pdfplumber
from cnocr import CnOcr
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL.Image import Image
from tqdm import tqdm

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    import numpy as np
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

THREAD_LOCK = threading.Lock()


def extract_text(
    path: str,
    start: int = 1,
    end: Optional[int] = None,
    ocr: str = "cnocr",
    workers: int = 1,
    force: bool = False,
) -> str:
    """从文件中提取文本内容"""
    ocr = ocr.lower()
    OCR_ENGINES = {
        "cnocr": extract_with_cnocr,
        "paddleocr": (extract_with_paddle, PaddleOCR, "paddleocr"),
        "tesseract": (extract_with_tesseract, pytesseract, "pytesseract"),
    }

    if ocr not in OCR_ENGINES:
        raise ValueError(f"Unsupported OCR engine: {ocr}")

    ext = path.split(".")[-1].lower()
    if ext not in {"pdf", "txt"}:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext == "txt":
        return read_txt(path)

    pages = get_pdf_pages(path, start, end)

    if not force:
        if text := extract_pdf_text(path, pages):
            return text
        logger.info("PDFplumber extraction failed, trying OCR...")

    engine = OCR_ENGINES[ocr]
    if isinstance(engine, tuple):
        extract_func, module, name = engine
        if module is None:
            raise ImportError(f"{name} not installed")
        if ocr == "tesseract":
            os.environ["OMP_THREAD_LIMIT"] = "1"
        text = extract_func(path, pages, workers)
    else:
        text = engine(path, pages, workers)

    if not text:
        logger.warning("No text content extracted")

    return text


def read_txt(path: str) -> str:
    """读取TXT文本"""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_pdf_text(path: str, pages: list[int]) -> str:
    """使用PDFplumber从PDF中提取文本"""
    logger.info("Starting PDFplumber extraction...")
    texts = []

    with pdfplumber.open(path, pages=pages) as pdf:
        for page in tqdm(pdf.pages, total=len(pages), unit="page"):
            if text := page.extract_text():
                texts.append(text)

    return "".join(texts)


def extract_with_ocr(
    path: str,
    pages: List[int],
    workers: int,
    engine: str,
    extract_page: Callable[[str, int], Optional[str]],
) -> str:
    """使用OCR提取文本的通用函数，支持多线程处理"""
    logger.info(f"Starting {engine} extraction with {workers} workers...")
    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(extract_page, path, num): num for num in pages}

        for future in tqdm(as_completed(futures), total=len(pages), unit="page"):
            page_num = futures[future]
            try:
                if page_text := future.result():
                    results.append((page_num, page_text))
            except Exception as e:
                logger.warning(f"Error processing page {page_num}: {e}")

    return "\n".join(text for _, text in sorted(results))


def extract_with_cnocr(path: str, pages: List[int], workers: int) -> str:
    """使用CnOCR提取文本"""
    ocr = CnOcr()

    def process_page(path: str, num: int) -> Optional[str]:
        if img := convert_page_to_image(path, num):
            try:
                res = ocr.ocr(img)
                return "\n".join(line["text"] for line in res).strip()
            except Exception as e:
                logger.warning(f"Error processing page {num}: {e}")
        return None

    return extract_with_ocr(path, pages, workers, "cnocr", process_page)


def extract_with_tesseract(path: str, pages: List[int], workers: int) -> str:
    """使用Tesseract提取文本"""

    def extract_page(path: str, num: int) -> Optional[str]:
        img = convert_page_to_image(path, num)
        if img is None:
            return None

        try:
            text = pytesseract.image_to_string(img, lang="chi_sim")
            return text.strip()
        except Exception as e:
            logger.warning(f"Error processing page {num}: {e}")
            return None

    return extract_with_ocr(path, pages, workers, "tesseract", extract_page)


def extract_with_paddle(path: str, pages: List[int], workers: int) -> str:
    """使用PaddleOCR提取文本"""
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="ch",
        show_log=False,
        use_mp=True,
    )

    def extract_page(path: str, num: int) -> Optional[str]:
        img = convert_page_to_image(path, num, "RGB")
        if img is None:
            return None

        try:
            with THREAD_LOCK:
                result = ocr.ocr(np.array(img))
            return "\n".join(line[1][0] for line in result[0]).strip()
        except Exception as e:
            logger.warning(f"Error processing page {num}: {e}")
            return None

    return extract_with_ocr(path, pages, workers, "paddleocr", extract_page)


def convert_page_to_image(
    path: str, num: int, convert_mode: str = "L"
) -> Optional[Image]:
    """将PDF页面转换为图像"""
    try:
        images = convert_from_path(path, first_page=num, last_page=num)
        return images[0].convert(convert_mode)
    except Exception as e:
        logger.warning(f"Error converting page {num} to image: {e}")
        return None


def get_pdf_pages(path: str, start: int, end: Optional[int]) -> List[int]:
    """获取PDF页面范围"""
    pdf_info = pdfinfo_from_path(path)
    total_pages = pdf_info["Pages"]
    end = end or total_pages

    if start < 1 or end > total_pages:
        raise ValueError("Page range is out of bounds")

    return list(range(start, end + 1))
