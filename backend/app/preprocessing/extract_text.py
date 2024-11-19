import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import pdfplumber
from cnocr import CnOcr  # type: ignore
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL.Image import Image
from tqdm import tqdm

try:
    import pytesseract  # type: ignore
except ImportError:
    pytesseract = None

try:
    import numpy as np
    from paddleocr import PaddleOCR  # type: ignore
except ImportError:
    PaddleOCR = None

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

THREAD_LOCK = threading.Lock()


def extract_text(
    path: str,
    first_page: int = 1,
    last_page: int | None = None,
    ocr_engine: str = "cnocr",
    num_workers: int = 4,
    force_ocr: bool = False,
) -> str:
    """提取文本内容. 如果文件是 pdf, 会优先使用 pdfolumber 提取文本, 否则使用 OCR 提取文本.

    :param path: 需要处理的文件路径
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

    ext = path.split(".")[-1].lower()
    if ext not in {"pdf", "txt"}:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext == "txt":
        return read_txt(path)

    pages = get_pdf_pages(path, first_page, last_page)

    if not force_ocr:
        if text := extract_pdf_text(path, pages):
            return text
        logger.info("PDFplumber extraction failed, trying OCR...")

    engine = OCR_ENGINES[ocr_engine]
    if isinstance(engine, tuple):
        extract_func, module, name = engine
        if module is None:
            raise ImportError(f"{name} not installed")
        if ocr_engine == "tesseract":
            os.environ["OMP_THREAD_LIMIT"] = "1"
        text = extract_func(path, pages, num_workers)
    else:
        text = engine(path, pages, num_workers)

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
    pages: list[int],
    workers: int,
    engine: str,
    extract_page: Callable[[str, int], str | None],
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


def extract_with_cnocr(path: str, pages: list[int], workers: int) -> str:
    """使用CnOCR提取文本"""
    ocr = CnOcr()

    def process_page(path: str, num: int) -> str | None:
        if img := convert_page_to_image(path, num):
            try:
                res = ocr.ocr(img)
                return "\n".join(line["text"] for line in res).strip()
            except Exception as e:
                logger.warning(f"Error processing page {num}: {e}")
        return None

    return extract_with_ocr(path, pages, workers, "cnocr", process_page)


def extract_with_tesseract(path: str, pages: list[int], workers: int) -> str:
    """使用Tesseract提取文本"""

    def extract_page(path: str, num: int) -> str | None:
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


def extract_with_paddle(path: str, pages: list[int], workers: int) -> str:
    """使用PaddleOCR提取文本"""
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="ch",
        show_log=False,
        use_mp=True,
    )

    def extract_page(path: str, num: int) -> str | None:
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


def convert_page_to_image(path: str, num: int, convert_mode: str = "L") -> Image | None:
    """将PDF页面转换为图像"""
    try:
        images = convert_from_path(path, first_page=num, last_page=num)
        return images[0].convert(convert_mode)
    except Exception as e:
        logger.warning(f"Error converting page {num} to image: {e}")
        return None


def get_pdf_pages(path: str, start: int, end: int | None) -> list[int]:
    """获取PDF页面范围"""
    pdf_info = pdfinfo_from_path(path)
    total_pages = pdf_info["Pages"]
    end = end or total_pages

    if start < 1 or end > total_pages:
        raise ValueError("Page range is out of bounds")

    return list(range(start, end + 1))


OCRConfig = Callable[..., str] | tuple[Callable[..., str], object, str]

OCR_ENGINES: dict[str, OCRConfig] = {
    "cnocr": extract_with_cnocr,
    "paddleocr": (extract_with_paddle, PaddleOCR, "paddleocr"),
    "tesseract": (extract_with_tesseract, pytesseract, "pytesseract"),
}
