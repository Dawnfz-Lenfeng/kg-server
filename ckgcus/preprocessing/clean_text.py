import re

# _PUNCTUATIONS_CHARS = re.compile(f'([{re.escape(".，。！？；：,!?;、 ")}])\\1+')

# _PATTERNS = [
#     re.compile(pattern)
#     for pattern in [
#         # 所有的数字
#         r"\d+",
#         # 所有的字母
#         r"[a-zA-Z]+",
#         # 常见的符号，例如加减乘除、各种括号，只保留句号逗号分号顿号
#         r"[+\-*\/()（）\[\]{}<>《》【】「」『』、；：、=:：_]",
#         # 特殊符号，可自行添加
#         r"[◆σΔ∂●δθ]",
#     ]
# ]

# 汉字
CHINESE_CHARS = r"\u4e00-\u9fa5"
# 标点符号
PUNCTUATION_CHARS = r",.;!?，。；！？\n"

# 合并正则
PATTERN = re.compile(f"[^{CHINESE_CHARS}{PUNCTUATION_CHARS}]")
# 标点符号去重
UNDUPLICATED_PATTERN = re.compile(f"([{PUNCTUATION_CHARS}])\\1+")


def clean_text(text):
    text = PATTERN.sub("", text)

    return UNDUPLICATED_PATTERN.sub(r"\1", text)


if __name__ == "__main__":
    print(clean_text("1234324545,+-*/()[]{},,, .....asdg rwe ◆∂δrew   423njf"))
