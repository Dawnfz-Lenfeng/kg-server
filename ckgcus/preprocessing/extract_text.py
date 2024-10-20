from functools import partial
from multiprocessing import Pool, cpu_count

import pdfplumber
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path


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

    if max_workers is None:
        max_workers = max(cpu_count() - 1, 1)  # 保留一个 CPU 给主进程

    if file_type == "pdf":
        if engine == "pdfplumber":
            return process_pdf_pdfplumber(file_path, first_page, last_page)
        elif engine == "ocr":
            return process_pdf_ocr(
                file_path, first_page, last_page, language, max_workers
            )
    elif file_type == "txt":
        return process_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type or engine: {file_type} with {engine}")


def process_pdf_pdfplumber(
    file_path: str, first_page: int, last_page: int | None
) -> str:
    text = []

    try:
        with pdfplumber.open(file_path, pages=[first_page, last_page]) as pdf:
            for page in pdf.pages:
                text.append(page.extract_text())
    except Exception as e:
        print(f"Error processing PDF: {e}")

    except Exception as e:
        raise Exception(f"Error processing PDF file with pdfplumber: {e}")

    return "\n".join(text)


def process_pdf_ocr(
    file_path: str,
    first_page: int,
    last_page: int | None,
    language: str,
    max_workers: int,
) -> str:
    try:
        # 获取 PDF 的总页数
        pdf_info = pdfinfo_from_path(file_path, userpw=None, poppler_path=None)
        total_pages = pdf_info["Pages"]
        last_page = last_page or total_pages

        if first_page < 1 or last_page > total_pages:
            raise ValueError("Page range is out of bounds.")

        page_numbers = list(range(first_page, last_page + 1))

        # 创建一个进程池
        with Pool(processes=max_workers) as pool:
            # 步骤 1：并行将每一页转换为图像
            convert_page_partial = partial(_convert_page_to_image, file_path)
            images = pool.map(convert_page_partial, page_numbers)

            # 步骤 2：并行对图像进行 OCR 处理
            ocr_image_partial = partial(_ocr_image, language)
            ocr_results = pool.map(ocr_image_partial, images)

        # 按页码排序结果
        text = [result for result in ocr_results if result is not None]

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
        print(f"Error converting page {page_num}: {e}")
        return None


def _ocr_image(language, image):
    if image is None:
        return None
    try:
        return pytesseract.image_to_string(image, lang=language)
    except Exception as e:
        print(f"Error processing OCR: {e}")
        return None
