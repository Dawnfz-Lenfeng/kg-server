import difflib
import re

# 字符集
CHINESE_CHARS = r"\u4e00-\u9fa5"
SEPARATOR_CHARS = ",;，；"
END_SENTENCE_CHARS = ".!?。！？"
PUNCTUATION_CHARS = SEPARATOR_CHARS + END_SENTENCE_CHARS

# 阈值
PARAGRAPH_LENS = 15
SETENCE_LENS = 5

# 正则表达式
punctuation_pattern = re.compile(f"，。|。，|[{SEPARATOR_CHARS}]+|[{END_SENTENCE_CHARS}]+")
separator_pattern = re.compile(f"[{SEPARATOR_CHARS}]+")
end_sentence_pattern = re.compile(f"[{END_SENTENCE_CHARS}]+")
normalize_chinese_pattern = re.compile(f"[^{CHINESE_CHARS}{PUNCTUATION_CHARS}\n]")
newline_pattern = re.compile(f"(?<=[{END_SENTENCE_CHARS}])\n")
split_sentence_pattern = re.compile(r"(?<=[。\.])\s*")
begin_with_punctuation_pattern = re.compile(f"^[{PUNCTUATION_CHARS}]+")


def clean_text(text: str) -> str:
    text = normalize_chinese_pattern.sub("", text)
    text = normalize_punctuation(text)
    text = remove_duplicated_text(text)
    text = normalize_punctuation(text)
    return text


def normalize_punctuation(text: str) -> str:
    def punctuation_replacer(match: re.Match) -> str:
        matched_text = match.group(0)

        if separator_pattern.fullmatch(matched_text):
            return "，"
        elif end_sentence_pattern.fullmatch(matched_text):
            return "。"
        elif matched_text in {"，。", "。，"}:
            return "。"

        return matched_text

    return punctuation_pattern.sub(punctuation_replacer, text)


def remove_duplicated_text(text: str, paragraph_threshold: float = 0.9) -> str:
    text = remove_duplicated_chars(text)

    paragraphs = newline_pattern.split(text)

    cleaned_paragraphs = []
    for paragraph in paragraphs:
        cleaned_paragraph = remove_duplicated_sentences(
            paragraph.replace("\n", ""), paragraph_threshold
        )
        if len(cleaned_paragraph) >= PARAGRAPH_LENS:
            cleaned_paragraphs.append(cleaned_paragraph)

    cleaned_text = "\n".join(cleaned_paragraphs).strip()
    return cleaned_text


def remove_duplicated_chars(text: str, char_threshold: int = 1) -> str:
    if not text:
        return ""

    def compress_match(match):
        char = match.group(0)[0]
        length = len(match.group(0))
        return char if length >= char_threshold else match.group(0)

    return re.sub(r"(.)\1+", compress_match, text)


def remove_duplicated_sentences(paragraph: str, paragraph_threshold: float) -> str:
    sentences = split_sentence_pattern.split(paragraph)
    unique_sentences = []
    similar_sentences = set()
    for i, sentence in enumerate(sentences):
        if len(sentence) < SETENCE_LENS or sentence in similar_sentences:
            continue
        unique_sentences.append(sentence)

        for j in range(i + 1, len(sentences)):
            if sentences[j] in similar_sentences or not sentences[j]:
                continue
            similarity = difflib.SequenceMatcher(None, sentence, sentences[j]).ratio()
            if similarity >= paragraph_threshold:
                similar_sentences.add(sentences[j])

    cleaned_paragraph = "".join(unique_sentences).strip()
    # 如果段落开头是标点符号，则去掉标点符号
    cleaned_paragraph = begin_with_punctuation_pattern.sub("", cleaned_paragraph)

    return cleaned_paragraph


if __name__ == "__main__":
    sample_text = """
1234324545,+-*/()[]{},,，,\n .....asdg ，考虑比较重复而且符合长度的句子。。，，。，。考虑比较重复而且符合长度的句子，，。.，，,.，。。，rwe ◆∂δrew   423njf
"""
    print(clean_text(sample_text))
