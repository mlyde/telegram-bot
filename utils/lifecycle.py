"""application 的启停管理"""
import logging
logger = logging.getLogger(__name__)

from telegram import Update
from telegram.ext import ContextTypes


async def stopApp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """停止 Application"""

    logger.info("Bot is stoping...")

    if context.application.running:
        # 停止轮询
        await context.application.updater.stop()
        # 停止 application
        context.application.stop_running()

async def restartUpdater(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """重启 Application updater"""

    logger.info("restarting updater...")
    if context.application.updater.running:
        await context.application.updater.stop()
        logger.info("stopped updater.")
    await context.application.updater.start_polling()
    logger.info("started updater.")
