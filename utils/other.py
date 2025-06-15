import logging
logger = logging.getLogger(__name__)

import random
import hashlib
import re

from utils.get_info import getUserInfo, getChatInfo


def getMD5(id: int | str) -> str:
    """获取 md5"""

    return hashlib.md5(str(id).encode('utf-8')).hexdigest()

def choiceOne(num: int=None) -> str:
    """ 根据不同概率返回内容 """

    options = ['_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
    weights_normal = [399, 388, 359, 314, 261, 205, 153, 108, 73, 46, 28, 16, 9, 4, 1]      # 正态分布, 数字和为 2364
    return random.choices(options, weights_normal)[0]

def is_md5(string: str) -> bool:
    """使用正则表达式检查是否为32位的16进制字符串, md5格式"""
    pattern = re.compile(r'^[a-fA-F0-9]{32}$')
    return bool(pattern.match(string))
