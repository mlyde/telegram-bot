"""使用会话处理器处理入群消息验证"""
import logging
logger = logging.getLogger(__name__)
import re
import random

from telegram import Update, Message
from telegram.ext import ContextTypes, ConversationHandler
from handle.message_handle import logReceiveMediaMessage
from core.captcha_question import captcha_question_dict
from utils.admin import captchaSuccess, captchaFail
from utils.get_info import getMessageContent, getUserInfo
from utils.job_manager import execute_job_now

# 定义会话状态
CAPTCHA_QUESTION, ANSWER = range(2)

async def startCaptcha(message: Message, context: ContextTypes.DEFAULT_TYPE):
    """开始问题对答"""
    random_item: dict = random.choice(list(captcha_question_dict.values()))
    # 每个用户有独立的 context.user_data 保证持续交互, 默认存储在内存中
    context.user_data["qa"] = random_item
    await message.reply_text(random_item['q'])
    return CAPTCHA_QUESTION

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理问题答案"""
    message, is_edit = getMessageContent(update)
    chat = context.user_data.get("chat")
    user = message.from_user
    answer = context.user_data.get("qa").get('a')

    logReceiveMediaMessage(message, "text", is_edit, message.text_markdown_v2)

    # 检查是否在验证流程中
    if chat and re.search(answer, message.text):
        logger.debug(f"{getUserInfo(user)} captcha success")
        await message.reply_text("回答正确，已解除禁言。")
        await captchaSuccess(message, chat, user)
    else:
        logger.debug(f"{getUserInfo(user)} captcha fail")
        await message.reply_text("回答错误, 请 6 分钟后再试。")
        await captchaFail(message, chat, user)

    await execute_job_now(context, chat, user)
    # 清理用户数据
    # context.user_data.pop("captcha_id", None)
    context.user_data.clear()

    return ConversationHandler.END

async def exitCaptcha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """退出对话"""
    return ConversationHandler.END
