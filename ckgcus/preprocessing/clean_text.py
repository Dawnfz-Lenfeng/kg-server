import re


_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        # 所有的数字
        r"\d+",
        # 所有的字母
        r"[a-zA-Z]+",
        # 常见的符号，例如加减乘除、各种括号，只保留句号逗号分号顿号
        r"[+\-*\/()（）\[\]{}<>《》【】「」『』、；：、=:：_◆σΔ∂●δθ]",
    ]
]

_PUNCTUATIONS_PATTERN = re.compile(f'([{re.escape(".，。！？；：,!?;、 ")}])\\1+')


def clean_text(text):
    for pattern in _PATTERNS:
        text = pattern.sub("", text)

    return _PUNCTUATIONS_PATTERN.sub(r"\1", text)


if __name__ == "__main__":
    print(clean_text("1234324545,+-*/()[]{},,, .....asdg rwe ◆∂δrew   423njf"))
