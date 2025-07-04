"""使用会话处理器处理入群消息验证"""
import logging
logger = logging.getLogger(__name__)
import re
import random

from telegram import Update, Message
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from handle.message_handle import logReceiveMediaMessage
from core.captcha_question import captcha_question_dict
from utils.admin import captchaSuccess, captchaFail
from utils.get_info import getMessageContent, getUserInfo
from utils.captcha import generateCaptcha
question_answer_list = list(captcha_question_dict.values())

# 定义会话状态
CAPTCHA, QUESTION_ANSWER = range(2)

async def startCaptcha(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """开始问题对答"""
    img, result = generateCaptcha()
    # 每个用户有独立的 context.user_data 保证持续交互, 默认存储在内存中
    context.user_data["captcha"] = result
    await message.reply_photo(photo=img, caption="请回答该式子的计算结果")
    return CAPTCHA

async def handleCaptcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """传统验证码"""
    message, is_edit = getMessageContent(update)
    chat = context.user_data.get("chat")
    user = message.from_user
    captcha = context.user_data.get("captcha")

    logReceiveMediaMessage(message, "text", is_edit, message.text_markdown_v2)

    if message.text and captcha in message.text:
        logger.info(f"{getUserInfo(user)} captcha success")
        random_item: dict = random.choice(question_answer_list)
        context.user_data["answer"] = random_item.get("a")
        await message.reply_text(random_item.get("q"), parse_mode=ParseMode.MARKDOWN_V2)
        return QUESTION_ANSWER
    else:
        logger.info(f"{getUserInfo(user)} captcha fail")
        await message.reply_text("回答错误, 请 6 分钟后再试。")
        await captchaFail(context, chat, user)
        return ConversationHandler.END

async def handleQA(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """回答问题"""
    message, is_edit = getMessageContent(update)
    chat = context.user_data.get("chat")
    user = message.from_user
    answer = context.user_data.get("answer")

    logReceiveMediaMessage(message, "text", is_edit, message.text_markdown_v2)

    if chat and re.search(answer, message.text):
        logger.info(f"{getUserInfo(user)} QA success")
        await message.reply_text("回答正确，已解除禁言。")
        await captchaSuccess(context, chat, user)
    else:
        logger.info(f"{getUserInfo(user)} QA fail")
        await message.reply_text("回答错误, 请 6 分钟后再试。")
        await captchaFail(context, chat, user)
        return ConversationHandler.END

async def exitCaptcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """退出对话"""
    # 清理用户数据
    context.user_data.clear()
    return ConversationHandler.END
