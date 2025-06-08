import logging
logger = logging.getLogger(__name__)

from telegram import Update, InlineKeyboardMarkup, MessageOrigin, Message
from telegram.ext import ContextTypes
from telegram.constants import ChatType

from core.static_config import static_config
from core.block_words import pattern_group_message, pattern_button
from core.database import db_user_verification
from utils.get_info import (
    getChatInfo, getUserInfo, getMessageOriginInfo,
    getAudioInfo, getCommonFileInfo, getStickerInfo, getStickerSetInfo, getStoryInfo,
    getLocationInfo, getVoiceInfo, getAudioInfo, getVideoInfo, getPhotoSizeInfo, getVideoNoteInfo
    )
from utils.check_contents import test_contain_all_block_words, checkMessageBlockContent, checkUserBlockContent, userIsActivity, checkButtonBlockContent

directory: str = static_config.get("directory")
admin_id_set: set = static_config.get("admin_id")
active_group_id_set: set = static_config.get("active_group_id")
groups_set = {ChatType.GROUP, ChatType.SUPERGROUP}

def logReceiveMediaMessage(message: Message, type: str, is_edit: bool, info: str = None):
    """整合媒体消息接收日志"""

    is_reply = bool(message.reply_to_message)
    caption = message.caption

    # 媒体消息
    log_text = (f"receive edit {type}({message.id})" if is_edit else f"receive {type}({message.id})")\
        + (f" reply to message({message.reply_to_message.id})" if is_reply else '')\
        + (f" with \"{caption}\" caption" if caption else '')\
        + f" from {getUserInfo(message.from_user)} in"\
        + (" private chat" if message.chat.id == message.from_user.id else f" {getChatInfo(message.chat)}")\
        + f" at {message.date}"\
        + (f": {info}" if info else '')
    logger.info(log_text)

# Message
async def textHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    text = message.text
    message_type = message.chat.type
    logReceiveMediaMessage(message, "text", is_edit, text)

    # 如果用户是第一次活跃, 二次检查用户页内容
    if not userIsActivity(chat_id=message.chat.id, user_id=message.from_user.id):
        await checkUserBlockContent(context, message.chat, message.from_user)

    if message_type in groups_set:
        if message.chat.id in active_group_id_set:
            await checkMessageBlockContent(message, context)

    elif message.from_user.id in admin_id_set:
        # 将管理员发给 bot 的内容做屏蔽词检测, 全匹配
        text = message.text
        logger.info(text)

        text = "匹配成功" if test_contain_all_block_words(text) else "不含屏蔽词"
        await update.message.reply_text(text)

async def photoHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    photo_info = getPhotoSizeInfo(message.photo)
    logReceiveMediaMessage(message, "photo", is_edit, photo_info)

    # if message.from_user.id in admin_id_set:
    #     photo_id = message.photo[-1].file_id    # -1 为最大尺寸图片
    #     # 保存图片
    #     file = await context.bot.get_file(photo_id)
    #     await file.download_to_drive(f"{directory}/{file.file_unique_id}_{file.file_path.split('/')[-1]}")
    #     logger.info(f"photo {photo_info} saved")

async def videoHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    video_info = getVideoInfo(message.video)
    logReceiveMediaMessage(message, "video", is_edit, video_info)

    # if message.from_user.id in admin_id_set:
    #     video_id = message.video.file_id    # -1 为最大尺寸
    #     # 保存视频
    #     file = await context.bot.get_file(video_id)
    #     await file.download_to_drive(f"{directory}/{file.file_unique_id}_{file.file_path.split('/')[-1]}")
    #     logger.info(f"video {video_info} saved")

async def documentHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    document_info = getCommonFileInfo(message.document)

    logReceiveMediaMessage(message, "document", is_edit, document_info)

async def stickerHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    sticker_info = getStickerInfo(message.sticker)
    logReceiveMediaMessage(message, "sticker", is_edit, sticker_info)

    if message.chat.type == ChatType.PRIVATE:
        # 如果是私聊, 回复一个相同的贴纸
        await message.reply_sticker(sticker=message.sticker.file_id)
        return
    # await message.reply_sticker(sticker='CAACAgUAAxkBAAICBGaThaP_3NPC0J301sJxAkwv81wZAAKNCQACCYSJVmS11JMf6Da9NQQ')

async def audioHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 音乐或其他类型的音频内容 """

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    audio_info = getAudioInfo(message.audio)
    logReceiveMediaMessage(message, "audio", is_edit, audio_info)

async def voiceHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 语音消息 """

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    voice_info = getVoiceInfo(message.voice)
    logReceiveMediaMessage(message, "voice", is_edit, voice_info)

    # voice_file = await context.bot.get_file(message.voice.file_id)

async def videoNoteHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """圆形视频消息"""

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    video_note_info = getVideoNoteInfo(message.video_note)
    logReceiveMediaMessage(message, "video note", is_edit, video_note_info)

async def storyHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    story_info = getStoryInfo(message.story)

    # story 类型好像只能转发到聊天
    logger.info(f"received story({message.id}) from {getUserInfo(message.story.chat)} forwarded by {getUserInfo(message.from_user)} at {message.date}: {story_info}")

async def locationHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    lal = getLocationInfo(message.location)
    logReceiveMediaMessage(message, "location", is_edit, lal)

async def lastHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """未匹配的消息类型"""

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    logger.debug(message)

# 不同类型消息对应的函数
message_handlers = {
    'text': textHandleMessage,
    'photo': photoHandleMessage,
    'document': documentHandleMessage,
    'sticker': stickerHandleMessage,
    'video': videoHandleMessage,
    'audio': audioHandleMessage,
    'voice': voiceHandleMessage,
    'story': storyHandleMessage,
    'location': locationHandleMessage,
    "video_note": videoNoteHandleMessage,
}

async def forwardedHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """所有转发消息"""

    message = update.message
    message_origin_info = getMessageOriginInfo(message.forward_origin)

    await checkButtonBlockContent(message, context)

    # 处理不同的转发消息类型
    for message_type, handler in message_handlers.items():
        if getattr(message, message_type):
            logger.info(f"received {message_type} type of forwarded message({message.id}) from {message_origin_info}")
            if handler: await handler(update, context)
            break
    else:
        logger.info(f"unmatch types of forwarded message from {message_origin_info}")
        logger.debug(message)
