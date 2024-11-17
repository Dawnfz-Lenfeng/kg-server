from ckgcus.preprocessing.clean_text import (
    clean_text,
    standardize_punctuation,
    remove_redundant_text,
    compress_chars,
)


def test_standardize_punctuation():
    """测试标点符号规范化"""
    cases = [
        ("测试，，，测试", "测试，测试"),
        ("测试。。。测试", "测试。测试"),
        ("测试，。测试", "测试。测试"),
        ("测试！。测试", "测试。测试"),
        ("测试。，测试", "测试。测试"),
    ]
    for input_text, expected in cases:
        assert standardize_punctuation(input_text) == expected


def test_compress_chars():
    """测试压缩重复字符"""
    cases = [
        ("试试试试试", "试"),  # 超过阈值压缩
        ("好好学习", "好好学习"),  # 未超过阈值不压缩
        ("啊啊啊", "啊"),  # 刚好达到阈值压缩
    ]
    for input_text, expected in cases:
        assert compress_chars(input_text, threshold=2) == expected


def test_remove_redundant_text():
    """测试去除重复内容"""
    # 测试相似句子
    text = "这是一个测试句子。这是一个很相似的句子。这是完全不同的句子。"
    result = remove_redundant_text(text)
    assert "这是一个测试句子。" in result
    assert "这是完全不同的句子。" in result

    # 测试完全重复的句子
    text = "这是重复的句子。这是重复的句子。这是不同的句子。"
    result = remove_redundant_text(text)
    assert result.count("这是重复的句子") == 1


def test_clean_text_handles_empty_input():
    """测试空输入处理"""
    assert clean_text("") == ""
    assert clean_text(" ") == ""
    assert clean_text("\n") == ""


def test_clean_text_removes_short_content():
    """测试删除过短内容"""
    text = "短。这是一个完整的句子。太短。"
    result = clean_text(text)
    assert "这是一个完整的句子" in result
    assert "短" not in result
    assert "太短" not in result


def test_clean_text_integration():
    """集成测试"""
    cases = [
        ("Hello世界123！！！", ""),
        ("这是一个完整的中文句子Hello123！！！", "这是一个完整的中文句子！"),
        ("试试试试试", ""),
        (
            """
        Hello世界123！！！,,,测试测试。。。
        这是重复的句子。这是重复的句子。
        这是一个完整的中文句子！！！
        """,
            "这是重复的句子。这是一个完整的中文句子。",
        ),
    ]

    for input_text, expected in cases:
        assert clean_text(input_text) == expected
