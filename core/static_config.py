import logging
logger = logging.getLogger(__name__)

import yaml
from pathlib import Path
from typing import Any

STATIC_CONFIG_FILENAME = "config/static_config.yaml"

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
            static_config_path = Path(__file__).parent.parent / STATIC_CONFIG_FILENAME
            with open(static_config_path, 'r', encoding='utf-8') as f:
                cls._static_config = yaml.safe_load(f)

        except FileNotFoundError:
            raise RuntimeError(f"{static_config_path} Not Found!")
        except yaml.YAMLError as e:
            raise RuntimeError(f"yaml Error: {str(e)}")

    @property
    def config(self) -> dict[str, Any]:
        """安全获取配置字典的副本"""
        return self._static_config.copy()


# 初始化配置
try:
    static_config = StaticConfigLoader().config
except RuntimeError as e:
    print(f"load fail{e}")
    # 终止当前程序
    exit(1)


if __name__ == "__main__":

    print("配置文件: ")
    print(static_config)
