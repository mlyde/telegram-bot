from utils.log import setup_logging
setup_logging()
import logging
logger = logging.getLogger(__name__)
import time

from telegram import Update
from telegram.error import NetworkError
from telegram.ext import (
    Application, AIORateLimiter, Defaults,
    CommandHandler, MessageHandler, CallbackQueryHandler, ChatMemberHandler, MessageReactionHandler,
    filters, ConversationHandler,
)
from handle import error_handle
from handle.command_handle import (
    startArgsCommand,
    helpCommand,
    uptimeCommand,
    banCommand,
    muteCommand
)
from handle.conversation_handle import (
    exitCaptcha, handle_answer,
    CAPTCHA_QUESTION, ANSWER
)
from handle.message_handle import (
    forwardedHandleMessage,
    textHandleMessage,
    photoHandleMessage,
    audioHandleMessage,
    voiceHandleMessage,
    storyHandleMessage,
    stickerHandleMessage,
    documentHandleMessage,
    videoHandleMessage,
    videoNoteHandleMessage,
    locationHandleMessage,
    lastHandleMessage,
)
from handle.other_handle import otherCommand
from handle.reaction_handle import reactionHandle
from handle.member_handle import chatMemberHandle
from handle.callback_handle import callbackHandle
from core.static_config import static_config
from utils.time import last_start_up_time, DEFAULT_TIMEZONE
TOKEN = static_config.get("token")
PROXY = static_config.get("proxy")
DEFAULTS = Defaults(
    tzinfo=DEFAULT_TIMEZONE,  # 设置默认时区
)

def main(drop_pending_updates=False) -> None:

    # Create the Application
    app = (Application.builder().token(TOKEN)
        .get_updates_proxy(PROXY).proxy(PROXY)
        .rate_limiter(AIORateLimiter(max_retries=5))        # 最大失败请求重试次数
        .get_updates_read_timeout(30).read_timeout(30)      # 等待 Telegram 服务器响应的最长时间
        .get_updates_write_timeout(30).write_timeout(30)    # 等待写入操作 (上传文件) 完成的最长时间
        .get_updates_connect_timeout(20).connect_timeout(20)# 尝试连接到 Telegram 服务器的最长时间
        .get_updates_pool_timeout(30).pool_timeout(30)      # 连接从连接池中变为可用的最长时间
        .get_updates_connection_pool_size(16).connection_pool_size(16)  # 连接池维护的最大活跃连接数
        .get_updates_http_version("2.0").http_version("2.0")
        .defaults(DEFAULTS)
        .build()
    )

    # Commands
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", startArgsCommand, filters.ChatType.PRIVATE)],
        states={CAPTCHA_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer, filters.ChatType.PRIVATE)]},
        fallbacks=[MessageHandler(filters.ALL, exitCaptcha)],
        conversation_timeout=180  # 超时秒数
    )
    app.add_handler(conversation_handler)
    # app.add_handler(CommandHandler("start", startCommand, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("uptime", uptimeCommand, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("help", helpCommand, filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("ban", banCommand, filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("mute", muteCommand, filters.ChatType.GROUPS))
    # app.add_handler(CommandHandler("captcha", captchaCommand, filters.ChatType.GROUPS))
    app.add_handler(MessageHandler(filters.COMMAND & filters.ChatType.PRIVATE, otherCommand))
    # Message
    app.add_handler(MessageHandler(filters.FORWARDED, forwardedHandleMessage))
    app.add_handler(MessageHandler(filters.TEXT, textHandleMessage))
    app.add_handler(MessageHandler(filters.PHOTO, photoHandleMessage))
    app.add_handler(MessageHandler(filters.AUDIO, audioHandleMessage))
    app.add_handler(MessageHandler(filters.VOICE, voiceHandleMessage))
    app.add_handler(MessageHandler(filters.STORY, storyHandleMessage))
    app.add_handler(MessageHandler(filters.VIDEO, videoHandleMessage))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE, videoNoteHandleMessage))
    app.add_handler(MessageHandler(filters.LOCATION, locationHandleMessage))
    app.add_handler(MessageHandler(filters.Sticker.ALL, stickerHandleMessage))
    app.add_handler(MessageHandler(filters.Document.ALL, documentHandleMessage))
    app.add_handler(MessageHandler(filters.ALL, lastHandleMessage))     # 未被匹配的消息
    # app.add_handler(MessageHandler(filters.Regex("^Something else...$"), handleTextMessage))  # 捕获特定文本
    # app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS & filters.ChatType.GROUPS, chatMemberHandle))  # 群内入群消息提示
    # Reaction
    app.add_handler(MessageReactionHandler(reactionHandle))
    # ChatMember
    app.add_handler(ChatMemberHandler(chatMemberHandle, ChatMemberHandler.CHAT_MEMBER))
    # CallbackQuery
    app.add_handler(CallbackQueryHandler(callbackHandle))
    # Error
    app.add_error_handler(error_handle.errorHandle)

    # Run
    logger.info("run polling...")
    app.run_polling(
        poll_interval=6,            # 拉取消息的间隔, s
        bootstrap_retries=-1,       # 启动阶段自动重试
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=drop_pending_updates,
        close_loop=True
    )

if __name__ == "__main__":

    while True:
        try:
            last_start_up_time.update()
            main()
        except (KeyboardInterrupt):
            logger.info("exit.")
            break
        except Exception as e:
            logger.critical(f"{e}")
            time.sleep(10)
