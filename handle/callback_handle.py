import logging
logger = logging.getLogger(__name__)


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes


# Callback
async def callbackHandle(update: Update, context: CallbackContext | ContextTypes.DEFAULT_TYPE):
    """ 消息下的按钮 点击事件 """

    query = update.callback_query
    message = query.message
    data = query.data

    button1 = InlineKeyboardButton("Option 2", callback_data="option2")
    reply_markup = InlineKeyboardMarkup([[button1]])

    if data == "option1":
        # await context.bot.send_message(chat_id=message.chat_id, text="You chose Option 1!")
        logger.debug("更改按钮键盘")
        await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='You chose Option 1!', reply_markup=reply_markup)
    elif data == "option2":
        # 更新消息的内联键盘
        # await context.bot.edit_message_reply_markup(chat_id=message.chat_id, message_id=message.message_id, reply_markup=None)
        logger.debug("更改按钮键盘")
        await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='You chose Option 2!', reply_markup=None)

    # 标记验证 回复消息
    if data[:8] == "captcha_":
        logger.debug("验证按钮被按下")

        # 确保按钮点击后的动画被终止
        query = update.callback_query
        await query.answer("1")

        # await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='需要验证', reply_markup=message.reply_markup)
        # await context.bot.edit_message_reply_markup
