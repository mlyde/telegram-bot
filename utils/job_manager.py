"""job_queue 相关操作"""
import logging
logger = logging.getLogger(__name__)

from telegram import Chat, User
from telegram.ext import ContextTypes, Job

def remove_job_by_name_if_exists(context: ContextTypes.DEFAULT_TYPE, name: str) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    logger.debug("remove job")
    return True

def getJobsByChatAndUser(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User) -> tuple[Job, ...]:
    """根据 chat user 查找 job"""
    jobs = [
        job for job in context.job_queue.jobs()
        if job.chat_id == chat.id and job.user_id == user.id
    ]
    return jobs

def remove_job_by_chat_and_user_if_exists(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User) -> bool:
    """根据群与用户 id, 查找并删除 job"""
    jobs = getJobsByChatAndUser(context, chat, user)
    if jobs:
        for job in jobs:
            job.schedule_removal()
        logger.debug("remove job")
        return True
    else:
        return False

async def deleteMessageJob(context: ContextTypes.DEFAULT_TYPE):
    """定时删除消息的回调函数"""
    job = context.job
    message_id = job.data.get("message_id")
    if job:
        await context.bot.delete_message(job.chat_id, message_id)
        logger.debug(f"{job.name} deleted")

async def execute_job_now(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User) -> bool:
    """立即执行 job"""
    jobs = getJobsByChatAndUser(context, chat, user)

    if jobs:
        for job in jobs:
            context.job = job
            await job.callback(context)
            context.job = None
            job.schedule_removal()
        logger.debug("execute job")
        return True
    else:
        return False
