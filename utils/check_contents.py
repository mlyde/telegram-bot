"""检查是否包含屏蔽词"""
import logging
logger = logging.getLogger(__name__)
import re

from telegram import User, Chat, ChatFullInfo, Message, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from core.database import db_user_verification
from core.block_words import block_worlds_dict, pattern_bio, pattern_button, pattern_chatname, pattern_group_message, pattern_user_id, pattern_username
from core.block_emoji import block_emoji
from utils.get_info import getChatInfo, getStickerInfo, getUserInfo

pattern_list: list = [pattern_bio, pattern_button, pattern_chatname, pattern_group_message, pattern_user_id, pattern_username]

def checkBlockList():
    """ 简单检查屏蔽词列表是否有效或范围过大, 正则很难进行完全测试, 就这样了吧 """
    if test_contain_all_block_words("1Ab谢谢学习资源"):
        logger.error("屏蔽词匹配到正常文本, 请检查屏蔽词列表")
        raise Exception
    elif test_contain_all_block_words("SM俱乐部"):
        logger.debug("屏蔽词匹配正常")

# def findBlockListSource(text: str):
#     """ 在原始屏蔽词列表中查找哪条规则匹配成功, 可用于排查错误 """
#     tmp_list: list[list[str]] = [dic for dic in block_worlds_json.get("blocked_words")]

#     for li in tmp_list:
#         for i in li:
#             if re.findall(i, text):
#                 yield i

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
    if emoji_ids := re.findall("<tg-emoji emoji-id=\"([0-9]{19})\">(?:.*?)</tg-emoji>", message_html):
        return any(any(emoji_id in li  for li in blocked_emoji_dict.values())  for emoji_id in emoji_ids)
    return False

def test_contain_all_block_words(content: str):

    txt = str(content)
    if any(containBlockedWords(txt, pattern) for pattern in pattern_list):
        return True
    else:
        return False

async def checkUserBlockContent(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User):
    """检查用户主页的屏蔽词, 并封禁用户"""
    need_ban = False

    # 名字违禁
    need_ban = (
        need_ban
        or containBlockedWords(user.full_name, pattern_username)
        or containBlockedWords(user.first_name, pattern_username)
        or containBlockedWords(user.username, pattern_user_id)
    )

    # 名字的表情 或 主页中挂的群 或 简介违禁
    if not need_ban:
        user_chat: ChatFullInfo = await context.bot.get_chat(user.id)
        logger.debug(user_chat)
        need_ban = (
            containBlockedWords(user_chat.bio, pattern_bio)
            or containBlockedWords(user_chat.effective_name, pattern_chatname)
            or (containBlockedEmojiId(user_chat.emoji_status_custom_emoji_id, block_emoji.dict) if hasattr(user_chat, "emoji_status_custom_emoji_id") else False)
        )

    if need_ban:
        logger.debug(f"ban {getUserInfo(user)}")
        await context.bot.ban_chat_member(chat.id, user.id)
        return True
    else:
        return False

async def checkMessageBlockContent(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """检查用户发出的消息的屏蔽词, 删除并并封禁用户"""
    # 违禁词或违禁会员表情
    if (containBlockedWords(message.text, pattern_group_message)
        or (containBlockedWords(message.quote.text, pattern_group_message) if message.quote else False)
        or containBlockedEmojiHtml(message.text_html, block_emoji.dict)
    ):
        logger.debug(f"删除消息 {message.id}")
        await message.delete()
        # await changePermission(update, context, False)
        logger.debug(f"ban {getUserInfo(message.from_user)}")
        await context.bot.ban_chat_member(message.chat_id, message.from_user.id)
        return True

    return False

async def checkButtonBlockContent(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """检测按钮中的屏蔽词, 删除并封禁用户"""
    if message and message.reply_markup and message.reply_markup.inline_keyboard:
        texts = [button.text for row in message.reply_markup.inline_keyboard for button in row]
        for text in texts:
            if containBlockedWords(text, pattern_button):
                logger.debug("删除消息")
                await message.delete()
                logger.debug(f"ban {getUserInfo(message.from_user)}")
                await context.bot.ban_chat_member(message.chat_id, message.from_user.id)
                return True
    return False

def userIsActivity(chat: Chat, user: User):
    """查询活跃, 并记录用户活跃"""
    if db_user_verification.isExist(chat, user):
        if db_user_verification.getActivity(chat, user):
            # 活跃过, 直接返回
            return True
    else:
        # 如果用户没有记录, 则记录
        db_user_verification.addUser(chat, user)

    db_user_verification.setActivity(chat, user)
    return False
