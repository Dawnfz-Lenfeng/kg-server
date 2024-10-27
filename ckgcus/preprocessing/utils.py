import logging

from pdf2image import convert_from_path, pdfinfo_from_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def convert_page_to_image(file_path: str, page_num: int, convert_mode: str = "L"):
    try:
        images = convert_from_path(file_path, first_page=page_num, last_page=page_num)
        return images[0].convert(convert_mode)
    except Exception as e:
        logger.warning(f"Error converting page {page_num} to image: {e}")
        return None


def get_pdf_pages(file_path: str, first_page: int, last_page: int | None):
    pdf_info = pdfinfo_from_path(file_path, userpw=None, poppler_path=None)
    total_pages = pdf_info["Pages"]
    last_page = last_page or total_pages

    if first_page < 1 or last_page > total_pages:
        raise ValueError("Page range is out of bounds.")

    return list(range(first_page, last_page + 1))
