import logging

from .clean_text import clean_text
from .extract_text import extract_text
from .remove_duplicated_text import remove_duplicated_text

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TextPreprocessor:
    def __init__(self, text: str, max_workers: int):
        self.original_text = text  # 初始文本
        self.text = text
        self.max_workers = max_workers

    @classmethod
    def read_file(
        cls,
        file_path: str,
        first_page: int = 1,
        last_page: int | None = None,
        engine: str = "pdfplumber",
        language: str = "chi_sim",
        max_workers: int | None = None,
    ):
        """
        提取文本内容

        :param file_path: 需要处理的文件路径.
        :param first_page: 需要处理的起始页码, 默认为1.
        :param last_page: 需要处理的结束页码, 默认为None, 表示处理到最后一页.
        :param engine: 用于处理文件的引擎. 对于PDF文件, 可以选择 'pdfplumber' (默认)来直接提取文本,
                    或者选择 'ocr' 来通过光学字符识别技术处理扫描或图像基的PDF文件.
        :param language: 用于OCR识别的语言代码. 默认为 'chi_sim' (中).
        :param max_workers: 用于并行处理的进程数. 默认为None, 使用所有的可用进程.
        """
        if max_workers is None:
            max_workers = 1
        logger.info(f"Using {max_workers} workers for text extraction.")

        return cls(
            extract_text(
                file_path,
                first_page,
                last_page,
                engine,
                language,
                max_workers,
            ),
            max_workers=max_workers,
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
        """
        清理文本内容
        """
        self.text = clean_text(self.text, self.max_workers)
        self.text = remove_duplicated_text(self.text)
