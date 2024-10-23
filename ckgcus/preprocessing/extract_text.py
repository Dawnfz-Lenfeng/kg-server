import logging
from functools import partial
from multiprocessing import Pool

import pdfplumber
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text(
    file_path: str,
    first_page: int = 1,
    last_page: int | None = None,
    engine: str = "pdfplumber",
    language: str = "chi_sim",
    max_workers: int = 1,
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

    if file_type == "pdf":
        if engine == "pdfplumber":
            text = process_pdf_pdfplumber(file_path, page_numbers)
            if not text:
                logger.info("PDFplumber failed to extract text, trying OCR.")
                text = process_pdf_ocr(file_path, page_numbers, language, max_workers)
        elif engine == "ocr":
            text = process_pdf_ocr(file_path, page_numbers, language, max_workers)
    elif file_type == "txt":
        text = process_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type or engine: {file_type} with {engine}")

    if not text:
        logger.warning("No text extracted from the document.")

    return text


def process_pdf_pdfplumber(file_path: str, page_numbers: list[int]) -> str:
    text = []

    with pdfplumber.open(file_path, pages=page_numbers) as pdf:
        for page_num, page in tqdm(
            enumerate(pdf.pages), total=len(page_numbers), unit="page"
        ):
            page_text = page.extract_text()

            if page_text:
                text.append(page_text)
            else:
                logger.warning(f"Page {page_num + 1} has no extractable text.")

    return "".join(text)


def process_pdf_ocr(
    file_path: str, page_numbers: list[int], language: str, max_workers: int
) -> str:
    text = []

    with Pool(processes=max_workers) as pool:
        logger.info("Starting OCR extraction.")
        ocr_extract_partial = partial(_ocr_extract, file_path, language=language)
        ocr_results = pool.imap_unordered(ocr_extract_partial, page_numbers)

        for ocr_text in tqdm(ocr_results, total=len(page_numbers), unit="page"):
            if ocr_text:
                text.append(ocr_text)

    text.sort(key=lambda x: x[0])
    text = [x[1] for x in text]
    return "".join(text)


def process_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return text


def _ocr_extract(file_path: str, page_num: int, language: str):
    try:
        images = convert_from_path(file_path, first_page=page_num, last_page=page_num)
        image = images[0].convert("L")  # 转换为灰度图像
    except Exception as e:
        logger.warning(f"Error converting page {page_num} to image: {e}")
        return None

    try:
        text = pytesseract.image_to_string(image, lang=language)
        return page_num, text.strip()
    except Exception as e:
        logger.warning(f"Error processing OCR on page {page_num}: {e}")
    return None
