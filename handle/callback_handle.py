import logging
logger = logging.getLogger(__name__)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
from core.static_config import static_config
from utils.admin import captchaSuccess, captchaFail
from utils.send import MyInlineKeyboard
from utils.get_info import getUserInfo, getChatInfo
from utils.job_manager import remove_job_by_chat_and_user_if_exists, remove_job_by_name_if_exists
admins_id_list = static_config.get("admin_id")

# Callback
async def callbackHandle(update: Update, context: CallbackContext | ContextTypes.DEFAULT_TYPE):
    """ 消息下的按钮 点击事件 """
    query = update.callback_query
    message = query.message
    data = query.data
    chat = message.chat
    from_user = query.from_user
    logger.debug(data)

    # 终止按钮点击动画
    await query.answer()

    if data == "option1":
        # await context.bot.send_message(chat_id=chat_id, text="You chose Option 1!")
        logger.debug("更改按钮键盘")
        await context.bot.edit_message_text(chat_id=chat.id, message_id=message.message_id, text='You chose Option 1!', reply_markup=MyInlineKeyboard.markup2)
    elif data == "option2":
        # 更新消息的内联键盘
        # await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message.message_id, reply_markup=None)
        logger.debug("更改按钮键盘")
        await context.bot.edit_message_text(chat_id=chat.id, message_id=message.message_id, text='You chose Option 2!', reply_markup=None)

    if data[:3] in ["pas", "ban"]:
        if from_user.id in admins_id_list:
            action, user_id = data.split('_')
            to_user = await context.bot.get_chat(user_id)
            await context.bot.delete_message(chat.id, message.id)
            remove_job_by_chat_and_user_if_exists(context, chat, to_user)

            if action == "pass":
                logger.info(f"admin {getUserInfo(from_user)} pass {getUserInfo(to_user)} in {getChatInfo(chat)}")
                await captchaSuccess(context, chat, to_user)

            elif action == "ban":
                logger.info(f"admin {getUserInfo(from_user)} ban {getUserInfo(to_user)} in {getChatInfo(chat)}")
                await captchaFail(context, chat, to_user)
