"""复杂管理员操作"""
import logging
logger = logging.getLogger(__name__)

import datetime

from telegram import Update, ChatPermissions, User, Chat
from telegram.ext import ContextTypes

from utils.get_info import getUserInfo, getChatInfo

_example = ChatPermissions(
    can_send_messages = False,
    can_send_polls = False,
    can_send_other_messages = False,
    can_add_web_page_previews = False,
    can_change_info = False,
    can_invite_users = False,
    can_pin_messages = False,
    can_manage_topics = False,
    can_send_audios = False,
    can_send_documents = False,
    can_send_photos = False,
    can_send_videos = False,
    can_send_video_notes = False,
    can_send_voice_notes = False,
)
all_permissions = ChatPermissions.all_permissions()
no_permissions = ChatPermissions.no_permissions()
mute_permission = ChatPermissions(can_send_messages = False)    # 其他发送权限自动失效

async def banTime(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User, hours=24):
    """封禁一段时间"""

    logger.debug(f"ban {getUserInfo(user)} in {getChatInfo(chat)} for {hours}h")
    to_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    await context.bot.ban_chat_member(chat.id, user.id, until_date=to_date)

async def muteTime(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User, hours: int):
    """禁言一段时间"""

    logger.debug(f"mute {getUserInfo(user)} in {getChatInfo(chat)} for {hours}h")
    to_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    await context.bot.restrict_chat_member(chat.id, user.id, mute_permission, until_date=to_date)

# async def removeDeleteAccount(context: ContextTypes.DEFAULT_TYPE, chat_id: str | int):
#     """ 移除群组的 delete account 账户    未实现!!! """

#     administrators = await context.bot.get_chat_administrators(chat_id)
#     member_count = await context.bot.get_chat_member_count(chat_id)
#     members: list[User] = []
#     try:
#         n = 0
#         for user in members:
#             if user.status == "Delete Account":
#                 await context.bot.ban_chat_member(chat_id, user.id, until_date=0)  # 移除用户, 不封禁
#                 logger.debug(f"已移除 Delete Account ({user.id})")
#                 n += 1
#     finally:
#         logger.info(f"已移除 {n} 个已注销账户")

# async def messageExist(context: ContextTypes.DEFAULT_TYPE, chat_id, message_id):
#     """检测一条消息是否存在    未实现!!!"""

#     # 通过尝试转发消息判断消息是否存在
#     response = await context.bot.forward_message(chat_id=-1001226170027, from_chat_id=-1001226170027, message_id=21834)
#     return True
#     return False
