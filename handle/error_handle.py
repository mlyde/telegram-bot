"""
错误处理
"""
import logging
logger = logging.getLogger(__name__)

import traceback
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError
from utils.lifecycle import restartUpdater

# error handle
async def errorHandle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    error = context.error
    logger.error(f"Error handler catch: {error}")

    if isinstance(error, NetworkError):
        ...
        # 重启 updater
        # await restartUpdater(update, context)

    else:
        # 详细错误信息
        logger.error(f"__cause__: {error.__cause__}")
        tb_list = traceback.format_exception(None, error, error.__traceback__)
        logger.error(f"\n%s", "".join(tb_list))
