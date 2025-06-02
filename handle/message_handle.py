import logging
logger = logging.getLogger(__name__)

from telegram import Update, InlineKeyboardMarkup, MessageOrigin
from telegram.ext import ContextTypes
from telegram.constants import ChatType

from core.static_config import static_config
from core.block_words import pattern_group_message, pattern_button
from core.block_emoji import block_emoji_dict
from utils.time import utc_timezone
from utils.get_info import getChat3Info, getSticker3Info, getUser3Info
from utils.check_contents import containBlockedEmojiHtml, containBlockedWords, check_all


directory: str = static_config.get("directory")
admin_id_set: set = static_config.get("admin_id")
active_group_id_set: set = static_config.get("active_group_id")

# Message
async def textHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    edit: bool = bool(update.edited_message)
    if edit:
        message = update.edited_message
    else:
        message = update.message

    if message.from_user.is_bot: # bot消息
        logger.info("bot message.")
        logger.debug(message)
        if "已被禁言" in message.text:    # rose 的消息提示
            logger.debug("删除包含 已被禁言 的 rose 消息")
            await message.delete()
        return

    message_type: str = message.chat.type
    text: str = message.text
    reply_markup: InlineKeyboardMarkup = message.reply_markup

    if edit:
        logger.info(f"receive edit text({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}: {text}")    # 在消息上recation也会触发
    else:
        logger.info(f"receive text({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}: {text}")

    if message_type in {ChatType.GROUP, ChatType.SUPERGROUP}:
        if message.chat.id in active_group_id_set:
            # 违禁词或违禁会员表情
            if containBlockedWords(text, pattern_group_message) or containBlockedEmojiHtml(message.text_html, block_emoji_dict):
                logger.debug(f"删除消息 {message.id}")
                await message.delete()
                # await changePermission(update, context, False)
                logger.debug(f"ban {getUser3Info(message.from_user)}")
                await context.bot.ban_chat_member(message.chat_id, message.from_user.id)
                return

    elif update.message.from_user.id in admin_id_set:
        # 将管理员发给 bot 的内容做屏蔽词检测, 全匹配
        text = update.message.text
        logger.info(text)

        if check_all(text):
            text = "匹配成功"
        else:
            text = "不含屏蔽词"

        await update.message.reply_text(text)

async def photoHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if not message:
        logger.debug(update)
    message_type: str = message.chat.type
    caption: str = message.caption  # 图片的说明文字

    # logger.info(f"receive picture({message.id}) { "with caption " if caption else '' }from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")
    if caption:
        logger.info(f"receive picture({message.id}) with caption from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}: {caption}")
    else:
        logger.info(f"receive picture({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}")

    if update.message.from_user.id in admin_id_set:
        photo_id: str = update.message.photo[-1].file_id    # -1 为最大尺寸图片

        # 保存图片
        file = await context.bot.get_file(photo_id)
        await file.download_to_drive(f"{directory}/{file.file_unique_id}_{file.file_path.split('/')[-1]}")
        logger.info("picture saved")

    # attachment: list = update.message.effective_attachment    # 附件

async def videoHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    caption = message.caption
    if caption:
        logger.info(f"receive video({message.id}) from with caption {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}: {caption}")
    else:
        logger.info(f"receive video({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}")

    if message.from_user.id in admin_id_set:
        video_id: str = message.video.file_id    # -1 为最大尺寸
        # 保存视频
        file = await context.bot.get_file(video_id)
        await file.download_to_drive(f"{directory}/{file.file_unique_id}_{file.file_path.split('/')[-1]}")
        logger.info("video saved")

async def documentHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    logger.info(f"receive document({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}: {message.effective_attachment.file_name}")
    if message.chat.type != ChatType.PRIVATE: return # 只回复私聊

async def stickerHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if message is None: return  # 什么时候?, 对消息reaction 好像会产生编辑空消息

    if message.chat.type != ChatType.PRIVATE: return # 只回复私聊

    # sticker_set = await context.bot.get_sticker_set(message.sticker.set_name) # 贴纸包详细内容

    logger.info(f"receive sticker({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}: {getSticker3Info(message.sticker)} from {getChat3Info(message.chat)}")
    # 发送一个相同的贴纸
    await message.reply_sticker(sticker=message.sticker.file_id)
    # await message.reply_sticker(sticker='CAACAgUAAxkBAAICBGaThaP_3NPC0J301sJxAkwv81wZAAKNCQACCYSJVmS11JMf6Da9NQQ')

async def audioHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 音乐或其他类型的音频内容 """

    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    caption: str = message.caption

    if caption:
        logger.info(f"receive audio({message.id}) with \"{caption}\" caption from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}: ({message.audio.title})({message.audio.file_name})")
    else:
        if message.chat.id == message.from_user.id:
            logger.info(f"receive audio({message.id}) from {getUser3Info(message.from_user)} at {message.date.astimezone(utc_timezone)}: ({message.audio.title})({message.audio.performer})({message.audio.file_name})")
        else:
            logger.info(f"receive audio({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}: ({message.audio.title})({message.audio.performer})({message.audio.file_name})")

async def voiceHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 语音消息 """

    message = update.message
    logger.info(f"receive voice({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}")
    logger.debug(message)

    # voice = message.voice
    # voice_file = await context.bot.get_file(voice.file_id)


async def storyHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    logger.info(f"received story({message.id}) from {getUser3Info(message.story.chat)} forwarded by {getUser3Info(message.from_user)} at {message.date.astimezone(utc_timezone)}")
    logger.debug(message)

async def locationHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    logger.info(f"receive location({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_timezone)}")
    logger.debug(message)

async def forwardedHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
                logger.debug(f"ban {getUser3Info(message.from_user)}")
                await context.bot.ban_chat_member(message.chat_id, message.from_user.id)
                break

    # 处理不同的转发消息类型
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

    for message_type, handler in message_handlers.items():
        if getattr(message, message_type):
            logger.info(f"{message_type} type of forwarded message({message.id}) from ({name})({id})")
            if handler: await handler(update, context)
            break
    else:
        logger.info(f"unknown types of forwarded message from ({name})({id})")
        logger.debug(message)
