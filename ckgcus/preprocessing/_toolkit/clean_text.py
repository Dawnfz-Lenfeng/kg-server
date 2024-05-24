import re


class TextCleaner:
    _qq_patterns = [
        re.compile(pattern)
        for pattern in [
            r'\b\d{5,12}\b',
            r'\([^()]*\d{5,12}[^()]*\)',
            r'QQ:|我的QQ是|QQ号码|qq:|qq号码|QQ号:?\s*\d{5,12}'
        ]
    ]
    # 匹配 "vx"、"微信" 或 "weixin" 及其后面的微信号，考虑中文冒号、英文冒号、逗号或句号作为分隔符
    _wechat_patterns = [
        re.compile(pattern)
        for pattern in [
            r'(vx|微信|weixin|微信号|weixin号|vx号)[：,。；;，]?([a-zA-Z0-9][a-zA-Z0-9_-]{4,19})',
            r'\xa0|\u00A0|●',
            r'关注微信.*?商业用途',
            r'关注微信公众号',
        ]
    ]
    _url_patterns = [
        re.compile(pattern)
        for pattern in [
            r"https?://[\w./-]+",
        ]
    ]
    # 匹配可能包含手机号的更复杂情况，如“手机号：”、“电话：”、“手机号码：”等前缀
    # 这里使用非贪婪匹配来确保不会匹配到过长的字符串
    _phone_patterns = [
        re.compile(pattern)
        for pattern in [
            r'1\d{9,10}\b',
            r'\(?:1[3-9]\d{9,10}\)?',
            r'手机号\s*:\s*1[3-9]\d{9,10}',
            r'电话\s*:\s*1[3-9]\d{9,10}',
            r'手机号码\s*:\s*1[3-9]\d{9,10}',
            r'phone\s*:\s*1[3-9]\d{9,10}',
            r'mobile\s*:\s*1[3-9]\d{9,10}',
            r'tel\s*:\s*1[3-9]\d{9,10}',
            r'phone number\s*:\s*1[3-9]\d{9,10}',
            r'联系电话\s*:\s*1[3-9]\d{9,10}',
            r'\+86 \d{11}',
            r'\+86\d{9}',
            # 添加其他可能的前缀模式...
        ]
    ]
    _email_pattern = re.compile(r"[A-Za-z0-9.\-+_]+@[a-z0-9.\-+_]+\.[a-z]+")
    _expression_patterns = [
        re.compile(pattern)
        for pattern in [
            u'['u'\U0001F300-\U0001F64F' u'\U0001F680-\U0001F6FF'u'\u2600-\u2B55]+',
            u'('u'\ud83c[\udf00-\udfff]|'u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'u'[\u2600-\u2B55])+',

        ]
    ]
    _punctuations_pattern = re.compile(f'([{re.escape(".，。！？；：,!?;、 ")}])\\1+')

    _clean_methods = ['email', 'wechat', 'qq', 'url', 'phone', 'expression']

    @staticmethod
    def clean(text, clean_methods=None):
        if clean_methods is None:
            clean_methods = TextCleaner._clean_methods

        for method_name in clean_methods:
            method = getattr(TextCleaner, method_name + '_clean')
            text = method(text)

        return text

    @staticmethod
    def email_clean(text):
        return TextCleaner._email_pattern.sub("", text)

    @staticmethod
    def wechat_clean(text):
        for pattern in TextCleaner._wechat_patterns:
            text = pattern.sub('', text)
        return text

    @staticmethod
    def qq_clean(text):
        for pattern in TextCleaner._qq_patterns:
            text = pattern.sub('', text)
        return text

    @staticmethod
    def url_clean(text):
        for pattern in TextCleaner._url_patterns:
            text = pattern.sub('', text)
        return text

    @staticmethod
    def phone_clean(text):
        for pattern in TextCleaner._phone_patterns:
            text = pattern.sub('', text)
        return text

    @staticmethod
    def expression_clean(text):
        for pattern in TextCleaner._expression_patterns:
            text = pattern.sub('', text)
        return TextCleaner._punctuations_pattern.sub(r'\1', text)


if __name__ == '__main__':
    print(TextCleaner.clean('13997594353,,,, .....   423njf'))
