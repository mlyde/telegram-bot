"""
数据库操作
"""
import logging
logger = logging.getLogger(__name__)
import sqlite3
from pathlib import Path

class Database:
    def __init__(self, table_name: str, db_path: str = ":memory:"):

        if db_path != ":memory:":
            # 创建父文件夹
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # 连接数据库, 如果 .db 文件不存在会自动创建
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.table_name = table_name

        self._createTable()

    def _createTable(self):
        """创建表"""

        if self._tableExist():
            logger.debug(f"已存在数据表: {self.table_name}")
        else:
            self.cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                (user_id INTEGER,
                chat_id INTEGER,
                verified BOOLEAN DEFAULT 0,
                token TEXT,
                join_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verify_time TIMESTAMP,
                first_activity_time TIMESTAMP,
                PRIMARY KEY (user_id, chat_id))''')
            # 手动提交更改
            self.conn.commit()
            logger.debug(f"已创建数据表: {self.table_name}")
        return True

    def _tableExist(self):
        """表是否已经存在"""

        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (self.table_name,)
        )
        existed_before = self.cursor.fetchone() is not None
        return existed_before

    def addUser(self, chat_id: int, user_id: int, verified=False, token=''):
        """添加成员"""

        with self.conn: # 自动提交更改
            # self.cursor.execute(f'''INSERT INTO products VALUES(?, ?, ?, ?)''', (user_id, chat_id, verified, token))
            self.cursor.execute(f'''INSERT OR IGNORE INTO {self.table_name}
                        (user_id, chat_id, verified, token)
                        VALUES (:user_id, :chat_id, :verified, :token)''',
                        dict(user_id=user_id, chat_id=chat_id, verified=verified, token=token))
        logger.debug(f"已添加数据库中 {chat_id} 的 {user_id}")
        return True

    def isExist(self, chat_id: int, user_id: int, ):

        with self.conn:
            self.cursor.execute(
                f"SELECT 1 FROM {self.table_name} WHERE user_id = ? AND chat_id = ? LIMIT 1",
                (user_id, chat_id)
            )

        exists = self.cursor.fetchone() is not None
        logger.debug(f"{chat_id} 中存在 {user_id}")
        return exists


    def getVerify(self, chat_id: int, user_id: int):
        """查询是否验证"""

        logger.debug(f"查询 {user_id} 是否在 {chat_id}")
        with self.conn:
            self.cursor.execute(f'''SELECT verified FROM {self.table_name}
                        WHERE user_id=? AND chat_id=?''',
                        (user_id, chat_id))
            result = self.cursor.fetchone()
            return result[0] if result else False

    def readAll(self, parser: bool=True):
        """获取表中所有内容"""

        logger.debug(f"获取表中所有内容")
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

    def getUnVerifiedUsers(self, chat_id: int):
        """查询指定群未完成验证的用户"""

        logger.debug(f"查询 {chat_id} 中未完成验证的用户")
        with self.conn:
            self.cursor.execute(f'''SELECT user_id FROM {self.table_name}
                        WHERE chat_id=? AND verified=0''',
                        (chat_id,))
            rows = self.cursor.fetchall()
            result = [row[0] for row in rows]
            return result

    def setVerified(self, chat_id: int, user_id: int):
        """设置为已验证"""

        with self.conn:
            self.cursor.execute(f'''UPDATE {self.table_name}
                        SET verified=1, verify_time=CURRENT_TIMESTAMP
                        WHERE user_id=? AND chat_id=?''',
                        (user_id, chat_id))

        logger.debug(f"{user_id} 在 {chat_id} 中已设置为完成验证")
        return True

    def getActivity(self, chat_id: int, user_id: int):
        """查询初次活跃时间"""

        with self.conn:
            self.cursor.execute(f'''SELECT first_activity_time FROM {self.table_name}
                        WHERE user_id=? AND chat_id=?''',
                        (user_id, chat_id))
            result = self.cursor.fetchone()
            return result[0] if result else False

    def setActivity(self, chat_id: int, user_id: int):
        """设置初次活跃时间"""

        with self.conn:
            self.cursor.execute(f'''UPDATE {self.table_name}
                        SET first_activity_time=CURRENT_TIMESTAMP
                        WHERE user_id=? AND chat_id=?''',
                        (user_id, chat_id))

        logger.debug(f"设置 {user_id} 在 {chat_id} 中活跃")
        return True

    def remove(self, chat_id: int, user_id: int):
        """删除用户记录数据"""

        with self.conn:
            self.cursor.execute(f'''DELETE FROM {self.table_name}
                        WHERE user_id=? AND chat_id=?''',
                        (user_id, chat_id))

        logger.debug(f"已删除数据库中 {chat_id} 的 {user_id}")
        return True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


db_user_verification = Database("user_verification", db_path="config/user_verification.db")


if __name__ == "__main__":
    """测试数据库"""

    db_user_verification.addUser(-1, 1, token="test2")
    db_user_verification.addUser(-1, 2, verified=True, token="test1")

    print(db_user_verification.getUnVerifiedUsers(-1))
    print(db_user_verification.getVerify(-1, 1))
    db_user_verification.setVerified(-1, 2)

    print("\n所有数据:")
    datas = db_user_verification.readAll()
    for data in datas:
        print(data)

    print("Exist:", db_user_verification.isExist(-1, 1))

    db_user_verification.remove(-1, 1)
    db_user_verification.remove(-1, -2)

    try:
        db_user_verification.remove(1, 1)

    except sqlite3.Error as e:
        print(f"database Error: {e}")
