import logging
logger = logging.getLogger(__name__)

from telegram import Update, ChatFullInfo, Chat, StickerSet, MessageOrigin, User, Sticker   # 变量注释
from telegram.ext import ContextTypes
from telegram.constants import ChatType, ChatMemberStatus

import re
import datetime
from core.static_config import static_config
from utils.time import utc_timezone
from utils.get_info import getChatInfo, getStickerInfo, getUserInfo
from utils.other import addEmojisId
from utils.lifecycle import stopApp

admin_id_set: set = static_config.get("admin_id")
active_group_id_set = static_config.get("active_group_id")

async def otherCommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ 未匹配的命令 """

    if hasattr(update, "message"):
        message = update.message
    else:
        logger.debug("unknown message")
        logger.debug(update) 
        return
    text = message.text
    # logger.debug(f"{text} from {message.chat.full_name}")
    logger.info(f"receive command({message.id}) from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date.astimezone(utc_timezone)}: {text}")

    # 分离命令和参数
    command: str; arg: str
    command, arg = re.findall(r"^/([\w-]+)\s*(.*)$", text)[0]
    if message.from_user.id in admin_id_set:
        match command:
            # case "flashconfig":
            #     bot_config.flash()
            # case "flashcommand":
            #     await resetBotCommand(update, context)
            # case "flashemoji":  # 重新获取所有表情包id
            #     await flashEmojisId(context)
            case "addemoji":
                await addEmojisId(context, arg.split("https://t.me/addemoji/")[-1], force=True)
            # case "re": # 转义正则中的特殊字符
            #     logger.info(re.escape(arg))
            # case "chdes":   # 更改 bot 自己的 description
            #     await context.bot.set_my_description(description="Anti-Spam for @shandongkeji")
            case "stop":
                await stopApp(update, context)
            case "test":
                logger.debug("/test")
                response = ...
                print(response)
                logger.debug('')

                # to_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
                # await context.bot.ban_chat_member(-1001226170027, 5131500671, until_date=to_date)
    else:
        await message.reply_text("unknown command")

async def unbanCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.chat.type != ChatType.PRIVATE: return     # 只回复私聊
    chat_id: int = active_group_id_set[0]    # 我的山科群

    admins = await context.bot.get_chat_administrators(chat_id)
    if any(admin.user.id == context.bot.id for admin in admins):    # bot 是管理员
        member = await context.bot.get_chat_member(chat_id, update.message.from_user.id)
        if member.status == ChatMemberStatus.BANNED:        # 用户已被ban
            if await context.bot.unban_chat_member(chat_id, update.message.from_user.id):
                await update.message.reply_text("已解除禁言, 你可以再次加入群组了!")
                logger.info(f"解除禁言: {update.message.from_user.full_name}")
        else:
            await update.message.reply_text("You're not on the ban list!")
    else:
        await update.message.reply_text("I can't unban for you!")
