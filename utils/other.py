import logging
logger = logging.getLogger(__name__)

import asyncio
import random
import hashlib
from telegram.ext import ContextTypes
from telegram import StickerSet
import re
from utils.get_info import getUserInfo, getChatInfo
from core.block_emoji import block_emoji_dict, emojiJsonWrite


def getMD5(id: int) -> str:
    """获取数字的 md5"""

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


def editEmojiId(emoji_name, sticker_set: StickerSet=None):

    if sticker_set:
        block_emoji_dict[emoji_name] = [sticker.custom_emoji_id for sticker in sticker_set.stickers]
    else:
        del block_emoji_dict[emoji_name]


async def flashEmojisId(context: ContextTypes.DEFAULT_TYPE):
    """ 重新获取 premium_blocked_emoji 表情包中表情的 id 列表 """

    try:
        for emoji_name in emojiJsonWrite:
            logger.info(f"获取 {emoji_name} 表情包")
            sticker_set = await context.bot.get_sticker_set(emoji_name)
            editEmojiId(emoji_name, sticker_set)
        # bot_config.save()
    except TimeoutError:
        logger.error("获取表情包超时")

async def addEmojisId(context: ContextTypes.DEFAULT_TYPE, emoji_name: str, force=False):
    """ 添加 emoji_name 表情包的 id 列表, 添加至 premium_blocked_emoji """

    if emoji_name in block_emoji_dict and not force:
        logger.info(f"表情包 {emoji_name} 已在列表中")
    else:
        sticker_set = await context.bot.get_sticker_set(emoji_name)
        editEmojiId(emoji_name, sticker_set)
        emojiJsonWrite(block_emoji_dict)
        logger.info(f"表情包 {emoji_name} 添加完成")

