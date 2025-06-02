import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path


BLOCK_EMOJI_FILENAME = "config/block_emoji.json"

blocked_words_path = Path(__file__).parent.parent / BLOCK_EMOJI_FILENAME

def emojiJsonRead():
    try:
        with open(blocked_words_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except FileNotFoundError:
        raise RuntimeError(f"{blocked_words_path} Not Found!")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"json decode Error: {str(e)}")

def emojiJsonWrite(block_emoji_dict):

    with open(blocked_words_path, 'w', encoding="utf-8") as f:
        json.dump(block_emoji_dict, f, ensure_ascii=False)


block_emoji_dict = emojiJsonRead()


if __name__ == "__main__":

    print(block_emoji_dict)

