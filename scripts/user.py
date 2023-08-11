
import random

from libs.mydb_lib import MysqlConn


def gen_data():
    mobile = 13011110000
    return [str(i) for i in range(mobile, mobile + 10000)]


def gen_sql(mobile_list):
    tmp = [(f"{i}", f"{i}") for i in mobile_list]
    return str(tmp)[1:-1]


def insert_users():
    conn = MysqlConn()
    temp = gen_sql(gen_data())
    sql = f'insert into user_info (nickname, mobile) values {temp}'
    conn.execute_modify_mysql(sql)


def get_user_id_list():
    conn = MysqlConn()
    mobile_list = random.sample(gen_data(), 100)
    sql_list = tuple([int(i) for i in mobile_list])
    sql = f'select id from user_info where mobile in {sql_list}'
    data = conn.get_all(sql)
    return [i[0] for i in data]


def content_id_list():
    conn = MysqlConn()
    sql = 'select id from content_main'
    data = conn.get_all(sql)
    return [i[0] for i in data]


def gen_play_sql():
    tmp = []
    for user_id in get_user_id_list():
        for content_id in random.sample(content_id_list(), 500):
            tmp.append((user_id, content_id, random.randint(5, 60)))
    return str(tmp)[1:-1]


def insert_play():
    conn = MysqlConn()
    sql = f'insert into user_play (user_id, content_id, play_time) values {gen_play_sql()}'
    conn.execute_modify_mysql(sql)


if __name__ == '__main__':
    insert_users()
    # print(gen_play_sql())
    insert_play()
