import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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


def clean_text(text: str):
    text = non_target_pattern.sub("", text)
    text = separator_pattern.sub("，", text)
    text = end_sentence_pattern.sub("。", text)
    text = punctuation_fix_pattern.sub("。", text)
    return text


if __name__ == "__main__":
    sample_text = "1234324545,+-*/()[]{},,，,\n .....asdg rwe ◆∂δrew   423njf"
    print(clean_text(sample_text, max_workers=1))
