import logging

from .clean_text import clean_text
from .extract_text import extract_text

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TextPreprocessor:
    def __init__(self, text: str):
        self.original_text = text  # 初始文本
        self.text = text

    @classmethod
    def read_file(
        cls,
        file_path: str,
        first_page: int = 1,
        last_page: int | None = None,
        ocr_engine: str = "cnocr",
        max_workers: int = 1,
        force_ocr: bool = False,
    ):
        """
        提取文本内容. 如果文件是 pdf, 会优先使用 pdfolumber 提取文本, 否则使用 OCR 提取文本.

        :param file_path: 需要处理的文件路径.
        :param first_page: 需要处理的起始页码, 默认为1.
        :param last_page: 需要处理的结束页码, 默认为None, 表示处理到最后一页.
        :param ocr_engine: OCR引擎, 默认为 'cnocr', 可选 'tesseract', 'paddleocr'.
        `cnocr` 精度和速度都适中; `paddleocr` 精度最高但是最慢; `tesseract` 精度最低但是最快.
        :param max_workers: 用于并行处理的进程数. 默认为1, 表示不使用并行处理.
        :param force_ocr: 是否强制使用 OCR 引擎, 默认为 False.
        """
        return cls(
            extract_text(
                file_path,
                first_page,
                last_page,
                ocr_engine,
                max_workers,
                force_ocr,
            )
        )

    def save_to_file(self, output_path: str, original=False):
        """
        处理文本, 并保存到指定的文件.
        NOTE: 该函数很可能会被重构, 因为可能之后的处理文件不一定会以实际的txt结构储存(比如跟数据库对接)

        :param output_path: 输出文件的路径.
        :param original: 是否输出原始文本
        """
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(self.text if not original else self.original_text)

    def clean(self):
        """清理文本内容"""
        logger.info("Cleaning text...")
        self.text = clean_text(self.text)
