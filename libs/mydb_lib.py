
from sqlalchemy.exc import SQLAlchemyError
from base import db
from flask import current_app
from libs.http_lib import error, HttpCode
import pymysql


def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(e)
        reason = str(e)
        return error(code=HttpCode.db_error, msg=reason)


class MysqlHelper(object):
    conn = None

    def __init__(self, host, username, password, db, charset='utf8', port=3306):
        self.host = host
        self.username = username
        self.password = password
        self.db = db
        self.charset = charset
        self.port = port

    def connect(self):
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.username, password=self.password,
                                    db=self.db,
                                    charset=self.charset)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def get_one(self, sql, params=()):
        result = None
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
            self.close()
        except Exception as e:
            print(e)
        return result

    def get_all(self, sql, params=()):
        list_data = ()
        try:
            self.connect()
            self.cursor.execute(sql, params)
            list_data = self.cursor.fetchall()
            self.close()
        except Exception as e:
            print(e)
        return list_data

    def insert(self, sql, params=()):
        return self.__edit(sql, params)

    def update(self, sql, params=()):
        return self.__edit(sql, params)

    def delete(self, sql, params=()):
        return self.__edit(sql, params)

    def __edit(self, sql, params):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql, params)
            self.conn.commit()
            self.close()
        except Exception as e:
            print(e)
        return count


class MysqlConn(object):
    # 魔术方法, 初始化, 构建函数
    def __init__(self):  # 初始化
        # 创建连接    db相当于mysql的连接
        self.db = pymysql.connect(host='127.0.0.1', user='root', password='root', port=3306, database='videodb')
        # 创建游标
        self.cursor = self.db.cursor()

    # 执行modify(修改)相关操作
    def execute_modify_mysql(self, sql):  # 实现一个插入,修改
        self.cursor.execute(sql)
        self.db.commit()

    # 魔术方法, 析构化, 析构函数
    def __del__(self):  # 结束
        self.cursor.close()
        self.db.close()

    def get_all(self, sql):
        list_data = ()
        try:
            self.cursor.execute(sql)
            list_data = self.cursor.fetchall()
        except Exception as e:
            print(e)
        return list_data

