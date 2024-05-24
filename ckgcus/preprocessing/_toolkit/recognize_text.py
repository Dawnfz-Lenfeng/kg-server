"""
Description:

- 本文件包含TextRecognizer类, 该类是为了支持不同文件类型的预处理而设计.
- 初始支持将PDF文件转换为文本, 预留了扩展接口以支持图像和纯文本的处理.
- 主要用途是为后续的数据分析和知识图谱构建提供预处理过的数据.

Dependencies:
以下是目前使用的库, 后期为了更好的处理效果, 可能会考虑调用更好的api.

- pdfplumber: 用于PDF文件处理.
- pytesseract: 使用Tesseract OCR引擎进行光学字符识别, 可从扫描的图像或PDF文件中提取文本.
- Tesseract: OCR引擎. 安装可参考 https://blog.csdn.net/qq_38463737/article/details/109679007.
- pdf2image: 将PDF文件页转换为图像, 便于OCR识别或进一步的图像处理.
"""
import pdfplumber
import pytesseract
from pdf2image import convert_from_path


class TextRecognizer:
    def __init__(self, file_path: str):
        """
        :param file_path: 需要处理的文件路径.
        """
        self.file_path = file_path

    def extract_text(
            self,
            pages: list | None = None,
            engine: str = 'pdfplumber',
            language: str = 'eng+chi_sim') -> str:
        """
        :param pages: 一个表示页码的列表, 或使用range对象表示的范围.页码从1开始计数.
        :param engine: 用于处理文件的引擎. 对于PDF文件, 可以选择 'pdfplumber' (默认)来直接提取文本,
                       或者选择 'ocr' 来通过光学字符识别技术处理扫描或图像基的PDF文件.
        :param language: 用于OCR识别的语言代码. 默认为 'eng+chi_sim' (中+英).
        :return: 提取到的文本内容, 作为一个字符串返回.
        """
        engine = engine.lower()
        file_type = self.file_path.split('.')[-1].lower()

        if file_type == 'pdf':
            if engine == 'pdfplumber':
                return self._process_pdf_pdfplumber(pages)
            elif engine == 'ocr':
                return self._process_pdf_ocr(pages, language)
        elif file_type == 'txt':
            return self._process_txt()
        # 其他文件类型处理留作未来实现
        else:
            raise ValueError(f"Unsupported file type or engine: {file_type} with {engine}")

    def _process_pdf_pdfplumber(self, pages: list = None) -> str:
        text = []

        try:
            with pdfplumber.open(self.file_path) as pdf:
                if pages is None:
                    # 如果没有提供 pages 参数, 则提取所有页面
                    pages_to_extract = range(1, len(pdf.pages) + 1)
                else:
                    pages_to_extract = pages

                # 提取指定页面的文本
                for page_num in pages_to_extract:
                    try:
                        page = pdf.pages[page_num - 1]  # 页码转换为索引
                        page_text = page.extract_text()
                        if page_text:
                            text.append(page_text)
                    except IndexError:
                        print(f"Page {page_num} is out of range.")
                        continue

        except Exception as e:
            print(f"Error processing PDF file with pdfplumber: {e}")

        return "\n".join(text)

    def _process_pdf_ocr(self, pages: list = None, language: str = 'eng+chi_sim') -> str:
        text = []

        try:
            # 将 PDF 文件页转换成图像
            images = convert_from_path(self.file_path)

            if pages is None:
                # 如果没有提供 pages 参数，则提取所有页面
                pages_to_extract = range(1, len(images) + 1)
            else:
                pages_to_extract = pages

            # 提取指定页面的文本
            for page_num in pages_to_extract:
                try:
                    image = images[page_num - 1]  # 页码转换为索引
                    page_text = pytesseract.image_to_string(image, lang=language)
                    if page_text:
                        text.append(page_text)
                except IndexError:
                    print(f"Page {page_num} is out of range.")
                    continue

        except Exception as e:
            print(f"Error processing PDF file with OCR: {e}")

        return "\n".join(text)

    def _process_txt(self) -> str:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return text
        except Exception as e:
            print(f"Error processing TXT file: {e}")
            return ""
