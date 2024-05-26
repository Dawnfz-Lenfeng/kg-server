import difflib
import re


class TextDuplicateRemover:
    def __init__(
            self,
            char_threshold=4,
            digit_threshold=20,
            paragraph_threshold=0.95):
        self.char_threshold = char_threshold
        self.digit_threshold = digit_threshold
        self.paragraph_threshold = paragraph_threshold

    def remove_duplicates(self, text):
        """
        移除文本中的重复字符和重复句子。
        """
        # 第一步：去重字符
        text = self.remove_duplicated_chars(text)

        # 第二步：按.、。或\n分割段落，并保留分隔符
        paragraphs = re.split(r'(?<=[\.。])\n', text)

        # 第三步：在每个段落内去重句子，并去掉段内的\n
        cleaned_paragraphs = [
            self.remove_duplicated_sentences(paragraph.replace('\n', ''))
            for paragraph in paragraphs
        ]

        # 将处理后的段落拼接回一个完整的文本
        cleaned_text = '\n'.join(cleaned_paragraphs).strip()

        return cleaned_text

    def remove_duplicated_sentences(self, paragraph):
        # 使用正则表达式分割句子
        sentences = re.split(r'(?<=[。\.])\s*', paragraph)

        # 初始化集合和列表
        unique_sentences = []
        similar_sentences = set()

        for i, sentence in enumerate(sentences):
            if sentence in similar_sentences or not sentence:
                continue
            unique_sentences.append(sentence)
            for j in range(i + 1, len(sentences)):
                if sentences[j] in similar_sentences or not sentences[j]:
                    continue
                similarity = difflib.SequenceMatcher(None, sentence, sentences[j]).ratio()
                if similarity >= self.paragraph_threshold:
                    similar_sentences.add(sentences[j])

        # 将唯一句子拼接成一个段落
        cleaned_paragraph = ''.join(unique_sentences).strip()
        return cleaned_paragraph

    def remove_duplicated_chars(self, text):
        """
        查找并压缩连续出现超过指定阈值的字符。
        """
        if not text:
            return ""

        # 压缩非数字字符
        def compress_match(match):
            char = match.group(0)[0]
            length = len(match.group(0))
            if char.isdigit():
                return char if length > self.digit_threshold else match.group(0)
            return char if length >= self.char_threshold else match.group(0)

        return re.sub(r'(.)\1+', compress_match, text)


if __name__ == '__main__':
    text_duplicate_remover = TextDuplicateRemover(char_threshold=4, digit_threshold=4)
    chars1 = '333333   ffffff       rrrrrrrr'
    paragraph1 = '这是。这是。这还是。'
    text1 = 'kkkkk\nfefefefefef。热热热。热热\nfefefef'
    print(text_duplicate_remover.remove_duplicates(text1))
