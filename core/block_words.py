import logging
logger = logging.getLogger(__name__)
from typing import TypeAlias, TypedDict
from pathlib import Path
import re
import yaml

_BLOCK_WORDS_FILENAME = "config/block_words.yaml"

RegexPattern: TypeAlias = str
class BlockWords(TypedDict):
    """屏蔽词文件"""
    username: list[RegexPattern]
    userid: list[RegexPattern]
    bio: list[RegexPattern]
    chatname: list[RegexPattern]    # 主页中挂的频道 personal_chat
    message: list[RegexPattern]     # message.text or message.quote.text
    button: list[RegexPattern]

try:
    static_config_path = Path(__file__).parent.parent / _BLOCK_WORDS_FILENAME
    with open(static_config_path, 'r', encoding='utf-8') as f:
        block_worlds_dict: BlockWords = yaml.safe_load(f)

except FileNotFoundError:
    raise RuntimeError(f"{static_config_path} Not Found!")
except yaml.YAMLError as e:
    raise RuntimeError(f"yaml Error: {str(e)}")

# 合并为一个正则表达式
re_message = '|'.join(block_worlds_dict.get("message"))
re_username = '|'.join(block_worlds_dict.get("username"))
re_bio = '|'.join(block_worlds_dict.get("bio"))
re_user_id = '|'.join(block_worlds_dict.get("userid"))
re_chatname = '|'.join(block_worlds_dict.get("chatname"))
re_button = '|'.join(block_worlds_dict.get("button"))

# 编译正则, 提高匹配速度
pattern_group_message = re.compile(re_message, flags=re.IGNORECASE|re.DOTALL)
pattern_username= re.compile(re_username, flags=re.IGNORECASE|re.DOTALL)
pattern_bio = re.compile(re_bio, flags=re.IGNORECASE|re.DOTALL)
pattern_user_id = re.compile(re_user_id, flags=re.IGNORECASE|re.DOTALL)
pattern_chatname = re.compile(re_chatname, flags=re.IGNORECASE|re.DOTALL)
pattern_button = re.compile(re_button, flags=re.IGNORECASE|re.DOTALL)

logger.info("正则表达式 pattern 编译完成")


if __name__ == "__main__":

    print(re_message, re_username, re_bio, re_user_id, re_chatname, re_button, sep='\n\n')
