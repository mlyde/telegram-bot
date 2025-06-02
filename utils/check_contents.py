"""
检查是否包含屏蔽词
"""

import logging
logger = logging.getLogger(__name__)

import re

from core.block_words import block_worlds_json, pattern_bio, pattern_button, pattern_chatname, pattern_group_message, pattern_user_id, pattern_username
from core.block_emoji import block_emoji_dict

pattern_list: list = [pattern_bio, pattern_button, pattern_chatname, pattern_group_message, pattern_user_id, pattern_username]

def checkBlockList():
    """ 简单检查屏蔽词列表是否有效或范围过大, 正则很难进行完全测试, 就这样了吧 """

    if check_all("1Ab谢谢学习资源"):
        logger.error("屏蔽词匹配到正常文本, 请检查屏蔽词列表")
        raise Exception
    elif check_all("SM俱乐部"):
        logger.debug("屏蔽词匹配正常")


def findBlockListSource(text: str):
    """ 在原始屏蔽词列表中查找哪条规则匹配成功, 可用于排查错误 """

    tmp_list: list[list[str]] = [dic for dic in block_worlds_json.get("blocked_words")]

    for li in tmp_list:
        for i in li:
            if re.findall(i, text):
                yield i


def containBlockedWords(text: str, pattern: re.Pattern) -> bool:
    """ 判断文本中是否包含屏蔽词, 含有则返回 True """

    if text:
        # 去除部分 除空格外 的空字符和 '.'
        text = re.sub(r"[.\t\n\r\f\v()]", '', text) 
        if text:
            match = pattern.search(text)
            return bool(match)
    return False

def containBlockedEmojiId(emoji_id: str, blocked_emoji_dict: dict[str, list[str]]) -> bool:
    """ 是否在屏蔽会员表情中 """
    return any(emoji_id in li  for li in blocked_emoji_dict.values())

def containBlockedEmojiHtml(message_html: str, blocked_emoji_dict: dict[str, list[str]]) -> bool:
    """ 判断是否包含屏蔽会员表情, 含有则返回 True """

    emoji_ids = re.findall("<tg-emoji emoji-id=\"([0-9]{19})\">(?:.*?)</tg-emoji>", message_html)
    if emoji_ids:
        return any(any(emoji_id in li  for li in blocked_emoji_dict.values())  for emoji_id in emoji_ids)
    return False

def check_all(content):

    txt = str(content)
    if any(containBlockedWords(txt, pattern) for pattern in pattern_list):
        return True
    else:
        return False
