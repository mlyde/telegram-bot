import os
import json
import logging
import time

config_logger = logging.getLogger(__name__)
config_logger.setLevel(logging.DEBUG)

config_console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    )
config_console_handler.setFormatter(formatter)
config_logger.addHandler(config_console_handler)

config_logger.info("config logger started.")

config_dict_outter = {
    "token": "0000000000:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "blocked_words": {
        "username": [
        ],
        "userid": [
        ],
        "bio": [
        ],
        "chatname": [
        ],
        "message": [
        ],
        "button": [
        ],
    },
    "premium_blocked_emoji": {  # 包含屏蔽词的 {会员表情包id: [表情id,], }
        "bygbb666": [],
    },
    "active_groups": [
        -1000000000000, # @xxx
        ],
    "admin": {
        "1111111111": "xxx"
        },
    "needCaptcha": [],
}

class BotConfig():

    def __init__(self, floader: str, config_dict: dict={}):

        config_logger.debug("botconfig 初始化")
        self.config_file_path = f"{floader}/config.json"
        self.config_dict = config_dict

        if not config_dict:
            # 存在配置文件则读取, 否则创建
            if os.path.isfile(self.config_file_path):
                config_logger.debug("config file exists")
                self.config_dict = self.load()
            else:
                config_logger.debug("config file not exists")
                self.config_dict: dict = config_dict_outter
                self.save()

    def set(self, config: dict):
        """  """
        self.config_dict = config

    def load(self) -> dict:
        """ 读取配置文件 """

        with open(self.config_file_path, 'r', encoding="utf-8") as f:
            config_logger.debug("reading config file")
            return json.load(f)

    def backup(self):
        """ 备份配置文件 """
        if os.path.exists(self.config_file_path):
            config_logger.debug("backup confing file started")
            os.rename(self.config_file_path, f"{self.config_file_path}.{int(time.time())}")
            config_logger.debug("backup confing file complete")
            return True
        else:
            config_logger.debug("confing file not exists")
            return False

    def merge(self):
        """ 将现有配置与文件中配置合并, 防止配置文件不同步 """

        config_logger.debug("merge config")
        # config_logger.debug(self.config_dict)
        self.config_dict = self.load() | self.config_dict   # 合并字典, 相同 key 取 | 后字典的 value

    def save(self, backup: bool=False):
        """ 保存配置文件 """

        if backup:
            self.backup()
        with open(self.config_file_path, 'w', encoding="utf-8") as f:
            json.dump(self.config_dict, f, ensure_ascii=False)
        config_logger.info("config file saved")

    def flash(self):
        """ 更新配置文件内容 """

        self.merge()
        self.save(backup=True)

if __name__ == "__main__":

    FLOADER = "/home/ml/Downloads/TelegramBot"
    config = BotConfig(floader=FLOADER, config_dict=config_dict_outter)
    del config_dict_outter["premium_blocked_emoji"]
    config.flash()
