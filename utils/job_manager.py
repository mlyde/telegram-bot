"""job_queue 相关操作"""
import logging
logger = logging.getLogger(__name__)

from telegram import Chat, User
from telegram.ext import ContextTypes, Job

def getJobsByName(context: ContextTypes.DEFAULT_TYPE, name: str) -> bool:
    """根据 name 查找 job"""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    return current_jobs

def getJobsByChatAndUser(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User) -> tuple[Job, ...]:
    """根据 chat + user 查找 job"""
    jobs = [
        job for job in context.job_queue.jobs()
        if job.chat_id == chat.id and job.user_id == user.id
    ]
    return jobs

async def removeJobs(context: ContextTypes.DEFAULT_TYPE, jobs: list[Job], execute = False) -> bool:
    """删除定时任务"""
    if jobs:
        for job in jobs:
            context.job = job
            if execute:
                logger.debug("execute job")
                await job.callback(context)
            else:
                logger.debug("remove job")
            job.schedule_removal()
            context.job = None
        return True
    else:
        return False

async def removeVerifyJobs(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User) -> bool:
    """执行并移除 删除验证消息 任务"""
    jobs = getJobsByChatAndUser(context, chat, user)
    for job in jobs:
        if job.data.get("message_id") is not None:
            logger.debug(f"active verify job: {job}")
            await removeJobs(context, [job], execute=True)

async def removeBanJobs(context: ContextTypes.DEFAULT_TYPE, chat: Chat, user: User, execute = False) -> bool:
    """执行并移除 封禁 任务"""
    jobs = getJobsByChatAndUser(context, chat, user)
    for job in jobs:
        if job.data.get("ban"):
            logger.debug(f"active ban job: {job}")
            await removeJobs(context, [job], execute=execute)
