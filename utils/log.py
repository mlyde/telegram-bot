"""配置基本日志参数"""
import os
from pathlib import Path
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler

from core.static_config import static_config
OTHER_LEVEL = logging.WARNING
bot_level = static_config.get("level")
BOT_LEVEL = logging._nameToLevel.get(bot_level)


def getLoggerConfig(filename: str, level=logging.DEBUG, max_bytes=32*1024*1024, backupCount=1) -> dict:
    """生成 logger 配置"""
    return {
        "level": level,
        "handlers": [
            RotatingFileHandler(
                filename=filename,
                maxBytes=max_bytes,
                backupCount=backupCount,
                encoding="utf-8"
            )
        ]
    }

def rootLogging(file_path, log_format: str, date_format: str, level=logging.DEBUG, max_bytes=32*1024*1024, backupCount=8):
    """根日志配置 (全局继承)"""

    # ================ 方法 1 ================
    # root_logger = logging.getLogger()
    # root_logger.setLevel(log_level)

    # # 统一处理器配置
    # handlers = [
    #     # 终端输出
    #     logging.StreamHandler(),
    #     # 日志文件, 32 MB * 8
    #     RotatingFileHandler(filename=log_path / "_all.log", maxBytes=32*1024*1024, backupCount=8, encoding="utf-8")
    # ]

    # # 应用处理器
    # for handler in handlers:
    #     handler.setFormatter(formatter)
    #     root_logger.addHandler(handler)

    # ================ 方法 2 ================
    # 手动配置根记录器配置, basicConfig 可防止重复配置 (仅在根记录器无处理器时生效)
    logging.basicConfig(
        format=log_format,
        datefmt=date_format,
        level=level,
        handlers=[
            logging.StreamHandler(),# 日志输出到终端
            RotatingFileHandler(    # 日志写入到文件
                file_path / "_all.log",
                maxBytes=max_bytes,
                backupCount=backupCount,
                encoding="utf-8"
            ),
        ]
    )

def fileLogging(files_path, formatter: Formatter, level = logging.DEBUG):
    """记录不同日志文件"""

    logger_default = getLoggerConfig(filename=files_path / "bot.log", level=level)
    logger_message = getLoggerConfig(filename=files_path / "message.log", level=level)
    logger_member  = getLoggerConfig(filename=files_path / "member.log", level=level)
    logger_error   = getLoggerConfig(filename=files_path / "error.log", level=level)

    # 不同模块独立日志
    module_loggers = {
        "handle.error_handle": logger_error,
        "handle.member_handle": logger_member,
        "handle.message_handle": logger_message,
        "handle.reaction_handle": logger_message,
        "utils.send": logger_message,
    }

    # 为其他文件使用默认 logger
    for root, dirs, files in os.walk('.'):
        # 从待遍历目录列表中移除 .venv
        dirs[:] = [d for d in dirs if not d.startswith(".venv")]
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):  # 跳过__init__.py
                module_path = Path(root) / file
                module_name = str(module_path.with_suffix('')).replace(os.sep, '.')

                if module_name in module_loggers:
                    print("use customs logger:", module_name)
                else:
                    print("use default logger:", module_name)
                    module_loggers.setdefault(module_name, logger_default)

    for logger_name, config in module_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(config["level"])
        for handler in config["handlers"]:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

def setup_logging(dir: str = "./log", level = OTHER_LEVEL, max_bytes = 32*1024*1024):
    """全局日志配置"""

    # 创建日志目录
    files_path = Path(dir)
    files_path.mkdir(exist_ok=True)

    # 配置基础格式
    log_format = "%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = Formatter(fmt=log_format, datefmt=date_format)

    # 配置日志记录器
    rootLogging(files_path, log_format, date_format, level=level, max_bytes=max_bytes)
    fileLogging(files_path, formatter, level=BOT_LEVEL)

    logger = logging.getLogger(__name__)
    logger.debug("log initialization complete.")


if __name__ == "__main__":

    # 初始化, 只需在主程序写
    setup_logging()

    # 获取logger, 自动继承全局配置, 都要写
    logger = logging.getLogger(__name__)
    # logger = logging.getLogger("log")

    logger.debug("log test debug ...")
    logger.info("log test info ...")
    logger.warning("log test waring ...")
    logger.error("log test error ...")
