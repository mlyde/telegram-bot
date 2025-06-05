"""
CommandHandler 的 callback 函数
"""
import logging
logger = logging.getLogger(__name__)

from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from telegram.constants import ChatType, ParseMode

import time
import datetime

from core.static_config import static_config
from utils.time import utc_timezone
from utils.get_info import getChatInfo, getStickerInfo, getUserInfo
from utils.other import getMD5, choiceOne
from utils.time import last_start_up_time

admin_id_set: set = static_config.get("admin_id")


# Commands
async def startCommand(update: Update, context: CallbackContext):

    message = update.message if update.edited_message is None else update.edited_message
    args = context.args # https://t.me/sdustbot?start=parameter 好像只能收到一个参数
    logger.info(f"/start with \"{' '.join(args)}\" from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")

    if message.chat.type != ChatType.PRIVATE:
        logger.debug("删除 /start 消息")
        await message.delete()    # 删除消息, 防止其他人跟着点
        return     # 只回复私聊

    # 判断参数是否为对应正确验证参数
    if args and args[0] == getMD5(message.chat.id):
        await message.reply_text("captcha")
        return

    today = datetime.datetime.now().date()
    if today.month == 4 and today.day == 1:     # 愚人节彩蛋
        await message.reply_text("418 I'm a teapot", reply_markup=ReplyKeyboardRemove())
        return

    choice = choiceOne()
    match choice:
        case 'g':
            await message.reply_text("Let's get started.", reply_markup=ReplyKeyboardRemove())
        case 'h':
            await message.reply_sticker(sticker='CAACAgUAAxkBAAICBGaThaP_3NPC0J301sJxAkwv81wZAAKNCQACCYSJVmS11JMf6Da9NQQ')   # 贴纸内容: 柴郡头猫猫趴在西瓜上
        case 'i':
            await message.reply_text("emm, may I help you?", reply_markup=ReplyKeyboardRemove())
        case _:
            await message.reply_text("Hello! I am a bot. <b>^_^</b>", reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)

async def uptimeCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message if update.edited_message is None else update.edited_message
    logger.info(f"/uptime from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")
    text = "已运行时间: %.0f s" % (time.time() - last_start_up_time.stamp)
    logger.info(text)
    await message.reply_text(text)

async def helpCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    logger.info(f"/help from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")

    text = "山东科技大学群组: @shandongkeji"
    await message.reply_text(text)

async def captchaCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message:
        message = update.message
    else:
        # 若编辑消息后的命令
        message = update.edited_message
    args = context.args
    logger.info(f"/captcha from {getUserInfo(message.from_user)} in {getChatInfo(message.chat)} at {message.date}")

    if message.from_user.id in admin_id_set:

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
