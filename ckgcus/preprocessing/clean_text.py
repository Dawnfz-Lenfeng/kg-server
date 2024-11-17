import difflib
import re

# 字符集
HANZI = r"\u4e00-\u9fa5"
COMMAS = ",;，；"
STOPS = ".!?。！？"
PUNCTS = COMMAS + STOPS

# 长度阈值
MIN_PARA = 15
MIN_SENT = 5

# 正则
RE_PUNCT = re.compile(f"，。|。，|[{COMMAS}]+|[{STOPS}]+")
RE_COMMA = re.compile(f"[{COMMAS}]+")
RE_STOP = re.compile(f"[{STOPS}]+")
RE_CLEAN = re.compile(f"[^{HANZI}{PUNCTS}\n]")
RE_PARA = re.compile(f"(?<=[{STOPS}])\n")
RE_SENT = re.compile(r"(?<=[。\.])\s*")
RE_HEAD = re.compile(f"^[{PUNCTS}]+")


def clean_text(text: str) -> str:
    """规范化文本：移除非中文字符，统一标点符号，去除重复内容"""
    text = RE_CLEAN.sub("", text)
    text = standardize_punctuation(text)
    text = remove_redundant_text(text)
    text = standardize_punctuation(text)
    return text


def standardize_punctuation(text: str) -> str:
    """统一标点符号格式"""

    def punctuation_replacer(match: re.Match) -> str:
        matched_text = match.group(0)
        if RE_COMMA.fullmatch(matched_text):
            return "，"
        elif RE_STOP.fullmatch(matched_text):
            return "。"
        elif matched_text in {"，。", "。，"}:
            return "。"
        return matched_text

    return RE_PUNCT.sub(punctuation_replacer, text)


def remove_redundant_text(text: str, similarity_threshold: float = 0.9) -> str:
    """移除文本中的重复内容"""
    text = compress_chars(text)
    paragraphs = RE_PARA.split(text)

    cleaned_paragraphs = []
    for paragraph in paragraphs:
        cleaned_paragraph = deduplicate_sentences(
            paragraph.replace("\n", ""), similarity_threshold
        )
        if len(cleaned_paragraph) >= MIN_PARA:
            cleaned_paragraphs.append(cleaned_paragraph)

    return "\n".join(cleaned_paragraphs).strip()


def compress_chars(text: str, repeat_threshold: int = 1) -> str:
    """压缩连续重复的字符"""
    if not text:
        return ""

    def compress_match(match):
        char = match.group(0)[0]
        length = len(match.group(0))
        return char if length >= repeat_threshold else match.group(0)

    return re.sub(r"(.)\1+", compress_match, text)


def deduplicate_sentences(paragraph: str, similarity_threshold: float) -> str:
    """去除段落中的相似句子"""
    sentences = RE_SENT.split(paragraph)
    unique_sentences = []
    similar_sentences = set()

    for i, sentence in enumerate(sentences):
        if len(sentence) < MIN_SENT or sentence in similar_sentences:
            continue
        unique_sentences.append(sentence)

        for j in range(i + 1, len(sentences)):
            if sentences[j] in similar_sentences or not sentences[j]:
                continue
            similarity = difflib.SequenceMatcher(None, sentence, sentences[j]).ratio()
            if similarity >= similarity_threshold:
                similar_sentences.add(sentences[j])

    cleaned_paragraph = "".join(unique_sentences).strip()
    return RE_HEAD.sub("", cleaned_paragraph)


if __name__ == "__main__":
    sample_text = """
1234324545,+-*/()[]{},,，,\n .....asdg ，考虑比较重复而且符合长度的句子。。，，。，。考虑比较重复而且符合长度的句子，，。.，，,.，。。，rwe ◆∂δrew   423njf
"""
    print(clean_text(sample_text))
