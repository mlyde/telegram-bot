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

        self.createTable()

    def createTable(self):
        """创建表"""

        self.cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
            (user_id INTEGER,
            chat_id INTEGER,
            verified BOOLEAN DEFAULT 0,
            token TEXT,
            join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verify_date TIMESTAMP,
            PRIMARY KEY (user_id, chat_id))''')
        # 手动提交更改
        self.conn.commit()

    def create(self, user_id: int, chat_id: int, verified=False, token=''):
        """创建一条数据"""

        with self.conn: # 自动提交更改
            # self.cursor.execute(f'''INSERT INTO products VALUES(?, ?, ?, ?)''', (user_id, chat_id, verified, token))
            self.cursor.execute(f'''INSERT OR IGNORE INTO {self.table_name}
                        (user_id, chat_id, verified, token)
                        VALUES (:user_id, :chat_id, :verified, :token)''',
                        dict(user_id=user_id, chat_id=chat_id, verified=verified, token=token))

    def read(self, user_id: int, chat_id: int):
        """查询数据"""

        with self.conn:
            self.cursor.execute(f'''SELECT verified FROM {self.table_name}
                        WHERE user_id=? AND chat_id=?''',
                        (user_id, chat_id))
            result = self.cursor.fetchone()
            return result[0] if result else False

    def readAll(self, parser: bool=True):
        """获取表中所有内容"""

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

    def getUnverifiedUsers(self, chat_id: int):
        """查询指定群未完成验证的用户"""

        with self.conn:
            self.cursor.execute(f'''SELECT user_id FROM {self.table_name}
                        WHERE chat_id=? AND verified=0''',
                        (chat_id,))
            rows = self.cursor.fetchall()
            result = [row[0] for row in rows]
            return result

    def setVerified(self, user_id: int, chat_id: int):
        """更新数据"""

        with self.conn:
            self.cursor.execute(f'''UPDATE {self.table_name}
                        SET verified=1, verify_date=CURRENT_TIMESTAMP
                        WHERE user_id=? AND chat_id=?''',
                        (user_id, chat_id))

    def delete(self, user_id: int, chat_id: int):
        """删除数据"""

        with self.conn:
            self.cursor.execute(f'''DELETE FROM {self.table_name}
                        WHERE user_id=? AND chat_id=?''',
                        (user_id, chat_id))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


db_user_verification = Database("user_verification")


if __name__ == "__main__":
    """测试数据库"""

    db_user_verification.create(2, -1, token="test2")
    db_user_verification.create(1, -1, verified=True, token="test1")

    print(db_user_verification.getUnverifiedUsers(-1))
    print(db_user_verification.read(1, -1))
    print(db_user_verification.setVerified(2,-1))
    print("\n所有数据:")
    datas = db_user_verification.readAll()
    for data in datas:
        print(data)

    db_user_verification.delete(1, -1)
    db_user_verification.delete(2, -1)

    try:
        db_user_verification.delete(1, 1)

    except sqlite3.Error as e:
        print(f"database Error: {e}")
