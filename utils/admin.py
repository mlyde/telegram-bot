import logging
logger = logging.getLogger(__name__)

from telegram import Update, ChatPermissions, User
from telegram.ext import ContextTypes
import datetime

from utils.get_info import getUserInfo, getChatInfo

async def banMemberTime(context: ContextTypes.DEFAULT_TYPE, chat_id, user_id, hours=24):
    """封禁用户一段时间"""

    logger.debug(f"ban {user_id} in {chat_id} for {hours}h")
    to_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    await context.bot.ban_chat_member(chat_id, user_id, until_date=to_date)

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
