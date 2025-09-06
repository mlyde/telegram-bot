"""复杂管理员操作"""
import logging
logger = logging.getLogger(__name__)
import datetime

from telegram import Update, ChatPermissions, User, Chat, Message
from telegram.ext import ContextTypes
from telegram.error import BadRequest

from core.static_config import static_config
from core.database import db_user_verification
from utils.get_info import getUserInfo, getChatInfo
from utils.job_manager import removeVerifyJobs, removeBanJobs
forward_to_user_id: int = static_config.get("forward_to")

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
# unmute_permission = ChatPermissions(can_send_messages = True)
unmute_permission = all_permissions

async def banTime(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User, hours=24):
    """封禁一段时间"""
    logger.debug(f"ban {getUserInfo(user)} in {getChatInfo(chat)} for {hours}h")
    to_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    await context.bot.ban_chat_member(chat.id, user.id, until_date=to_date)

async def muteTime(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User, hours: int=0):
    """禁言一段时间"""
    logger.debug(f"mute {getUserInfo(user)} in {getChatInfo(chat)} for {hours}h")
    to_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)
    await context.bot.restrict_chat_member(chat.id, user.id, mute_permission, until_date=to_date)

async def unmute(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User):
    """取消禁言"""
    logger.debug(f"unmute {getUserInfo(user)} in {getChatInfo(chat)}")
    await context.bot.restrict_chat_member(chat.id, user.id, unmute_permission)

async def getAdminList(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """获取群管理员列表"""
    administrators = await context.bot.get_chat_administrators(chat_id)
    return administrators

async def banMemberDelay(context: ContextTypes.DEFAULT_TYPE):
    """超时后将成员移除群组"""
    job = context.job
    chat = job.data.get("chat")
    user = job.data.get("user")
    if job:
        await banTime(context, chat, user, 0.1)
        logger.debug(f"{job.name} ban 6 min")

async def captchaSuccess(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User):
    """验证成功"""
    await removeVerifyJobs(context=context, chat=chat, user=user)
    await removeBanJobs(context=context, chat=chat, user=user)
    await unmute(context, chat, user)
    db_user_verification.setVerified(chat, user)

async def captchaFail(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User):
    """验证失败"""
    await removeVerifyJobs(context=context, chat=chat, user=user)
    await removeBanJobs(context=context, chat=chat, user=user, execute=True)
    db_user_verification.remove(chat, user)

async def deleteMessageCallback(context: ContextTypes.DEFAULT_TYPE):
    """定时删除消息的回调函数"""
    job = context.job
    message_id = job.data.get("message_id")
    if job:
        await context.bot.delete_message(job.chat_id, message_id)
        logger.debug(f"{job.name} deleted")

# async def removeDeleteAccount(context: ContextTypes.DEFAULT_TYPE, chat: Chat):
#     """ 移除群组的 delete account 账户    未实现!!! """
#     # 不存在的方法
#     members: list[User] = await context.bot.get_chat_members(chat_id)
#     try:
#         n = 0
#         for user in members:
#             if user.status == "Delete Account":
#                 await context.bot.ban_chat_member(chat.id, user.id, until_date=0)  # 移除用户, 不封禁
#                 logger.debug(f"已移除 Delete Account ({user.id})")
#                 n += 1
#     finally:
#         logger.info(f"已移除 {getChatInfo(chat)} 的 {n} 个已注销账户")

async def messageExist(context: ContextTypes.DEFAULT_TYPE, from_chat_id, message_id, chat_id=forward_to_user_id):
    """检测一条消息是否存在"""
    # 通过尝试转发消息间接判断消息是否存在
    try:
        message: Message = await context.bot.forward_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id)
        await message.delete()
        return message
    except BadRequest as e:
        if "Message to forward not found" in str(e):
            logger.info("消息不存在或已被删除")
        elif "Chat not found" in str(e):
            logger.info("目标聊天不存在")
        else:
            logger.info(f"转发失败: {e}")
        return False

    # 不存在的方法
    # if message := await context.bot.get_message(chat_id=chat_id,message_id=int(message_id)):
    #     return message
    # else:
    #     return False
