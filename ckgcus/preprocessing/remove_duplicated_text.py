import difflib
import re
from .clean_text import _PUNCTUATION_CHARS


# 句末符号
_END_CHARS = re.compile(r"(?<=[\.。!！?？])\n")
_PARAGRAPH_LENS = 15
_BEGIN_WITH_PUNCTUATION_CHARS = re.compile(f"^[{_PUNCTUATION_CHARS}]+")


def remove_duplicated_text(
    text: str,
    char_threshold: int = 4,
    digit_threshold: int = 20,
    paragraph_threshold: float = 0.95,
) -> str:
    """
    移除文本中的重复字符和重复句子。

    :param text: 需要处理的文本.
    :param char_threshold: 连续字符的阈值，超过这个阈值将被压缩.
    :param digit_threshold: 连续数字的阈值，超过这个阈值将被压缩.
    :param paragraph_threshold: 句子相似度的阈值，超过这个阈值将被认为是重复句子.
    :return: 处理后的文本.
    """
    # 第一步：去重字符
    text = _remove_duplicated_chars(text, char_threshold, digit_threshold)

    # 第二步：按.、。或\n分割段落，并保留分隔符
    paragraphs = _END_CHARS.split(text)

    # 第三步：在每个段落内去重句子，并去掉段内的\n
    cleaned_paragraphs = []

    for paragraph in paragraphs:
        cleaned_paragraph = _remove_duplicated_sentences(
            paragraph.replace("\n", ""), paragraph_threshold
        )

        # 如果段落开头是标点符号，则去掉标点符号
        cleaned_paragraph = _BEGIN_WITH_PUNCTUATION_CHARS.sub("", cleaned_paragraph)

        if len(cleaned_paragraph) >= _PARAGRAPH_LENS:
            cleaned_paragraphs.append(cleaned_paragraph)

    # 将处理后的段落拼接回一个完整的文本
    cleaned_text = "\n".join(cleaned_paragraphs).strip()

    return cleaned_text


def _remove_duplicated_sentences(paragraph: str, paragraph_threshold: float) -> str:
    # 使用正则表达式分割句子
    sentences = re.split(r"(?<=[。\.])\s*", paragraph)

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
            if similarity >= paragraph_threshold:
                similar_sentences.add(sentences[j])

    # 将唯一句子拼接成一个段落
    cleaned_paragraph = "".join(unique_sentences).strip()

    return cleaned_paragraph


def _remove_duplicated_chars(
    text: str, char_threshold: int, digit_threshold: int
) -> str:
    """
    查找并压缩连续出现超过指定阈值的字符。

    :param text: 需要处理的文本.
    :param char_threshold: 连续字符的阈值，超过这个阈值将被压缩.
    :param digit_threshold: 连续数字的阈值，超过这个阈值将被压缩.
    :return: 处理后的文本.
    """
    if not text:
        return ""

    # 压缩非数字字符
    def compress_match(match):
        char = match.group(0)[0]
        length = len(match.group(0))
        if char.isdigit():
            return char if length > digit_threshold else match.group(0)
        return char if length >= char_threshold else match.group(0)

    return re.sub(r"(.)\1+", compress_match, text)


if __name__ == "__main__":
    chars1 = "333333   ffffff       rrrrrrrr"
    paragraph1 = "这是。这是。这还是。"
    text1 = ",,,，kkkkk\nf1112342342344231111           \n?\n  \n热热热。热热\nfefefef"
    print(remove_duplicated_text(text1, char_threshold=4, digit_threshold=4))
