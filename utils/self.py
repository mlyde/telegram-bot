"""bot 对自己的操作"""
import logging
logger = logging.getLogger(__name__)

from telegram import Update, BotCommand, BotCommandScopeAllPrivateChats
from telegram.ext import ContextTypes


async def setBotCommandHint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """设置 bot 自己的命令提示列表"""

    logger.debug("删除 bot 命令提示")
    await context.bot.delete_my_commands()
    commands_user = [
        BotCommand("start", "Start this dialogue and initialization"),
        BotCommand("uptime", 'Uptime'),
        BotCommand("help", "Provides help for this bot")
    ]
    logger.debug("设置 bot 命令提示")

    # 只设置私聊提示
    return await context.bot.set_my_commands(commands_user, scope=BotCommandScopeAllPrivateChats())
