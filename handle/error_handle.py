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

    errors = ["httpx.PoolTimeout", "httpx.LocalProtocolError", "SSLError", "httpx.ConnectError", "httpx.ReadError", "httpx.RemoteProtocolError"]

    if isinstance(error, NetworkError):
        logger.error(f"已知 NetworkError 错误: {error}")
        logger.error(f"{error.__cause__}")

    elif any(error in str(error) for error in errors):
        # 重启 updater
        # await restartUpdater(update, context)
        logger.error(f"已知错误: {error}, 要重启 updater 吗?")

    else:
        # 详细错误信息
        tb_list = traceback.format_exception(None, error, error.__traceback__)
        logger.error(f"\n%s", "".join(tb_list))
