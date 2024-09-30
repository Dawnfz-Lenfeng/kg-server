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
_CHINESE_CHARS = r"\u4e00-\u9fa5"
# 标点符号
_PUNCTUATION_CHARS = r",.;!?，。；！？\n"

# 合并正则
_PATTERN = re.compile(f"[^{_CHINESE_CHARS}{_PUNCTUATION_CHARS}]")
# 标点符号去重
_UNDUPLICATED_PATTERN = re.compile(f"([{_PUNCTUATION_CHARS}])\\1+")


def clean_text(text):
    text = _PATTERN.sub("", text)

    return _UNDUPLICATED_PATTERN.sub(r"\1", text)


if __name__ == "__main__":
    print(clean_text("1234324545,+-*/()[]{},,, .....asdg rwe ◆∂δrew   423njf"))
