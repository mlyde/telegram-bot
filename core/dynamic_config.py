"""动态获取配置"""
import logging
logger = logging.getLogger(__name__)

from telegram.ext import Application, ContextTypes

from utils.admin import getAdminList
from core.static_config import static_config
active_group_id_list = static_config.get("active_group_id")

async def mainPostInit(app: Application):
    """启动任务主函数, 方便使用多个启动函数"""
    # bot = app.bot
    logger.info("执行启动任务...")
    await getAdminslist(app)
    logger.info("启动任务执行完毕")

async def getAdminslist(app: Application):
    """读取群管理员列表"""
    for group_id in active_group_id_list:
        admins = await getAdminList(app, group_id)  # [-1] 为 Owner
        admins_list = [member.user.id for member in admins]
        static_config["admins_dict"].setdefault(str(group_id), admins_list)
    logger.debug(f"admins_dict: {static_config.get("admins_dict")}")
