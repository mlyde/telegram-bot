"""
返回一个东西的几个基本信息
"""

import logging
logger = logging.getLogger(__name__)

from telegram import Update, User, Chat, Sticker, Audio, Video, Location
from telegram.ext import ContextTypes


def getUserInfo(user: User) -> str:
    """ 返回 user 的 用户名+自定义id+数字id """

    name = user.full_name if hasattr(user, "full_name") else ''
    link = user.username if hasattr(user, "username") else '' if user.username else ''
    return f"({name})(@{link})({user.id})"

def getChatInfo(chat: Chat) -> str:
    """ 返回 chat 的 群聊名+自定义id+数字id """

    name = chat.effective_name if hasattr(chat, "effective_name") else ''
    link = chat.username if hasattr(chat, "username") else '' if chat.username else ''
    return f"({name})(@{link})({chat.id})"

def getStickerInfo(sticker: Sticker) -> str:
    """ 返回贴纸的 贴纸表情emoji+贴纸id+贴纸包名 """

    return f"({sticker.emoji})({sticker.file_id})({sticker.set_name})"

async def getEmojiStickers(update: Update, context: ContextTypes.DEFAULT_TYPE, emoji_id: str):

    sticker_set = await context.bot.getCustomEmojiStickers(["emoji_id"])
    getStickerInfo(sticker_set)
    return sticker_set

def getAudioInfo(audio: Audio) -> str:
    """返回 audio 的 标题+演唱者+文件名"""

    title = audio.title
    performer = audio.performer
    file_name = audio.file_name
    return f"({title})({performer})({file_name})"
