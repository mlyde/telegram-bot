"""数据库操作"""
import logging
logger = logging.getLogger(__name__)
import sqlite3
from pathlib import Path

from telegram import Chat, User
from utils.get_info import getChatInfo, getUserInfo

class Database:
    def __init__(self, table_name: str, db_path: str = ":memory:"):

        if db_path != ":memory:":
            # 创建父文件夹
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # 连接数据库, 如果 .db 文件不存在会自动创建
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.table_name = table_name

        # 创建表, 若更改了 key, 需要手动删除 .db 文件, 重新创建
        self._createTable()

    def _createTable(self):
        """创建表"""

        if self._tableExist():
            logger.debug(f"database: already exist {self.table_name}")
        else:
            self.cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                (user_id INTEGER,
                chat_id INTEGER,
                verified BOOLEAN DEFAULT 0,
                token TEXT,
                join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verify_time TIMESTAMP,
                activity_time TIMESTAMP,
                PRIMARY KEY (user_id, chat_id))''')
            # 手动提交更改
            self.conn.commit()
            logger.debug(f"database: created {self.table_name}")

    def _tableExist(self):
        """表是否已经存在"""

        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (self.table_name,)
        )
        existed_before = self.cursor.fetchone() is not None
        return existed_before

    def addUser(self, chat: Chat, user: User, verified=False, token=''):
        """添加成员"""

        if self.isExist(chat, user): return False
        with self.conn: # 自动提交更改
            self.cursor.execute(f'''INSERT OR IGNORE INTO {self.table_name}
                        (user_id, chat_id, verified, token)
                        VALUES (:user_id, :chat_id, :verified, :token)''',
                        dict(user_id=user.id, chat_id=chat.id, verified=verified, token=token))
        logger.debug(f"database: add {getUserInfo(user)} in {getChatInfo(chat)}")
        return self.cursor.rowcount

    def isExist(self, chat: Chat, user: User):
        """查询是否已记录用户在群中"""

        with self.conn:
            self.cursor.execute(
                f"SELECT 1 FROM {self.table_name} WHERE user_id = ? AND chat_id = ? LIMIT 1",
                (user.id, chat.id)
            )

        exists = self.cursor.fetchone() is not None
        if exists:
            logger.debug(f"database: {getUserInfo(user)} already in {getChatInfo(chat)}")
        return exists

    def readAll(self, parser: bool=True):
        """获取数据库表中所有内容"""

        logger.debug(f"database: select all the contents in the database table")
        with self.conn:
            self.cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = self.cursor.fetchall()

            if parser:
                # 列名
                column_names: list = [description[0] for description in self.cursor.description]
                # 字典
                result = [dict(zip(column_names, row)) for row in rows]
                return result
            else:
                return rows

    def getUnVerifiedUsers(self, chat: Chat):
        """查询指定群未完成验证的用户"""

        logger.debug(f"database: select {getChatInfo(chat)} who have not completed verification")
        with self.conn:
            self.cursor.execute(f'''SELECT user_id FROM {self.table_name}
                        WHERE chat_id=? AND verified=0''',
                        (chat.id,))
            rows = self.cursor.fetchall()
            result = [row[0] for row in rows]
            return result

    def setVerified(self, chat: Chat, user: User):
        """设置为已验证"""

        with self.conn:
            self.cursor.execute(f'''UPDATE {self.table_name}
                        SET verified=1, verify_time=CURRENT_TIMESTAMP
                        WHERE user_id=? AND chat_id=?''',
                        (user.id, chat.id))

        logger.debug(f"database: set {getUserInfo(user)} in {getChatInfo(chat)} verified")
        return self.cursor.rowcount

    def getVerified(self, chat: Chat, user: User):
        """查询是否已验证"""

        logger.debug(f"database: {getUserInfo(user)} in {getChatInfo(chat)} has been verified?")
        with self.conn:
            self.cursor.execute(f'''SELECT verified FROM {self.table_name}
                        WHERE user_id=? AND chat_id=?''',
                        (user.id, chat.id))
            result = self.cursor.fetchone()
            ret = result[0] if result else False
            logger.debug(f"database: {getUserInfo(user)} in {getChatInfo(chat)} already verified")
            return ret

    def setActivity(self, chat: Chat, user: User):
        """设置活跃时间"""

        with self.conn:
            self.cursor.execute(f'''UPDATE {self.table_name}
                        SET activity_time=CURRENT_TIMESTAMP
                        WHERE user_id=? AND chat_id=?''',
                        (user.id, chat.id))

        logger.debug(f"database: set activity {getUserInfo(user)} in {getChatInfo(chat)}")
        return self.cursor.rowcount

    def getActivity(self, chat: Chat, user: User):
        """查询活跃时间"""

        with self.conn:
            self.cursor.execute(f'''SELECT activity_time FROM {self.table_name}
                        WHERE user_id=? AND chat_id=?''',
                        (user.id, chat.id))
            result = self.cursor.fetchone()
            logger.debug(f"database: get activity {getUserInfo(user)} in {getChatInfo(chat)}")
            return result[0] if result and result[0] is not None else False

    def remove(self, chat: Chat, user: User):
        """删除用户记录数据"""

        with self.conn:
            self.cursor.execute(f'''DELETE FROM {self.table_name}
                        WHERE user_id=? AND chat_id=?''',
                        (user.id, chat.id))

        logger.debug(f"database: delete {getUserInfo(user)} in {getChatInfo(chat)}")
        return self.cursor.rowcount

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


db_user_verification = Database("user_verification", db_path="config/user_verification.db")


if __name__ == "__main__":

    try:
        print("\All data:")
        datas = db_user_verification.readAll()
        for data in datas:
            print(data)
    except sqlite3.Error as e:
        print(f"database Error: {e}")
