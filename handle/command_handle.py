"""CommandHandler 的 callback 函数"""
import logging
logger = logging.getLogger(__name__)
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler
from telegram.constants import ChatType, ParseMode

from core.static_config import static_config
from handle.conversation_handle import startCaptcha
from utils.admin import banTime, muteTime
from utils.get_info import getChatInfo, getStickerInfo, getUserInfo, getMessageContent
from utils.other import getMD5
from utils.time import last_start_up_time
from utils.send import sendRandomStartReply
admin_id_list: list = static_config.get("admin_id")
help_content = static_config.get("help_content")

# Commands
async def startCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """开始对话"""
    message, is_edit = getMessageContent(update)
    logger.info(f"/start from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")

    # 删除消息, 防止群组其他人跟着点
    if message.chat.type != ChatType.PRIVATE:
        logger.debug("删除 /start 消息")
        await message.delete()
    else:
        await sendRandomStartReply(message)

    return ConversationHandler.END

async def startArgsCommand(update: Update, context: CallbackContext):
    """携带参数的对话, deep link, 最长 64 字符
    https://t.me/sdustbot?start=parameter"""
    message, is_edit = getMessageContent(update)

    if args := context.args:
        logger.info(f"/start with \"{' '.join(args)}\" from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")
        # 过滤入群验证, 负数 id 为群 id
        if args[0][:9]=="captcha_-":
            chat_id = int(args[0].split('_')[1])
            chat = await context.bot.get_chat(chat_id)
            logger.info(f"{getUserInfo(message.from_user)} 发起在群组 {getChatInfo(chat)} 的验证")
            context.user_data["chat"] = chat
            return await startCaptcha(message, context)
        else:
            logger.debug("/start: unknown args")

    await startCommand(update, context)
    return ConversationHandler.END

async def uptimeCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """已运行时间"""
    message, is_edit = getMessageContent(update)
    logger.info(f"/uptime from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")
    text = "已运行时间: %.0f s" % (time.time() - last_start_up_time.stamp)
    logger.info(text)
    await message.reply_text(text)

async def helpCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """帮助信息"""
    message = update.message
    logger.info(f"/help from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")

    text = help_content
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN_V2)

async def banCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """封禁用户一段时间或永久"""
    message, is_edit = getMessageContent(update)
    time = 0 if context.args is None else int(context.args[0])
    logger.info(f"/ban from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date} for {time}h")
    await message.delete()
    if message.from_user.id in admin_id_list and message.reply_to_message is not None:
        await banTime(context, message.chat, message.reply_to_message.from_user, time)

async def captchaCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """标记用户, 由 bot 向用户发起一次验证"""   # 未使用
    message, is_edit = getMessageContent(update)
    args = context.args
    logger.info(f"/captcha from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")

    if message.from_user.id in admin_id_list:
        if message.reply_to_message.from_user:
            # 标记的用户的 id
            message.reply_to_message.from_user.id
            logger.debug(f"{getUserInfo(message.from_user)} 使用 /captcha 标记了 {getUserInfo(message.reply_to_message.from_user)}")
            user_id_md5 = getMD5(message.reply_to_message.from_user.id)
            # 记下message id, 完成验证后删除消息
            captcha_ask = await context.bot.send_message(chat_id=message.chat.id,
                                           text="用户已被标记, 请在下次发出消息前完成验证",
                                           reply_to_message_id=message.reply_to_message.id,
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("去验证",
                                                                                                    callback_data=f"captcha_{user_id_md5}",
                                                                                                    url=f"https://t.me/{context.bot.username}?start={user_id_md5}")]])
                                           )
            logger.debug(f"验证消息id: {captcha_ask.id}, 被标记消息id: {message.reply_to_message.id}")
            await message.delete()

    if args:
        print(args)
    if message.chat.type == ChatType.PRIVATE:
        message.reply_text("验证")

async def muteCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """群内回复指定消息, 将消息来源用户封禁"""
    message, is_edit = getMessageContent(update)
    await message.delete()
    logger.info(f"/mute from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")
    if message.from_user.id in admin_id_list and message.reply_to_message is not None:
        mute_hour = 0 if context.args is None else int(context.args[0])

        reply_to_user = message.reply_to_message.from_user

        logger.info(f"mute {getUserInfo(reply_to_user)} in {getChatInfo(message.chat)} at {message.date} for {mute_hour}h")
        await muteTime(context, message.chat, reply_to_user)
