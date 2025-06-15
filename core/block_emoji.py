import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

from telegram import StickerSet
from telegram.ext import ContextTypes

BLOCK_EMOJI_FILENAME = "config/block_emoji.json"
blocked_emoji_path = Path(__file__).parent.parent / BLOCK_EMOJI_FILENAME

class BlockEmojiLoader:
    """表情包屏蔽词 json 读写"""

    def __init__(self, file_path):

        self.path = file_path
        self._dict = self._loadEmoji()

    def _loadEmoji(self) -> dict:
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise RuntimeError(f"{self.path} Not Found!")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"json decode Error: {str(e)}")

    def dump(self):
        """保存当前列表"""
        with open(self.path, 'w', encoding="utf-8") as f:
            json.dump(self._dict, f, ensure_ascii=False)

    def addEmojiSet(self, emoji_name, sticker_set: StickerSet=None):
        """添加或更改表情包"""

        if sticker_set:
            self._dict[emoji_name] = [sticker.custom_emoji_id for sticker in sticker_set.stickers]
        self.dump()

    def removeEmojiSet(self, emoji_name):
        """删除表情包"""

        del self._dict[emoji_name]
        self.dump()

    @property
    def dict(self):
        return self._dict


block_emoji = BlockEmojiLoader(blocked_emoji_path)


async def flashEmojisId(context: ContextTypes.DEFAULT_TYPE):
    """重新获取所有表情包的表情 id"""

    for emoji_name in block_emoji.dict:
        logger.info(f"获取 {emoji_name} 表情包")
        await addEmojisId(context, emoji_name, force=True)

async def addEmojisId(context: ContextTypes.DEFAULT_TYPE, emoji_name: str, force=False):
    """添加 emoji_name 表情包的表情 id 至 block_emoji"""

    if (not force) and emoji_name in block_emoji.dict:
        logger.info(f"表情包 {emoji_name} 已在列表中")
    else:
        sticker_set = await context.bot.get_sticker_set(emoji_name)
        block_emoji.addEmojiSet(emoji_name, sticker_set)
        logger.info(f"表情包 {emoji_name} 添加完成")


if __name__ == "__main__":

    logger.info(block_emoji.dict)
