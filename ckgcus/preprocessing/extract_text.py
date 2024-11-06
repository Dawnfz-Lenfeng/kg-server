import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import pdfplumber
from cnocr import CnOcr
from tqdm import tqdm

from .utils import convert_page_to_image, get_pdf_pages

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

lock = threading.Lock()


def extract_text(
    file_path: str,
    first_page: int = 1,
    last_page: int | None = None,
    ocr_engine: str = "cnocr",
    max_workers: int = 1,
    force_ocr: bool = False,
) -> str:
    ocr_engine = ocr_engine.lower()
    file_type = file_path.split(".")[-1].lower()

    if file_type == "pdf":
        page_numbers = get_pdf_pages(file_path, first_page, last_page)

        if not force_ocr:
            text = process_pdf_pdfplumber(file_path, page_numbers)
            if text:
                return text
            logger.info("PDFplumber failed to extract text, trying OCR.")

        if ocr_engine == "cnocr":
            text = process_pdf_cnocr(file_path, page_numbers, max_workers)

        elif ocr_engine == "paddleocr":
            if PaddleOCR is None:
                raise ImportError("paddleocr is not installed.")
            text = process_pdf_paddleocr(file_path, page_numbers, max_workers)

        elif ocr_engine == "tesseract":
            if pytesseract is None:
                raise ImportError("pytesseract is not installed.")
            # 每个 tesseract 默认使用omp多线程, 避免线程过多
            os.environ["OMP_THREAD_LIMIT"] = "1"
            text = process_pdf_tesseract(file_path, page_numbers, max_workers)
        else:
            raise ValueError(f"Unsupported OCR engine: {ocr_engine}")
    elif file_type == "txt":
        text = process_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    if not text:
        logger.warning("No text extracted from the document.")

    return text


def process_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def process_pdf_pdfplumber(file_path: str, page_numbers: list[int]) -> str:
    text = []

    logger.info("Starting PDFplumber extraction.")
    with pdfplumber.open(file_path, pages=page_numbers) as pdf:
        for page in tqdm(pdf.pages, total=len(page_numbers), unit="page"):
            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

    return "".join(text)


def process_pdf_ocr(
    file_path: str,
    page_numbers: list[int],
    max_workers: int,
    ocr_engine: str,
    extract_text: Callable[[str, int], str],
) -> str:
    text = []
    logger.info(f"Starting {ocr_engine} extraction with {max_workers} workers.")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(extract_text, file_path, page_num): page_num
            for page_num in page_numbers
        }

        for future in tqdm(as_completed(futures), total=len(page_numbers), unit="page"):
            page_num = futures[future]
            try:
                page_text = future.result()
                if page_text:
                    text.append((page_num, page_text))
            except Exception as e:
                logger.warning(f"Error processing page {page_num}: {e}")

    text.sort(key=lambda x: x[0])
    return "\n".join(x[1] for x in text if x[1])


def process_pdf_cnocr(file_path: str, page_numbers: list[int], max_workers: int) -> str:
    ocr = CnOcr()

    def extract_text(file_path, page_num):
        image = convert_page_to_image(file_path, page_num)
        if image is None:
            return None

        try:
            res = ocr.ocr(image)
            return "\n".join(line["text"] for line in res).strip()
        except Exception as e:
            logger.warning(f"Error processing OCR on page {page_num}: {e}")
            return None

    return process_pdf_ocr(
        file_path,
        page_numbers,
        max_workers,
        "cnocr",
        extract_text,
    )


def process_pdf_tesseract(
    file_path: str, page_numbers: list[int], max_workers: int
) -> str:
    def extract_text(file_path, page_num):
        image = convert_page_to_image(file_path, page_num)
        if image is None:
            return None

        try:
            text = pytesseract.image_to_string(image, lang="chi_sim")
            return text.strip()
        except Exception as e:
            logger.warning(f"Error processing OCR on page {page_num}: {e}")
        return None

    return process_pdf_ocr(
        file_path,
        page_numbers,
        max_workers,
        "tesseract",
        extract_text,
    )


def process_pdf_paddleocr(
    file_path: str, page_numbers: list[int], max_workers: int
) -> str:
    ocr = PaddleOCR(
        use_angle_cls=True,
        lang="ch",
        show_log=False,
        use_mp=True,
    )

    def extract_text(file_path, page_num):
        image = convert_page_to_image(file_path, page_num, "RGB")
        if image is None:
            return None
        image = np.array(image)

        try:
            with lock:
                result = ocr.ocr(image)
            return "\n".join(line[1][0] for line in result[0]).strip()
        except Exception as e:
            logger.warning(f"Error processing OCR on page {page_num}: {e}")

    return process_pdf_ocr(
        file_path,
        page_numbers,
        max_workers,
        "paddleocr",
        extract_text,
    )
