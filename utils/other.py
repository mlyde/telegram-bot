import logging
logger = logging.getLogger(__name__)

import asyncio
import random
import hashlib
from telegram.ext import ContextTypes
from telegram import Update, User, ChatPermissions, StickerSet
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

async def removeDeleteAccount(context: ContextTypes.DEFAULT_TYPE, chat_id: str | int):
    """ 移除群组的 delete account 账户    未实现!!! """

    administrators = await context.bot.get_chat_administrators(chat_id)
    member_count = await context.bot.get_chat_member_count(chat_id)
    members: list[User] = []
    try:
        n = 0
        for user in members:
            if user.status == "Delete Account":
                await context.bot.ban_chat_member(chat_id, user.id, until_date=0)  # 移除用户, 不封禁
                logger.debug(f"已移除 Delete Account ({user.id})")
                n += 1
    finally:
        logger.info(f"已移除 {n} 个已注销账户")

async def messageExist(context: ContextTypes.DEFAULT_TYPE, chat_id, message_id):
    """检测一条消息是否存在    未实现!!!"""

    # 通过尝试转发消息判断消息是否存在
    response = await context.bot.forward_message(chat_id=-1001226170027, from_chat_id=-1001226170027, message_id=21834)
    return True
    return False

async def changePermission(update: Update, context: ContextTypes.DEFAULT_TYPE, permission: bool):
    """ 给予或禁止权限 """

    chat = update.message.chat
    user = update.message.from_user

    whether = bool(permission)
    all_permissions = ChatPermissions(
        can_send_messages = whether,
        can_send_polls = whether,
        can_send_other_messages = whether,
        can_add_web_page_previews = whether,
        can_change_info = whether,
        can_invite_users = whether,
        can_pin_messages = whether,
        can_manage_topics = whether,
        can_send_audios = whether,
        can_send_documents = whether,
        can_send_photos = whether,
        can_send_videos = whether,
        can_send_video_notes = whether,
        can_send_voice_notes = whether,
    )

    await context.bot.restrict_chat_member(chat.id, user.id, all_permissions)
    if whether:
        logger.info(f"已给予 {getUserInfo(user)} 在 {getChatInfo(chat)} 的权限")
    else:
        logger.info(f"已禁止 {getUserInfo(user)} 在 {getChatInfo(chat)} 的权限")

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

