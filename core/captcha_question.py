"""读取验证问题配置文件"""
import logging
logger = logging.getLogger(__name__)

CAPTCHA_QUESTION_FILENAME = "config/captcha_question.yaml"

import yaml
from pathlib import Path

try:
    static_config_path = Path(__file__).parent.parent / CAPTCHA_QUESTION_FILENAME
    with open(static_config_path, 'r', encoding='utf-8') as f:
        captcha_question_dict: dict = yaml.safe_load(f)

except FileNotFoundError:
    raise RuntimeError(f"{static_config_path} Not Found!")
except yaml.YAMLError as e:
    raise RuntimeError(f"yaml Error: {str(e)}")
