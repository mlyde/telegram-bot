import logging
logger = logging.getLogger(__name__)

from telegram import Update
from telegram.ext import CallbackContext

from utils.time import utc_timezone
from utils.get_info import getChat3Info, getUser3Info


# Reaction
async def reactionHandle(update: Update, context: CallbackContext) -> None:
    """ 处理消息的 reaction 事件 """

    reaction = update.message_reaction
    logger.info(f"Reaction {reaction.new_reaction} from {getUser3Info(reaction.user)} in {getChat3Info(reaction.chat)} for message({reaction.message_id}) at {reaction.date.astimezone(utc_timezone)}.")

