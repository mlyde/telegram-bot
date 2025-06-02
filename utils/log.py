"""
配置基本日志参数
"""

from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from core.static_config import static_config


if static_config["debug"]:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.WARNING


def setup_logging(dir: str = "./log", level = LOG_LEVEL, max_bytes = 64*1024*1024):
    """全局日志配置中心"""

    # 创建日志目录
    files_path = Path(dir)
    files_path.mkdir(exist_ok=True)

    # 基础格式配置
    log_format = "%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # 两种方式操作根记录器
    # # 根日志配置 (全局继承)
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

    # ================ 总日志 ================
    # 手动配置根记录器配置, basicConfig 可防止重复配置 (仅在根记录器无处理器时生效)
    logging.basicConfig(
        format=log_format,
        datefmt=date_format,
        level=level,
        handlers=[
            logging.StreamHandler(),             # 日志输出到终端
            RotatingFileHandler(files_path / "_all.log", maxBytes=max_bytes, backupCount=8, encoding="utf-8"),  # 日志写入到文件
        ]
    )

    # ================ 单独文件日志 ================
    logger_bot ={
        "level": logging.DEBUG,
        "handlers": [
            RotatingFileHandler(
                filename=files_path / "bot.log",
                maxBytes=max_bytes, 
                backupCount=8,
                encoding="utf-8"
            )
        ]
    }
    logger_message = {
        "level": logging.DEBUG,
        "handlers": [
            RotatingFileHandler(
                filename=files_path / "message.log",
                maxBytes=max_bytes,
                backupCount=1,
                encoding="utf-8"
            )
        ]
    }

    # 可设置部分模块另存独立日志
    module_loggers = {
        "main": logger_bot,
        "utils.check_contents": logger_bot,
        "utils.get_info": logger_bot,
        "utils.lifecycle": logger_bot,
        "utils.log": logger_bot,
        "utils.other": logger_bot,
        "utils.retry": logger_bot,
        "utils.self": logger_bot,
        "utils.send": logger_bot,
        "utils.time": logger_bot,
        "core.block_emoji": logger_bot,
        "core.block_words": logger_bot,
        "core.static_config": logger_bot,
        "handle.callback_handle": logger_bot,
        "handle.command_handle": logger_bot,
        "handle.error_handle": logger_bot,
        "handle.member_handle": logger_bot,
        "handle.message_handle": logger_message,
        "handle.other_handle": logger_bot,
        "handle.reaction_handle": logger_bot,
    }

    for logger_name, config in module_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(config["level"])
        for handler in config["handlers"]:
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    logger = logging.getLogger(__name__)
    logger.debug("log initialization complete.")

if __name__ == "__main__":

    # 初始化, 只需在主程序写
    setup_logging()

    # 获取logger, 自动继承全局配置
    logger = logging.getLogger(__name__)
    # logger = logging.getLogger("log")

    logger.debug("log test debug ...")
    logger.info("log test info ...")
    logger.warning("log test waring ...")
    logger.error("log test error ...")
