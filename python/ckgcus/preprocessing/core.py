from .clean_text import clean_text
from .extract_text import extract_text
from .remove_duplicated_text import remove_duplicated_text


class TextPreprocessor:
    def __init__(self, text: str):
        self._original_text = text  # 初始文本
        self._text = text

    @classmethod
    def read_file(
        cls,
        file_path: str,
        pages: list | None = None,
        engine="pdfplumber",
        language: str = "eng+chi_sim",
    ):
        return cls(extract_text(file_path, pages, engine, language))

    def save_to_file(self, output_path: str, original=False):
        """
        处理文本, 并保存到指定的文件.
        NOTE: 该函数很可能会被重构, 因为可能之后的处理文件不一定会以实际的txt结构储存(比如跟数据库对接)

        :param output_path: 输出文件的路径.
        :param original: 是否输出原始文本
        """
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(self._text if not original else self._original_text)

    def clean(self, char_threshold=4, digit_threshold=20, paragraph_threshold=0.95):
        """
        Clean text using specified methods.
        :param clean_methods: List of cleaning methods to apply.
        """
        self._text = clean_text(self._text)
        self._text = remove_duplicated_text(
            self._text, char_threshold, digit_threshold, paragraph_threshold
        )

    @property
    def text(self):
        return self._text

    @property
    def original_text(self):
        return self._original_text
