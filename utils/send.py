"""发送消息相关"""
import logging
logger = logging.getLogger(__name__)

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from core.static_config import static_config
directory = static_config.get("directory")

async def send_stream_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, time: int | float=0):
    """ 实现在同一消息中更改变化内容 """

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # 4096 character limit
    logger.debug('test edit message send')
    message = await message.reply_text("正在查询...")
    logger.debug(message.id)
    await asyncio.sleep(3)
    await message.edit_text("查询完毕, 正在处理...")
    await asyncio.sleep(3)
    await message.edit_text("完成.")
    await asyncio.sleep(6)
    await message.delete()


async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 一些发送图片的方法 """

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    # 向聊天对方显示"正在上传照片"状态, 自动显示 5 秒
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

    # 发送一张本地图片
    # with open("/home/mlyder/Downloads/out.jpg", 'rb') as f:
    #     await message.reply_photo(photo=f)
    # await message.reply_photo(photo=open("/home/mlyder/Downloads/out.jpg", 'rb'))

    # 发送一张网络图片
    await message.reply_photo(photo="https://www.baidu.com/favicon.ico")

    # media = [
    #     InputMediaPhoto(open("/home/mlyder/Downloads/out.jpg", 'rb')),
    #     InputMediaPhoto("https://www.baidu.com/favicon.ico")
    # ]
    # 发送多张图片
    # await message.reply_media_group(media=media)

async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送音频"""

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    # await context.bot.send_audio(list(config["admin"].keys())[0], audio=open(f"{FLOADER}/考试什么的都去死吧.mp3", 'rb'))
    await message.reply_audio(audio=open(f"{directory}/考试什么的都去死吧.mp3", 'rb'))

async def send_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送语音"""

async def send_reply_markup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """reply_markup, 为消息添加按钮, 添加按钮键盘, 要求回复指定消息"""

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    button1 = InlineKeyboardButton("Option 1", callback_data="option1")
    button2 = InlineKeyboardButton("Option 2", callback_data="option2")
    reply_markup = InlineKeyboardMarkup([[button1, button2]])

    # 发送带有按钮的消息
    await context.bot.send_message(message.chat_id, text="Please choose an option:", reply_markup=reply_markup)

    # 不太好用, 如何删除键盘是个问题
    # button1 = KeyboardButton("按钮1")
    # button2 = KeyboardButton("按钮2")
    # reply_markup = ReplyKeyboardMarkup([[button1, button2]], resize_keyboard=True, one_time_keyboard=True)
    # # 创建键盘按钮
    # await message.reply_text("请选择一个选项：", reply_markup=reply_markup)

    # 自动选中本条消息要求用户回复
    # await message.reply_text("请输入一些文本：",reply_markup=ForceReply(selective=False))
