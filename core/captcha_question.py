"""读取验证问题配置文件"""
import logging
logger = logging.getLogger(__name__)
from typing import TypeAlias, TypedDict, NotRequired
import yaml
from pathlib import Path

_CAPTCHA_QUESTION_FILENAME = "config/captcha_question.yaml"

RegexPattern: TypeAlias = str
class QAPair(TypedDict):
    q: str          # 问题
    a: RegexPattern # 答案
    note: NotRequired[str]

class QuestionCaptcha(TypedDict):
    qa_pairs: list[QAPair]


try:
    static_config_path = Path(__file__).parent.parent / _CAPTCHA_QUESTION_FILENAME
    with open(static_config_path, 'r', encoding="utf-8") as f:
        _captcha_question_dict: QuestionCaptcha = yaml.safe_load(f)
        question_answer_list = _captcha_question_dict.get("qa_pairs")

except FileNotFoundError:
    raise RuntimeError(f"{static_config_path} Not Found!")
except yaml.YAMLError as e:
    raise RuntimeError(f"yaml Error: {str(e)}")
