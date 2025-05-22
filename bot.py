import re
import datetime
import json
import logging
from logging.handlers import RotatingFileHandler
import random
import os
import time
import asyncio
import traceback
import hashlib
from config import BotConfig
# pip install "python-telegram-bot[http2]==21.4"
# 官方文档: https://docs.python-telegram-bot.org/en/v21.4/index.html
# wiki: https://github.com/python-telegram-bot/python-telegram-bot/wiki/
from telegram import Update, ChatFullInfo, Chat, StickerSet, MessageOrigin, User, Sticker   # 变量注释
from telegram import BotCommand, BotCommandScopeAllPrivateChats, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, ForceReply, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.constants import ChatType, ParseMode, ChatMemberStatus
from telegram.ext import ContextTypes, Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ChatMemberHandler, CallbackContext, ConversationHandler, MessageReactionHandler
# from telegram.error import 

PROXY = "http://127.0.0.1:1234/"
FLOADER = "/home/ml/Downloads/TelegramBot"

# 存放编译后的正则
patterns = {}

log_format = "%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Logging setup 总日志, 包含调用的其他文件的日志
logging.basicConfig(
    format=log_format,
    datefmt=date_format,
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),             # 将日志输出到终端
        # logging.FileHandler(filename=f"{FLOADER}/bot_ALL.log", encoding="utf-8"),    # 将日志写入文件
        RotatingFileHandler(f"{FLOADER}/bot_ALL.log", maxBytes=32*1024*1024, backupCount=8, encoding="utf-8"),
    ]
)

# 当前文件的自定义 log
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# 将日志消息记录到文件中
main_file_handle = RotatingFileHandler(f"{FLOADER}/bot_mainlog.log", maxBytes=16*1024*1024, backupCount=4, encoding="utf-8")
# main_file_handle = logging.FileHandler(filename=f"{FLOADER}/bot_mainlog.log", encoding="utf-8")
formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
main_file_handle.setFormatter(formatter)
logger.addHandler(main_file_handle)
logger.info("logger started.")

# Function
def compilePatterns():
    """ 编译 pattern, 加快搜索速度 """

    global patterns
    patterns["massage"] = re.compile('|'.join(config["blocked_words"]["message"]), flags=re.IGNORECASE|re.DOTALL)
    patterns["username"] = re.compile('|'.join(config["blocked_words"]["username"]), flags=re.IGNORECASE|re.DOTALL)
    patterns["bio"] = re.compile('|'.join(config["blocked_words"]["bio"]), flags=re.IGNORECASE|re.DOTALL)
    patterns["userid"] = re.compile('|'.join(config["blocked_words"]["userid"]), flags=re.IGNORECASE|re.DOTALL)
    patterns["chatname"] = re.compile('|'.join(config["blocked_words"]["chatname"]), flags=re.IGNORECASE|re.DOTALL)
    patterns["button"] = re.compile('|'.join(config["blocked_words"]["button"]), flags=re.IGNORECASE|re.DOTALL)
    logger.info("正则表达式 pattern 编译完成")

def checkBlockList():
    """ 简单检查屏蔽词列表是否有效或范围过大, 正则很难进行完全测试, 就这样了吧 """

    if any(containBlockedWords("1Ab谢谢学习资源", pattern) for pattern in patterns.values()):
        logger.error("屏蔽词匹配到正常文本, 请检查屏蔽词列表")
        raise Exception
    elif any(containBlockedWords("SM俱乐部", pattern) for pattern in patterns.values()):
        logger.debug("屏蔽词匹配正常")

def findBlockListSource(text: str):
    """ 在原始屏蔽词列表中查找哪条规则匹配成功, 可用于排查错误 """

    tmp_list: list[list[str]] = [dic for dic in config.get("blocked_words")]

    for li in tmp_list:
        for i in li:
            if re.findall(i, text):
                yield i

async def stopLoop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 停止 event loop """

    logger.info("Bot is stoping...")

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.stop()  # 暂停 loop
        loop.close() # 关闭 loop

    # 停止 application
    # await context.application.stop()    # 立即停止
    await context.application.shutdown() # 等待进行的任务完成后停止
    # sys.exit(1)   # 终止当前程序

async def removeDeleteAccount(context: ContextTypes.DEFAULT_TYPE, chat_id: str | int):
    """ 移除群组的 delete account 账户    未实现!!! """

    administrators = await context.bot.get_chat_administrators(chat_id)
    member_count = await context.bot.get_chat_member_count(chat_id)
    members: list[User] = []
    try:
        n = 0
        for user in members:
            if user.status == "Delete Account":
                await context.bot.ban_chat_member(chat_id, user.id, until_date=0)  # 移除用户, 不封禁
                logger.debug(f"已移除 Delete Account ({user.id})")
                n += 1
    finally:
        logger.info(f"已移除{n}个已注销账户")

async def messageExist(context: ContextTypes.DEFAULT_TYPE, chat_id, message_id):
    """检测一条消息是否存在    未实现!!!"""

    # 通过尝试转发消息判断消息是否存在
    response = await context.bot.forward_message(chat_id=-1001226170027, from_chat_id=-1001226170027, message_id=21834)
    return True
    return False

def getUser3Info(user: User) -> str:
    """ 返回 user 的 用户名+自定义id+数字id """

    name = user.full_name if hasattr(user, "full_name") else ''
    link = user.username if hasattr(user, "username") else '' if user.username else ''
    return f"({name})(@{link})({user.id})"

def getChat3Info(chat: Chat) -> str:
    """ 返回 chat 的 群聊名+自定义id+数字id """

    name = chat.effective_name if hasattr(chat, "effective_name") else ''
    link = chat.username if hasattr(chat, "username") else '' if chat.username else ''
    return f"({name})(@{link})({chat.id})"

def getSticker3Info(sticker: Sticker) -> str:
    """ 返回贴纸的 贴纸表情emoji+贴纸id+贴纸包名 """

    return f"({sticker.emoji})({sticker.file_id})({sticker.set_name})"

def getMD5(id: int) -> str:
    """获取数字的 md5"""

    return hashlib.md5(str(id).encode('utf-8')).hexdigest()

async def getEmojiStickers(update: Update, context: ContextTypes.DEFAULT_TYPE, emoji_id: str):

    sticker_set = await context.bot.getCustomEmojiStickers(["emoji_id"])
    getSticker3Info(sticker_set)
    return sticker_set

async def retryAwait(update: Update, context: ContextTypes.DEFAULT_TYPE, func, exception_type=Exception, message: str='', retries: int=5, delay: int=4):
    """ 自动重试函数 使用方法: 
    await retryAwait(update, context, lambda: update.message.reply_text("Hello!"))
    await retryAwait(update, context, lambda: ...) """

    for _ in range(retries):
        try:
            return await func()
        except Exception as e:
            logger.error(e)
            if e.message in {'Message to delete not found', "Can't remove chat owner"}: # 或者如何获取 statue code ?
                return
            else:
                logger.error(update.message)
            await asyncio.sleep(delay)
    raise Exception("Max retries exceeded")

async def changePermission(update: Update, context: ContextTypes.DEFAULT_TYPE, permission: bool):
    """ 给予或禁止权限 """

    chat = update.message.chat
    user = update.message.from_user

    whether = bool(permission)
    all_permissions = ChatPermissions(
        can_send_messages = whether,
        can_send_polls = whether,
        can_send_other_messages = whether,
        can_add_web_page_previews = whether,
        can_change_info = whether,
        can_invite_users = whether,
        can_pin_messages = whether,
        can_manage_topics = whether,
        can_send_audios = whether,
        can_send_documents = whether,
        can_send_photos = whether,
        can_send_videos = whether,
        can_send_video_notes = whether,
        can_send_voice_notes = whether,
    )

    await context.bot.restrict_chat_member(chat.id, user.id, all_permissions)
    if whether:
        logger.info(f"已给予 {getUser3Info(user)} 在 {getChat3Info(chat)} 的权限")
    else:
        logger.info(f"已禁止 {getUser3Info(user)} 在 {getChat3Info(chat)} 的权限")

def containBlockedWords(text: str, pattern: re.Pattern) -> bool:
    """ 判断文本中是否包含屏蔽词, 含有则返回 True """

    if text:
        # 去除部分 除空格外 的空字符和 .
        text = re.sub(r"[.\t\n\r\f\v()]", '', text) 
        if text:
            match = pattern.search(text)
            return bool(match)
    return False

def containBlockedEmojiId(emoji_id: str, blocked_emoji_dict: dict[str, list[str]]) -> bool:
    """ 是否在屏蔽会员表情中 """
    return any(emoji_id in li  for li in blocked_emoji_dict.values())

def containBlockedEmojiHtml(message_html: str, blocked_emoji_dict: dict[str, list[str]]) -> bool:
    """ 判断是否包含屏蔽会员表情, 含有则返回 True """

    emoji_ids = re.findall("<tg-emoji emoji-id=\"([0-9]{19})\">(?:.*?)</tg-emoji>", message_html)
    if emoji_ids:
        return any(any(emoji_id in li  for li in blocked_emoji_dict.values())  for emoji_id in emoji_ids)
    return False

def choiceOne(num: int=None) -> str:
    """ 根据不同概率返回内容 """

    options = ['_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n']
    weights_normal = [399, 388, 359, 314, 261, 205, 153, 108, 73, 46, 28, 16, 9, 4, 1]      # 正态分布, 数字和为 2364
    return random.choices(options, weights_normal)[0]

def is_md5(string: str) -> bool:
    """使用正则表达式检查是否为32位的16进制字符串, md5格式"""
    pattern = re.compile(r'^[a-fA-F0-9]{32}$')
    return bool(pattern.match(string))

async def send_stream_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, time: int | float=0):
    """ 实现在同一消息中更改变化内容 """

    logger.debug('test edit message send')
    message = await update.message.reply_text("正在查询...")
    logger.debug(message.id)
    await asyncio.sleep(3)
    await message.edit_text("查询完毕, 正在处理...")
    await asyncio.sleep(3)
    await message.edit_text("完成.")
    await asyncio.sleep(6)
    await message.delete()

async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 一些发送图片的方法 """

    # 发送一张本地图片
    # with open("/home/mlyder/Downloads/out.jpg", 'rb') as f:
    #     await update.message.reply_photo(photo=f)
    # await update.message.reply_photo(photo=open("/home/mlyder/Downloads/out.jpg", 'rb'))

    # 发送一张网络图片
    await update.message.reply_photo(photo="https://www.baidu.com/favicon.ico")

    # media = [
    #     InputMediaPhoto(open("/home/mlyder/Downloads/out.jpg", 'rb')),
    #     InputMediaPhoto("https://www.baidu.com/favicon.ico")
    # ]
    # 发送多张图片
    # await update.message.reply_media_group(media=media)

async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 发送音频 """

    # await context.bot.send_audio(list(config["admin"].keys())[0], audio=open(f"{FLOADER}/考试什么的都去死吧.mp3", 'rb'))
    await update.message.reply_audio(audio=open(f"{FLOADER}/考试什么的都去死吧.mp3", 'rb'))

async def send_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 发送语音 """

async def send_reply_markup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ reply_markup, 为消息添加按钮, 添加按钮键盘, 要求回复指定消息 """

    button1 = InlineKeyboardButton("Option 1", callback_data="option1")
    button2 = InlineKeyboardButton("Option 2", callback_data="option2")
    reply_markup = InlineKeyboardMarkup([[button1, button2]])

    # 发送带有按钮的消息
    await context.bot.send_message(update.message.chat_id, text="Please choose an option:", reply_markup=reply_markup)

    # 不太好用, 如何删除键盘是个问题
    # button1 = KeyboardButton("按钮1")
    # button2 = KeyboardButton("按钮2")
    # reply_markup = ReplyKeyboardMarkup([[button1, button2]], resize_keyboard=True, one_time_keyboard=True)
    # # 创建键盘按钮
    # await update.message.reply_text("请选择一个选项：", reply_markup=reply_markup)

    # 自动选中本条消息要求用户回复
    # await update.message.reply_text("请输入一些文本：",reply_markup=ForceReply(selective=False))

async def resetBotCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 设置 bot 命令提示列表 """

    logger.debug("删除 bot 命令提示")
    await context.bot.delete_my_commands()
    commands_user = [
        BotCommand("start", "Start this dialogue and initialization"),
        BotCommand("uptime", 'Uptime'),
        BotCommand("help", "Provides help for this bot")
    ]
    logger.debug("设置 bot 命令提示")
    return await context.bot.set_my_commands(commands_user, scope=BotCommandScopeAllPrivateChats())

def editEmojiId(emoji_name, sticker_set: StickerSet=None):

    global config
    if sticker_set:
        config["premium_blocked_emoji"][emoji_name] = [sticker.custom_emoji_id for sticker in sticker_set.stickers]
    else:
        del config["premium_blocked_emoji"][emoji_name]

async def flashEmojisId(context: ContextTypes.DEFAULT_TYPE):
    """ 重新获取 premium_blocked_emoji 表情包中表情的 id 列表 """

    global config
    try:
        for emoji_name in config["premium_blocked_emoji"]:
            logger.info(f"获取{emoji_name}表情包")
            sticker_set = await context.bot.get_sticker_set(emoji_name)
            editEmojiId(emoji_name, sticker_set)
        bot_config.save()
    except TimeoutError:
        logger.error("获取表情包超时")

async def addEmojisId(context: ContextTypes.DEFAULT_TYPE, emoji_name: str, force=False):
    """ 添加 emoji_name 表情包的 id 列表, 添加至 premium_blocked_emoji """

    global config
    if emoji_name in config["premium_blocked_emoji"] and not force:
        logger.info(f"表情包{emoji_name}已在列表中")
    else:
        sticker_set = await context.bot.get_sticker_set(emoji_name)
        editEmojiId(emoji_name, sticker_set)
        logger.info(f"表情包{emoji_name}添加完成")
        bot_config.save()

# Commands
async def startCommand(update: Update, context: CallbackContext):

    message = update.message
    args = context.args # https://t.me/xxxbot?start=parameter 好像只能收到一个参数
    logger.info(f"/start {''.join(args)} from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")

    if message.chat.type != ChatType.PRIVATE:
        logger.debug("删除 /start 消息")
        await message.delete()    # 删除消息, 防止其他人跟着点
        return     # 只回复私聊

    # if is_md5(args[0]):   # 先判断为md5, 再具体判断可能会更快?
    if args[0] == getMD5(message.chat.id):
        await message.reply_text("captcha")
        return

    today = datetime.datetime.now().date()
    if today.month == 4 and today.day == 1:     # 愚人节彩蛋
        await message.reply_text("418 I'm a teapot", reply_markup=ReplyKeyboardRemove())
        return

    choice = choiceOne()
    match choice:
        case 'g':
            await message.reply_text("Let's get started.", reply_markup=ReplyKeyboardRemove())
        case 'h':
            await message.reply_sticker(sticker='CAACAgUAAxkBAAICBGaThaP_3NPC0J301sJxAkwv81wZAAKNCQACCYSJVmS11JMf6Da9NQQ')   # 贴纸内容: 柴郡头猫猫趴在西瓜上
        case 'i':
            await message.reply_text("emm, may I help you?", reply_markup=ReplyKeyboardRemove())
        case _:
            # await message.reply_text("Hello! I am a bot. A new bot. ^_^", reply_markup=ReplyKeyboardRemove())
            await message.reply_text("Hello! I am a bot. <b>^_^</b>", reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)

async def uptimeCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    logger.info(f"/uptime from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")
    text = "已运行时间: %.1f" % (time.time() - start_time)
    logger.info(text)
    await message.reply_text(text)
    # logger.info(datetime.datetime.now(datetime.timezone.utc).astimezone(utc_time_zone))   # 当前 UTC 时间

async def captchaCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message:
        message = update.message
    else:
        # 若编辑消息后的命令
        message = update.edited_message
    args = context.args
    logger.info(f"/captcha from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")

    if str(message.from_user.id) in config["admin"]:

        if message.reply_to_message.from_user:
            # 标记的用户的 id
            message.reply_to_message.from_user.id
            logger.debug(f"{getUser3Info(message.from_user)} 使用 /captcha 标记了 {getUser3Info(message.reply_to_message.from_user)}")
            user_id_md5 = getMD5(message.reply_to_message.from_user.id)
            # 记下message id, 完成验证后删除消息
            captcha_ask = await context.bot.send_message(chat_id=message.chat.id,
                                           text="用户已被标记, 请在下次发出消息前完成验证",
                                           reply_to_message_id=message.reply_to_message.id,
                                           reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("去验证",
                                                                                                    callback_data=f"captcha_{user_id_md5}",
                                                                                                    url=f"https://t.me/{context.bot.username}?start={user_id_md5}")]])
                                           )
            logger.debug(f"验证消息id: {captcha_ask.id}, 被标记消息id: {message.reply_to_message.id}")
            await message.delete()

    if args:
        print(args)
    if message.chat.type == ChatType.PRIVATE:
        message.reply_text("验证")


async def otherCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 一些可能不长期使用的测试临时命令 """

    if hasattr(update, "message"):
        message = update.message
    else:
        logger.debug("unknown message")
        logger.debug(update) 
        return
    text = message.text
    # logger.debug(f"{text} from {message.chat.full_name}")
    logger.info(f"receive command({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: {text}")

    # 分离命令和参数
    command: str; arg: str
    command, arg = re.findall("^/(\w+)\s*(.*)$", text)[0]
    if str(message.from_user.id) in config["admin"]:
        match command:
            case "re": # 转义正则中的特殊字符
                logger.info(re.escape(arg))
    else:
        await message.reply_text("unknown command")

async def unbanCommand(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.chat.type != ChatType.PRIVATE: return     # 只回复私聊
    chat_id: int = config["active_groups"][0]    # 我的群

    admins = await context.bot.get_chat_administrators(chat_id)
    if any(admin.user.id == context.bot.id for admin in admins):    # bot 是管理员
        member = await context.bot.get_chat_member(chat_id, update.message.from_user.id)
        if member.status == ChatMemberStatus.BANNED:        # 用户已被ban
            if await context.bot.unban_chat_member(chat_id, update.message.from_user.id):
                await update.message.reply_text("已解除禁言, 你可以再次加入群组了!")
                logger.info(f"解除禁言: {update.message.from_user.full_name}")
        else:
            await update.message.reply_text("You're not on the ban list!")
    else:
        await update.message.reply_text("I can't unban for you!")

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
            await retryAwait(update, context, lambda: message.delete())
        return

    message_type: str = message.chat.type
    text: str = message.text
    reply_markup: InlineKeyboardMarkup = message.reply_markup

    if edit:
        logger.info(f"receive edit text({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: {text}")    # 在消息上recation也会触发
    else:
        logger.info(f"receive text({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: {text}")

    if message_type in {ChatType.GROUP, ChatType.SUPERGROUP}:
        if message.chat.id in config["active_groups"]:
            # 违禁词或违禁会员表情
            if containBlockedWords(text, patterns["massage"]) or containBlockedEmojiHtml(message.text_html, config["premium_blocked_emoji"]):
                logger.debug(f"删除消息 {message.id}")
                await retryAwait(update, context, lambda: message.delete())
                # await changePermission(update, context, False)
                logger.debug(f"ban {getUser3Info(message.from_user)}")
                await retryAwait(update, context, lambda: context.bot.ban_chat_member(message.chat_id, message.from_user.id))
                return

    elif str(update.message.from_user.id) in config["admin"]:
        # 将管理员发给 bot 的内容做屏蔽词检测, 全匹配
        text = update.message.text
        logger.info(text)

        t = []
        for key, value in patterns.items():
            if containBlockedWords(text, value):
                t.append(key)
        if t:
            logger.debug(t)
            await retryAwait(update, context, lambda: update.message.reply_text(f"列表 {','.join(t)} 匹配成功"))
        else:
            await update.message.reply_text("不含屏蔽词")

async def photoHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if not message:
        logger.debug(update)
    message_type: str = message.chat.type
    caption: str = message.caption  # 图片的说明文字

    # logger.info(f"receive picture({message.id}) { "with caption " if caption else '' }from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")
    if caption:
        logger.info(f"receive picture({message.id}) with caption from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: {caption}")
    else:
        logger.info(f"receive picture({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")

    if str(update.message.from_user.id) in config["admin"]:
        photo_id: str = update.message.photo[-1].file_id    # -1 为最大尺寸图片

        # 保存图片
        file = await context.bot.get_file(photo_id)
        await file.download_to_drive(f"{FLOADER}/{file.file_unique_id}_{file.file_path.split('/')[-1]}")
        logger.info("picture saved")

    # attachment: list = update.message.effective_attachment    # 附件

async def videoHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    caption = message.caption
    if caption:
        logger.info(f"receive video({message.id}) from with caption {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: {caption}")
    else:
        logger.info(f"receive video({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")

    if str(message.from_user.id) in config["admin"]:
        video_id: str = message.video.file_id    # -1 为最大尺寸
        # 保存视频
        file = await context.bot.get_file(video_id)
        await file.download_to_drive(f"{FLOADER}/{file.file_unique_id}_{file.file_path.split('/')[-1]}")
        logger.info("video saved")

async def documentHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    logger.info(f"receive document({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: {message.effective_attachment.file_name}")
    if message.chat.type != ChatType.PRIVATE: return # 只回复私聊

async def stickerHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    if message is None: return  # 什么时候?, 对消息reaction 好像会产生编辑空消息

    if message.chat.type != ChatType.PRIVATE: return # 只回复私聊

    # sticker_set = await context.bot.get_sticker_set(message.sticker.set_name) # 贴纸包详细内容

    logger.info(f"receive sticker({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: {getSticker3Info(message.sticker)} from {getChat3Info(message.chat)}")
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
        logger.info(f"receive audio({message.id}) with \"{caption}\" caption from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: ({message.audio.title})({message.audio.file_name})")
    else:
        if message.chat.id == message.from_user.id:
            logger.info(f"receive audio({message.id}) from {getUser3Info(message.from_user)} at {message.date.astimezone(utc_time_zone)}: ({message.audio.title})({message.audio.performer})({message.audio.file_name})")
        else:
            logger.info(f"receive audio({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}: ({message.audio.title})({message.audio.performer})({message.audio.file_name})")

async def voiceHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 语音消息 """
    message = update.message
    logger.info(f"receive voice({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")
    logger.debug(message)

async def storyHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    logger.info(f"received story({message.id}) from {getUser3Info(message.story.chat)} forwarded by {getUser3Info(message.from_user)} at {message.date.astimezone(utc_time_zone)}")
    logger.debug(message)

async def locationHandleMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.message
    logger.info(f"receive location({message.id}) from {getUser3Info(message.from_user)} in {getChat3Info(message.chat)} at {message.date.astimezone(utc_time_zone)}")
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
            if containBlockedWords(text, patterns["button"]):
                logger.debug("删除消息")
                await retryAwait(update, context, lambda: message.delete())
                logger.debug(f"ban {getUser3Info(message.from_user)}")
                await retryAwait(update, context, lambda: context.bot.ban_chat_member(message.chat_id, message.from_user.id))
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
        'video_note': None,
    }

    for message_type, handler in message_handlers.items():
        if getattr(message, message_type):
            logger.info(f"{message_type} type of forwarded message({message.id}) from ({name})({id})")
            if handler: await handler(update, context)
            break
    else:
        logger.info(f"unknown types of forwarded message from ({name})({id})")
        logger.debug(message)

# Reaction
async def __reactionHandle(update: Update, context: CallbackContext):
    """ 处理消息的 reaction 事件 """

    reaction = update.message_reaction
    logger.info(f"Reaction {reaction.new_reaction} from {getUser3Info(reaction.user)} in {getChat3Info(reaction.chat)} for message({reaction.message_id}) at {reaction.date.astimezone(utc_time_zone)}.")

# ChatMember
async def chatMemberHandle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ 新成员加入时, 对名字\简介进行屏蔽词检测 """

    def log_status_different(middle_message: str):
        """ 大致相同格式的成员状态信息 """
        logger.info(f"{getUser3Info(user)} {middle_message} by {getUser3Info(chat_member.from_user)} in {getChat3Info(chat)} at {chat_member.date.astimezone(utc_time_zone)}.")

    chat = update.effective_chat
    chat_member = update.chat_member
    user = chat_member.new_chat_member.user

    # old_member_status, new_member_status = chat_member.difference().get("status", (None, None)) # _chat_member.status 不一样时取出
    old_member_status, new_member_status = chat_member.old_chat_member.status, chat_member.new_chat_member.status
    if (old_member_status == new_member_status):
        logger.debug(f"{getUser3Info(user)}member status unchange, still is '{old_member_status}'")
        return
    else:
        logger.debug(f"{getUser3Info(user)}member status changed from '{old_member_status}' to '{new_member_status}'")

    match new_member_status:    # 先判断状态变为了什么, 再判断之前是什么
        case ChatMemberStatus.BANNED:       log_status_different("has been banned")
        case ChatMemberStatus.RESTRICTED:   log_status_different("has been restricted")
        case ChatMemberStatus.ADMINISTRATOR:log_status_different("is the administrator")
        case ChatMemberStatus.OWNER:        log_status_different("is owner")
        case ChatMemberStatus.LEFT:
            match old_member_status:
                case ChatMemberStatus.BANNED:log_status_different("has been unbanned")
                case _:                      log_status_different("left")
        case ChatMemberStatus.MEMBER:
            match old_member_status:
                case ChatMemberStatus.ADMINISTRATOR:log_status_different("is no longer be administrator")
                case ChatMemberStatus.RESTRICTED:   log_status_different("was no longer restricted")
                case ChatMemberStatus.OWNER:        log_status_different("is no longer the owner")
                case _: # 为新成员
                    log_status_different("is a member")
                    # 名字违禁
                    if containBlockedWords(user.full_name, patterns["username"]) or containBlockedWords(user.first_name, patterns["username"]) or containBlockedWords(user.username, patterns["userid"]):
                        logger.debug(f"ban {getUser3Info(user)}")
                        await retryAwait(update, context, lambda: context.bot.ban_chat_member(chat.id, user.id))
                    # 名字的表情 或 主页中挂的群 或 简介违禁
                    user_chat: ChatFullInfo = await retryAwait(update, context, lambda: context.bot.get_chat(user.id))
                    logger.debug(user_chat)
                    if containBlockedWords(user_chat.bio, patterns["bio"]) or containBlockedWords(user_chat.effective_name, patterns["chatname"]) \
                        or (containBlockedEmojiId(user_chat.emoji_status_custom_emoji_id, config["premium_blocked_emoji"]) if hasattr(user_chat, "emoji_status_custom_emoji_id") else False):
                        logger.debug(f"ban {getUser3Info(user)}")
                        await retryAwait(update, context, lambda: context.bot.ban_chat_member(chat.id, user.id))
        case _:
            logger.warning("unknown member status!")

# Callback
async def callbackHandle(update: Update, context: CallbackContext | ContextTypes.DEFAULT_TYPE):
    """ 消息下的按钮 点击事件 """

    query = update.callback_query
    message = query.message
    data = query.data

    button1 = InlineKeyboardButton("Option 2", callback_data="option2")
    reply_markup = InlineKeyboardMarkup([[button1]])

    if data == "option1":
        # await context.bot.send_message(chat_id=message.chat_id, text="You chose Option 1!")
        logger.debug("更改按钮键盘")
        await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='You chose Option 1!', reply_markup=reply_markup)
    elif data == "option2":
        # 更新消息的内联键盘
        # await context.bot.edit_message_reply_markup(chat_id=message.chat_id, message_id=message.message_id, reply_markup=None)
        logger.debug("更改按钮键盘")
        await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='You chose Option 2!', reply_markup=None)

    # 标记验证 回复消息
    if data[:8] == "captcha_":
        logger.debug("验证按钮被按下")

        # 确保按钮点击后的动画被终止
        query = update.callback_query
        await query.answer("1")

        # await context.bot.edit_message_text(chat_id=message.chat_id, message_id=message.message_id, text='需要验证', reply_markup=message.reply_markup)
        # await context.bot.edit_message_reply_markup




# Error
async def errorHandle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.error(f"custom error handler catch: {context.error}")

    # isinstance() 不好用, telegram.error封装了, 没法具体判断, 先改用判断字符串的方式吧
    # httpx.connectError 不一定导致卡住, 由 Updater 抛出时捕获不到
    # 不重启解决不了的
    errors_restart = ["httpx.PoolTimeout", "httpx.LocalProtocolError", "SSLError", "httpx.ConnectError"]
    # 不影响轮询的
    errors_continue = ["httpx.ReadError", "httpx.RemoteProtocolError"]

    if any(error in str(context.error) for error in errors_restart):
        # 详细错误信息
        # tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        # logger.error(f"\n%s", "".join(tb_list))

        # 重启 updater
        logger.info("restarting updater...")
        if context.application.updater.running:
            await context.application.updater.stop()
        await context.application.updater.start_polling()
        logger.info("restarted updater.")

    elif any(error in str(context.error) for error in errors_continue):
        ... # 已知错误不显示详细信息
    else:
        # 未知错误显示详细错误信息
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        logger.error(f"\n%s", "".join(tb_list))

def main(timeout=1):

    # Create the Application, 尝试解决超时, 未果
    app = (Application.builder().token(config["token"])
        .get_updates_proxy(PROXY).proxy(PROXY)
        .get_updates_read_timeout(timeout*5).read_timeout(timeout*5)    # 等待 Telegram 服务器响应的最长时间
        .get_updates_write_timeout(timeout*5).write_timeout(timeout*5)      # 等待写入操作(POST, 上传文件)完成的最长时间
        .get_updates_connect_timeout(timeout*5).connect_timeout(timeout*5)  # 尝试连接到 Telegram 服务器的最长时间
        .get_updates_pool_timeout(timeout).pool_timeout(timeout)    # 连接从连接池中变为可用的最长时间
        .get_updates_connection_pool_size(4).connection_pool_size(512)
        .get_updates_http_version("2.0").http_version("2.0")
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start", startCommand))
    app.add_handler(CommandHandler("uptime", uptimeCommand, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("captcha", captchaCommand))
    app.add_handler(MessageHandler(filters.COMMAND & filters.ChatType.PRIVATE, otherCommand))
    # Message
    app.add_handler(MessageHandler(filters.FORWARDED, forwardedHandleMessage))
    app.add_handler(MessageHandler(filters.TEXT, textHandleMessage))
    app.add_handler(MessageHandler(filters.PHOTO, photoHandleMessage))
    app.add_handler(MessageHandler(filters.AUDIO, audioHandleMessage))
    app.add_handler(MessageHandler(filters.VOICE, voiceHandleMessage))
    app.add_handler(MessageHandler(filters.STORY, storyHandleMessage))
    app.add_handler(MessageHandler(filters.Sticker.ALL, stickerHandleMessage))
    app.add_handler(MessageHandler(filters.Document.ALL, documentHandleMessage))
    # app.add_handler(MessageHandler(filters.Regex("^Something else...$"), HandleMessage))  # 捕获特定文本
    # app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS & filters.ChatType.GROUPS, chatMemberHandle))  # 只有群内有入群消息提示时有用
    # Reaction
    app.add_handler(MessageReactionHandler(__reactionHandle))
    # ChatMember
    app.add_handler(ChatMemberHandler(chatMemberHandle, ChatMemberHandler.CHAT_MEMBER))
    # CallbackQuery
    app.add_handler(CallbackQueryHandler(callbackHandle))
    # Error
    app.add_error_handler(errorHandle)
    # Run
    logger.info("run polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=6, drop_pending_updates=False)    # 每 3 秒拉取信息


if __name__ == "__main__":

    utc_time_zone = datetime.timezone(datetime.timedelta(hours=8)) # 设置当前 UTC 时区

    bot_config = BotConfig(FLOADER)
    bot_config.load()

    global config; config = bot_config.config_dict  # 引用同一个字典对象, 会同时改变
    compilePatterns()
    checkBlockList()

    while True:
        try:
            start_time = time.time()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run(main(2))
            logger.warning("It shouldn't be running here.")
            break
        except (KeyboardInterrupt, ValueError):
            bot_config.merge()
            break
        except Exception as e:
            logger.critical(f"__main__ 遇到 {e}")
            time.sleep(16)

