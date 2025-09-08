import logging
logger = logging.getLogger(__name__)
import yaml
from pathlib import Path
from typing import Any, TypeAlias, TypedDict, Literal
from telegram import ChatMember, Chat

_STATIC_CONFIG_FILENAME = "config/static_config.yaml"

UserId: TypeAlias = int   # 用户 id 为正整数
ChatId: TypeAlias = int   # 群组 id 为负整数
ChatIdStr: TypeAlias = str# 文本群组 id, 用做字典的 key
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

class StaticConfig(TypedDict):
    """基础配置文件"""
    token: str
    proxy: str
    directory: str
    font: str                       # 生成图片验证码的字体文件路径
    active_group_id: list[ChatId]   # bot 运行的群
    debug_group_id: list[ChatId]    # bot 测试功能的群, 方便测试
    admins_dict: dict[ChatIdStr, tuple[UserId, ...]]# 群对应的管理员
    forward_to: UserId | ChatId
    owener_user_id: list[UserId]
    level: LogLevel
    help_content: str
    description: str

class StaticConfigLoader:
    """配置加载器(单例模式)"""
    _instance = None
    _static_config: dict[str, Any] = None

    # 确保只有一个实例
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        try:
            static_config_path = Path(__file__).parent.parent / _STATIC_CONFIG_FILENAME
            with open(static_config_path, 'r', encoding="utf-8") as f:
                cls._static_config = yaml.safe_load(f)

        except FileNotFoundError:
            raise RuntimeError(f"{static_config_path} Not Found!")
        except yaml.YAMLError as e:
            raise RuntimeError(f"yaml Error: {str(e)}")

    @property
    def config(self) -> dict[str, Any]:
        return self._static_config

# 初始化配置
try:
    static_config: StaticConfig = StaticConfigLoader().config
    static_config.setdefault("admins_dict", {})
except RuntimeError as e:
    print(f"load fail{e}")
    exit(1)


if __name__ == "__main__":

    print("配置文件: ")
    print(static_config)
