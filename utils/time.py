"""
时间相关的变量, 函数
"""
import logging
logger = logging.getLogger(__name__)

from zoneinfo import ZoneInfo
import time
import datetime

# 当前 UTC 时区
DEFAULT_TIMEZONE = ZoneInfo("Asia/Shanghai")
utc_timezone = datetime.timezone(datetime.timedelta(hours=8))

class StartupTime:
    def __init__(self):
        self._timestamp = None
        self._date = None
        self._shift_time = None
        self.update()

    def update(self):
        self._stamp = time.time()       # 1748787444.371503
        self._date = datetime.datetime.now().date() # 2025-06-01
        self._shift_time = datetime.datetime.now()# 2025-06-01 22:17:22.371503

    # 其他文件直接引用变量不会同步更新, 要使用函数获取变量
    @property
    def stamp(self):
        return self._stamp

    @property
    def date(self):
        return self._date

    @property
    def shift_time(self):
        return self._shift_time


last_start_up_time = StartupTime()


if __name__ == "__main__":

    from utils.log import setup_logging
    setup_logging()

    logger.info(datetime.datetime.now())
    logger.info(datetime.datetime.now(datetime.timezone.utc))   # UTC 时间
    logger.info(datetime.datetime.now(datetime.timezone.utc).astimezone(utc_timezone))
