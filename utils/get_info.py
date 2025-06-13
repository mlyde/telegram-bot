"""返回基本信息"""
import logging
logger = logging.getLogger(__name__)

from telegram import (
    Update, User, Chat, Message,
    MessageOriginUser, MessageOriginChat, MessageOriginChannel, MessageOriginHiddenUser,
    Sticker, Audio, Video, Location, Document, Voice, PhotoSize, VideoNote, Story
    )
from telegram.ext import ContextTypes


def getUserInfo(user: User) -> str:
    """ 返回 user 的 用户名+自定义id+数字id """

    name = user.full_name if hasattr(user, "full_name") else ''
    link = user.username if hasattr(user, "username") else '' if user.username else ''
    return f"({name})(@{link})({user.id})"

def getChatInfo(chat: Chat) -> str:
    """ 返回 chat 的 群聊名+自定义id+数字id """

    name = chat.effective_name if hasattr(chat, "effective_name") else ''
    link = chat.username if hasattr(chat, "username") else '' if chat.username else ''
    return f"({name})(@{link})({chat.id})"

def getMessageOriginInfo(forward_origin: MessageOriginUser | MessageOriginHiddenUser | MessageOriginChat | MessageOriginChannel) -> str:
    """获取消息来源的信息"""

    if forward_origin.type == forward_origin.USER:
        # 用户
        return getUserInfo(forward_origin.sender_user)
    elif forward_origin.type == forward_origin.HIDDEN_USER:
        # 隐藏用户名的用户
        name = forward_origin.sender_user_name
        link = id = None
        return f"({name})(@{link})({id})"
    elif forward_origin.type == forward_origin.CHAT:
        # 群
        return getChatInfo(forward_origin.sender_chat)
    elif forward_origin.type == forward_origin.CHANNEL:
        # 频道
        message_id = forward_origin.message_id
        return getChatInfo(forward_origin.chat)

def getStickerInfo(sticker: Sticker) -> str:
    """贴纸信息 - 贴纸表情emoji+贴纸包名+贴纸id"""

    return f"({sticker.emoji})({sticker.set_name})({sticker.file_unique_id})"

async def getStickerSetInfo(update: Update, context: ContextTypes.DEFAULT_TYPE, set_name: str) -> str:
    """sticker set 贴纸包信息"""

    sticker_set = await context.bot.get_sticker_set(set_name) # 贴纸包详细内容
    name = sticker_set.name      # id
    title = sticker_set.title
    sticker_type = sticker_set.sticker_type
    stickers: tuple = sticker_set.stickers  # 贴纸包内容

    return f"({title})({name})({sticker_type})(number: {len(stickers)})"

def getLocationInfo(location: Location) -> str:
    """位置信息"""

    longitude, latitude = location.longitude, location.latitude # 经度, 纬度
    return f"({longitude}, {latitude})"

def getStoryInfo(story: Story) -> str:
    """story 信息"""

    chat = story.chat
    id = story.id

    return f"({chat})({id})"

def getCommonFileInfo(file: Document) -> str:
    """一般文件的通用信息"""

    name = file.file_name
    mime_type = file.mime_type
    size = file.file_size  # bytes
    unique_id = file.file_unique_id

    return f"({unique_id})({name})({mime_type})(size: {size})"

def getVoiceInfo(voice: Voice) -> str:
    """voice 信息"""

    mime_type = voice.mime_type
    size = voice.file_size
    unique_id = voice.file_unique_id
    duration = voice.duration

    return f"({unique_id})({mime_type})(size: {size})(duration: {duration}s)"

def getVideoNoteInfo(video_note: VideoNote) -> str:
    """video note 圆形视频信息"""

    size = video_note.file_size
    unique_id = video_note.file_unique_id
    duration = video_note.duration
    length = video_note.length  # 宽 = 高 = 直径
    # thumbnail = video_note.thumbnail

    return f"({unique_id})(size: {size})(duration: {duration}s)(D = {length})"

def getVideoInfo(video: Video) -> str:
    """video 信息"""

    duration = video.duration
    width, height = video.width, video.height
    thumbnail = video.thumbnail
    # thumbnail_info = getPhotoSizeInfo(thumbnail)
    # cover = video.cover

    return getCommonFileInfo(video) + f"(duration: {duration}s)({width} x {height})"

def getAudioInfo(audio: Audio) -> str:
    """audio 音频的信息"""

    duration = audio.duration
    title = audio.title
    performer = audio.performer

    return getCommonFileInfo(audio) + f"(duration: {duration}s)({title} - {performer})"

def getPhotoSizeInfo(photo_size: tuple[PhotoSize]) -> str:
    """照片信息"""

    # [-1] 为原图, 只保留原图信息
    photo_size = photo_size[-1:]
    photo_list = []

    for photo in photo_size:
        unique_id = photo.file_unique_id
        width, height = photo.width, photo.height
        size = photo.file_size

        photo_list.append(f"({unique_id})(size: {size})({width} x {height})")

    return '|'.join(photo_list)

def getMessageContent(update: Update):
    """判断是否为编辑的消息, 返回消息内容"""

    is_edit = bool(update.edited_message)
    message: Message = update.edited_message if is_edit else update.message

    return message, is_edit
