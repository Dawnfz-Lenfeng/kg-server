import re

# 字符集
CHINESE_CHARS = r"\u4e00-\u9fa5"
SEPARATOR_CHARS = ",;，；"
END_SENTENCE_CHARS = ".!?。！？"
PUNCTUATION_CHARS = SEPARATOR_CHARS + END_SENTENCE_CHARS

# 正则表达式
separator_pattern = re.compile(f"[{SEPARATOR_CHARS}]+")  # 压缩连续的分隔符
end_sentence_pattern = re.compile(f"[{END_SENTENCE_CHARS}]+")  # 压缩连续的句末符
punctuation_fix_pattern = re.compile(r"，。|。，")
non_target_pattern = re.compile(
    f"[^{CHINESE_CHARS}{PUNCTUATION_CHARS}\n]"
)  # 删除非目标字符


def clean_text(text: str, max_workers: int):
    if len(text) < 1000:
        return clean_text_synchronously(text)
    else:
        return clean_text_in_parallel(text, max_workers)


def clean_text_synchronously(text: str):
    text = non_target_pattern.sub("", text)
    text = separator_pattern.sub("，", text)
    text = end_sentence_pattern.sub("。", text)
    text = punctuation_fix_pattern.sub("。", text)
    return text


def clean_text_in_parallel(text: str, max_workers: int):
    from multiprocessing import Pool

    parts = split_text(text, max_workers)
    with Pool(max_workers) as pool:
        results = pool.map(clean_text_synchronously, parts)
    return "".join(results)


def split_text(text, parts):
    part_length = len(text) // parts
    return [text[i : i + part_length] for i in range(0, len(text), part_length)]


if __name__ == "__main__":
    sample_text = "1234324545,+-*/()[]{},,，,\n .....asdg rwe ◆∂δrew   423njf"
    print(clean_text(sample_text, max_workers=1))
