"""发送消息相关"""
import logging
logger = logging.getLogger(__name__)
import asyncio
import datetime

from telegram import (
    Update, Message, Chat, User,
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup, ForceReply
)
from telegram.ext import ContextTypes
from telegram.constants import ChatAction, ParseMode

from core.static_config import static_config
from utils.job_manager import deleteMessageJob
from utils.other import choiceOne
from utils.get_info import getMessageContent, getChatInfo, getUserInfo
directory = static_config.get("directory")

class MyInlineKeyboard:
    """常用固定按钮或组合"""
    # 测试
    button1 = InlineKeyboardButton("Option 1", callback_data="option1")
    button2 = InlineKeyboardButton("Option 2", callback_data="option2")
    markup1 = InlineKeyboardMarkup([[button1]])
    markup2 = InlineKeyboardMarkup([[button2]])
    markup3 = InlineKeyboardMarkup([[button1, button2]])

    @classmethod
    def getCaptchaMarkup(cls, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int):
        """指向 bot 的群验证的键盘"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text = "点击此按钮前往验证",
                    callback_data = "captcha",
                    url = f"https://t.me/{context.bot.username}?start=captcha_{chat_id}"
                )
            ],[ # 管理员手动操作
                InlineKeyboardButton(
                    text = "⭕通过(管理员操作)",
                    callback_data = f"pass_{user_id}",
                ),
                InlineKeyboardButton(
                    text = "❌拒绝(管理员操作)",
                    callback_data = f"ban_{user_id}",
                ),
            ],
        ])

    @classmethod
    def getRecaptchaMarkup(cls, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int):
        return InlineKeyboardMarkup([[
            InlineKeyboardButton(
                text = "点击此按钮前往验证",
                callback_data = "recaptcha",
                url = f"https://t.me/{context.bot.username}?start=recaptcha_{chat_id}_{message_id}"
            )
        ]])

async def sendStreamText(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, time: int | float=0):
    """ 实现在同一消息中更改变化内容 """
    message, is_edit = getMessageContent(update)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # * 4096 character limit
    logger.debug('test edit message send')
    message = await message.reply_text("正在查询...")
    logger.debug(message.id)
    await asyncio.sleep(3)
    await message.edit_text("查询完毕, 正在处理...")
    await asyncio.sleep(3)
    await message.edit_text("完成.")
    await asyncio.sleep(6)
    await message.delete()

async def sendPhoto(update: Update, context: ContextTypes.DEFAULT_TYPE, img=None):
    """ 一些发送图片的方法 """
    message, is_edit = getMessageContent(update)

    # 向聊天对方显示"正在上传照片"状态, 自动显示 5 秒
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)

    if img is None:
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
    else:
        await message.reply_photo(photo=img)

async def sendAudio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送音频"""
    message, is_edit = getMessageContent(update)

    # await context.bot.send_audio(chat_id, audio=open(f"{directory}/考试什么的都去死吧.mp3", 'rb'))
    await message.reply_audio(audio=open(f"{directory}/考试什么的都去死吧.mp3", 'rb'))

async def sendVoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送语音"""
    message, is_edit = getMessageContent(update)
    # await message.reply_voice(voice=)

async def sendEasterEggReply(message: Message) -> bool:
    """发送彩蛋消息"""
    today = datetime.datetime.now().date()

    # 愚人节彩蛋
    if today.month == 4 and today.day == 1:
        await message.reply_text("418 I'm a teapot", reply_markup=ReplyKeyboardRemove())
        return True

    return False

async def sendRandomStartReply(message: Message):
    """随机回复"""
    if await sendEasterEggReply(message): return

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

async def sendReplyMarkup(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """reply_markup, 在输入框下方添加按钮键盘, 要求回复指定消息"""

    # 不太好用, 如何删除键盘是个问题
    button1 = KeyboardButton("按钮1")
    button2 = KeyboardButton("按钮2")
    reply_markup = ReplyKeyboardMarkup([[button1, button2]], resize_keyboard=True, one_time_keyboard=True)
    # 创建键盘按钮
    await message.reply_text("请选择一个选项：", reply_markup=reply_markup)

    # 自动选中本条消息要求用户回复
    await message.reply_text("请输入一些文本：",reply_markup=ForceReply(selective=False))

async def sendCaptchaMessage(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User):
    """入群验证消息"""
    sent_message = await context.bot.send_message(
        chat_id = chat.id,
        text = f"{user.full_name}，请在 *5* 分钟内点击下面的按钮，回答两个问题后完成验证，否则你将被移出群组一段时间。",
        reply_markup=MyInlineKeyboard.getCaptchaMarkup(context=context, chat_id=chat.id, user_id=user.id),
        parse_mode=ParseMode.MARKDOWN_V2
    )

    # 定时删除任务
    context.job_queue.run_once(
        callback=deleteMessageJob,
        when=300,  # second
        chat_id=chat.id,
        user_id=user.id,
        name=f"{getChatInfo(chat)}'s captcha for {getUserInfo(user)} message({sent_message.message_id}))",
        data={"chat": chat, "user": user, "message_id": sent_message.message_id},
    )

    return sent_message

async def sendButtonMessage(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """向用户发出二次验证"""
    sent_message = await message.reply_text(
        text="请在下次发消息前完成验证",
        reply_markup=MyInlineKeyboard.getRecaptchaMarkup(context, message.chat.id, message.id)
    )

    return sent_message
