import logging
logger = logging.getLogger(__name__)

from telegram import Update, InlineKeyboardMarkup, MessageOrigin, Message
from telegram.ext import ContextTypes
from telegram.constants import ChatType

from core.static_config import static_config
from core.block_words import pattern_group_message, pattern_button
from core.database import db_user_verification
from utils.get_info import getChatInfo, getStickerInfo, getUserInfo, getAudioInfo
from utils.check_contents import containBlockedEmojiHtml, containBlockedWords, test_contain_all_block_words, checkMessageBlockContent, checkUserBlockContent, userIsActivity


directory: str = static_config.get("directory")
admin_id_set: set = static_config.get("admin_id")
active_group_id_set: set = static_config.get("active_group_id")
GROUPS_SET = {ChatType.GROUP, ChatType.SUPERGROUP}

def logReceiveMediaMessage(message: Message, type, is_edit: bool, info):
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
    is_reply = bool(message.reply_to_message)
    text = message.text

    log_text = ("receive edit" if is_edit else "receive")\
         + f" text({message.id}) from {getUserInfo(message.from_user)} in"\
         + (" private chat" if message.chat.id == message.from_user.id else f" {getChatInfo(message.chat)}")\
         + (f" reply to message({message.reply_to_message.id})" if is_reply else '')\
         + f" at {message.date}: {text}"
    logger.info(log_text)

    message_type = message.chat.type
    # reply_markup: InlineKeyboardMarkup = message.reply_markup

    # 如果用户是第一次活跃, 检查用户页内容
    if not userIsActivity(chat_id=message.chat.id, user_id=message.from_user.id):
        await checkUserBlockContent(context, message.chat, message.from_user)

    if message_type in GROUPS_SET:
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

    logReceiveMediaMessage(message, "photo", is_edit, '')

    # if update.message.from_user.id in admin_id_set:
    #     photo_id: str = update.message.photo[-1].file_id    # -1 为最大尺寸图片

    #     # 保存图片
    #     file = await context.bot.get_file(photo_id)
    #     await file.download_to_drive(f"{directory}/{file.file_unique_id}_{file.file_path.split('/')[-1]}")
    #     logger.info("picture saved")

    # attachment: list = message.effective_attachment    # 附件

async def videoHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    logReceiveMediaMessage(message, "video", is_edit, '')

    if message.from_user.id in admin_id_set:
        video_id: str = message.video.file_id    # -1 为最大尺寸
        # 保存视频
        file = await context.bot.get_file(video_id)
        await file.download_to_drive(f"{directory}/{file.file_unique_id}_{file.file_path.split('/')[-1]}")
        logger.info("video saved")

async def documentHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    logReceiveMediaMessage(message, "document", is_edit, '')

async def stickerHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    logReceiveMediaMessage(message, "sticker", is_edit, getStickerInfo(message.sticker))

    # sticker_set = await context.bot.get_sticker_set(message.sticker.set_name) # 贴纸包详细内容

    if message.chat.type != ChatType.PRIVATE: return # 只回复私聊
    # 发送一个相同的贴纸
    await message.reply_sticker(sticker=message.sticker.file_id)
    # await message.reply_sticker(sticker='CAACAgUAAxkBAAICBGaThaP_3NPC0J301sJxAkwv81wZAAKNCQACCYSJVmS11JMf6Da9NQQ')

async def audioHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 音乐或其他类型的音频内容 """

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message
    info = getAudioInfo(message.audio)

    logReceiveMediaMessage(message, "audio", is_edit, info)


async def voiceHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 语音消息 """

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    logReceiveMediaMessage(message, "voice", is_edit, '')
    logger.debug(message)

    # voice = message.voice
    # voice_file = await context.bot.get_file(voice.file_id)


async def storyHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    # story 类型好像只能转发到聊天
    logger.info(f"received story({message.id}) from {getUserInfo(message.story.chat)} forwarded by {getUserInfo(message.from_user)} at {message.date}")
    logger.debug(message)

async def locationHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    is_edit = bool(update.edited_message)
    message = update.edited_message if is_edit else update.message

    logReceiveMediaMessage(message, "location", is_edit, '')

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
    'video_note': None, # 圆形视频消息
}

async def forwardedHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """所有转发消息"""

    message = update.message
    # 能否获得消息来源者信息
    forward_origin: MessageOrigin = message.forward_origin
    if forward_origin.type == forward_origin.USER:  # 用户
        name = forward_origin.sender_user.full_name
        id = forward_origin.sender_user.id
    elif forward_origin.type in {forward_origin.CHAT, forward_origin.CHANNEL}:  # 群或频道
        name = forward_origin.chat.title
        id = forward_origin.chat.id
    elif forward_origin.type == forward_origin.HIDDEN_USER: # 隐藏的用户名
        name = forward_origin.sender_user_name
        id = None

    # logger.debug(message)

    if message and message.reply_markup and message.reply_markup.inline_keyboard:
        texts = [button.text for row in message.reply_markup.inline_keyboard for button in row]
        for text in texts:
            if containBlockedWords(text, pattern_button):
                logger.debug("删除消息")
                await message.delete()
                logger.debug(f"ban {getUserInfo(message.from_user)}")
                await context.bot.ban_chat_member(message.chat_id, message.from_user.id)
                break

    # 处理不同的转发消息类型
    for message_type, handler in message_handlers.items():
        if getattr(message, message_type):
            logger.info(f"{message_type} type of forwarded message({message.id}) from ({name})({id})")
            if handler: await handler(update, context)
            break
    else:
        logger.info(f"unknown types of forwarded message from ({name})({id})")
        logger.debug(message)

# async def handleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """处理所有非转发消息"""

#     is_edit = bool(update.edited_message)
#     message = update.edited_message if is_edit else update.message
#     caption = message.caption              # 说明文字
#     is_reply = bool(message.reply_to_message)   # 回复其他消息

#     # 处理不同消息类型
#     for message_type, handler in message_handlers.items():
#         if getattr(message, message_type):
#             log_text = f"{message_type} message({message.id}) from {getUserInfo(message.from_user)}"
#             logger.info(log_text)
#             if handler: await handler(update, context)
#             break
#     else:
#         logger.info(f"unknown types of forwarded message from {getUserInfo(message.from_user)}")
#         logger.debug(message)
