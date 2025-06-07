"""
用户在群中的状态发生变化的处理函数
"""
import logging
logger = logging.getLogger(__name__)

from core.database import db_user_verification
from utils.get_info import getChatInfo, getStickerInfo, getUserInfo
from utils.check_contents import checkUserBlockContent

from telegram.constants import ChatMemberStatus
from telegram import Update
from telegram.ext import ContextTypes


# ChatMember
async def chatMemberHandle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ 新成员加入时, 对名字\简介进行屏蔽词检测 """

    def log_status_different(middle_message: str):
        """简化输出函数, 类似格式的成员状态信息"""
        logger.info(f"{getUserInfo(user)} {middle_message} by {getUserInfo(chat_member.from_user)} in {getChatInfo(chat)} at {chat_member.date}.")

    chat = update.effective_chat
    chat_member = update.chat_member
    user = chat_member.new_chat_member.user

    # old_member_status, new_member_status = chat_member.difference().get("status", (None, None)) # _chat_member.status 不一样时取出
    old_member_status, new_member_status = chat_member.old_chat_member.status, chat_member.new_chat_member.status
    if (old_member_status == new_member_status):
        logger.debug(f"{getUserInfo(user)}member status unchange, still is '{old_member_status}'")
        return
    else:
        logger.debug(f"{getUserInfo(user)}member status changed from '{old_member_status}' to '{new_member_status}'")

    need_remove = False

    match new_member_status:    # 先判断状态变为了什么, 再判断之前是什么
        case ChatMemberStatus.BANNED:
            log_status_different("has been banned")
            need_remove = True
        case ChatMemberStatus.RESTRICTED:   log_status_different("has been restricted")
        case ChatMemberStatus.ADMINISTRATOR:log_status_different("is the administrator")
        case ChatMemberStatus.OWNER:        log_status_different("is owner")
        case ChatMemberStatus.LEFT:
            match old_member_status:
                case ChatMemberStatus.BANNED:log_status_different("has been unbanned")
                case _:                      log_status_different("left")
            need_remove = True
        case ChatMemberStatus.MEMBER:
            match old_member_status:
                case ChatMemberStatus.ADMINISTRATOR:log_status_different("is no longer be administrator")
                case ChatMemberStatus.RESTRICTED:   log_status_different("was no longer restricted")
                case ChatMemberStatus.OWNER:        log_status_different("is no longer the owner")
                case _: # 为新成员
                    log_status_different("is a member")
                    await checkUserBlockContent(context, chat, user)
            db_user_verification.addUser(chat.id, user.id)
        case _:
            logger.warning("unknown member status!")

    if need_remove:
        db_user_verification.remove(chat.id, user.id)
