import logging
logger = logging.getLogger(__name__)

import re
import datetime

from telegram import Update, ChatFullInfo, Chat, StickerSet, MessageOrigin, User, Sticker   # 变量注释
from telegram.ext import ContextTypes
from telegram.constants import ChatType, ChatMemberStatus

from core.static_config import static_config
from core.block_emoji import addEmojisId, flashEmojisId
from utils.get_info import getChatInfo, getStickerInfo, getUserInfo, getMessageContent
from utils.lifecycle import stopApp
from utils.admin import banTime

admin_id_set: set = static_config.get("admin_id")
active_group_id_set = static_config.get("active_group_id")

async def otherCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ 未匹配的命令 """

    message, is_edit = getMessageContent(update)
    text = message.text
    # logger.debug(f"{text} from {message.chat.full_name}")
    logger.info(f"receive command({message.id}) from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}: {text}")

    # 分离命令和参数
    command: str; arg: str
    command, arg = re.findall(r"^/([\w-]+)\s*(.*)$", text)[0]
    if message.from_user.id in admin_id_set:
        match command:
            case "flashemoji":
                await flashEmojisId(context)
            case "addemoji":
                await addEmojisId(context, arg.split("https://t.me/addemoji/")[-1], force=True)
            case "re": # 转义正则中的特殊字符
                logger.info(re.escape(arg))
            case "stop":
                await stopApp(update, context)
            # case "ban":
                # await banMemberTime(context, chat_id=-1001226170027, user_id=8085440182, hours=48)
            case "test":
                logger.debug("/test")
                response = ...
                print(response)
                logger.debug('')
    else:
        await message.reply_text("unknown command")

# async def unbanCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """自助解除封禁, 暂不使用"""

#     message, is_edit = getMessageContent(update)

#     chat_id = active_group_id_set[0]    # 先询问要解除哪个群的封禁
#     if chat_id not in active_group_id_set: return False

#     admins = await context.bot.get_chat_administrators(chat_id)
#     if any(admin.user.id == context.bot.id for admin in admins):    # bot 是管理员
#         member = await context.bot.get_chat_member(chat_id, message.from_user.id)
#         if member.status == ChatMemberStatus.BANNED:        # 用户已被ban
#             if await context.bot.unban_chat_member(chat_id, message.from_user.id):
#                 await message.reply_text("已解除禁言, 你可以再次加入群组了!")
#                 logger.info(f"解除禁言: {message.from_user.full_name}")
#         else:
#             await message.reply_text("You're not on the ban list!")
#     else:
#         await message.reply_text("I can't unban for you!")
