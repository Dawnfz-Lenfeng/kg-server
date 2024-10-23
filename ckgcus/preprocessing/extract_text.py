import logging
from functools import partial
from multiprocessing import Manager, Pool

import pdfplumber
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_text(
    file_path: str,
    first_page: int = 1,
    last_page: int | None = None,
    engine: str = "pdfplumber",
    language: str = "chi_sim",
    max_workers: int | None = None,
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

        if text:
            return text
        else:
            raise Exception(f"Failed to extract text from {file_path}.")

    elif file_type == "txt":
        return process_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type or engine: {file_type} with {engine}")


def process_pdf_pdfplumber(file_path: str, page_numbers: list[int]) -> str:
    text = []
    total_pages = len(page_numbers)
    processed_pages = 0

    with pdfplumber.open(file_path, pages=page_numbers) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text()

            processed_pages += 1
            if page_text:
                text.append(page_text)
                print(
                    f"\rProcessing {processed_pages} / {total_pages} pages...", end=""
                )
            else:
                logger.info(f"Page {page_num + 1} has no extractable text.")
    print()  # 打印换行以结束进度条

    return "\n".join(text)


def process_pdf_ocr(
    file_path: str, page_numbers: list[int], language: str, max_workers: int
) -> str:
    total_pages = len(page_numbers)

    # 使用 Manager 创建共享变量
    manager = Manager()
    processed_pages = manager.Value("i", 0)
    text_list = manager.list()
    lock = manager.Lock()

    def callback(result):
        if result:
            text_list.append(result)
        with lock:
            processed_pages.value += 1
            print(
                f"\rProcessing {processed_pages.value} / {total_pages} pages...", end=""
            )

    try:
        with Pool(processes=max_workers) as pool:
            logger.info("Starting OCR extraction.")
            ocr_extract_partial = partial(_ocr_extract, file_path, language=language)
            for page_num in page_numbers:
                pool.apply_async(
                    ocr_extract_partial, args=(page_num,), callback=callback
                )
            pool.close()
            pool.join()
        print()  # 打印换行以结束进度条

        text = [ocr_text for ocr_text in text_list if ocr_text]

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


def _ocr_extract(file_path: str, page_num: int, language: str):
    try:
        images = convert_from_path(file_path, first_page=page_num, last_page=page_num)
        image = images[0].convert("L")  # 转换为灰度图像
    except Exception as e:
        logger.warning(f"Error converting page {page_num} to image: {e}")
        return None

    if image is not None:
        try:
            text = pytesseract.image_to_string(image, lang=language)
            return text
        except Exception as e:
            logger.warning(f"Error processing OCR on page {page_num}: {e}")
    return None
