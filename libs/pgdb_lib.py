import psycopg2
from dbutils.pooled_db import PooledDB
from libs.logger import log


class DataBaseParent:
    def __init__(self):
        """构造器
        strConnect := 'usr/pwd@202.96.154.184:5432/dbname/GB18030'

        #特别注意：在合肥数据中心的红旗4.4下，发现带参数 client_encoding, 会报错
        #psycopg2.OperationalError: invalid connection option client_encoding
        #处理方法：设置环境变量  export PGCLIENTENCODING=GB18030, 并去掉 client_encoding 参数
        链接参数： 'usr/pwd@202.96.154.184:5432/dbname/'
        """

        self.host, self.port, self.usr, self.pwd, self.dbname, self.charset = self.splitStrConnect()

        maxconn = 1000  # 最大连接数
        maxcached = 50  # 最大缓存连接数
        failures = (psycopg2.OperationalError, psycopg2.InternalError, psycopg2.InterfaceError)
        args = (0, maxcached, 0, maxconn, 0, 0, None, True,
                failures)  # mincached=0, maxcached=0, maxshared=0, maxconnections=0, blocking=False, maxusage=None, setsession=None, reset=True,failures=None, ping=1
        conn_kwargs = {'port': self.port, 'database': self.dbname, 'host': self.host, 'user': self.usr,
                       'password': self.pwd}
        if self.charset: conn_kwargs['client_encoding'] = self.charset

        try:
            self.pool = PooledDB(psycopg2, *args, **conn_kwargs)
        except Exception as e:
            log(e)
            raise "Connect PostgreSQL DB Error!"

    def splitStrConnect(self):
        """解析连接字串"""
        self.strConnect = 'web/asplpl88@localhost:5432/web/GB18030'
        A, B = self.strConnect.split('@')
        usr, pwd = A.split('/')

        m = self.strConnect.count('/')
        if m == 2:
            host, dbname = B.split('/')
            charset = ''
        else:
            host, dbname, charset = B.split('/')

        port = 5432  # 默认端口
        if host.find(':') > 0: host, port = host.split(':')

        return host, port, usr, pwd, dbname, charset.upper().strip()

    def select(self, sql, tup=()):
        """SELECT
           tup  := 一维度 tuple
           返回 := L,m
        """
        conn = self.pool.connection()
        cur = conn.cursor()

        if tup:
            tup = tuple(tup)
            if type(tup[0]) == type(()):
                cur.execute(sql, tup[0])
            else:
                cur.execute(sql, tup)
        else:
            cur.execute(sql)

        L = cur.fetchall()
        m = cur.rowcount

        cur.close()
        conn.close()
        return L, m

    def insert(self, sql, tup=(), getaid=0):
        """ 插入 (可批量，和单独插入，并会返回影响行数)
            例子： db.insert("INSERT INTO waithandle_to(id, tolist) VALUES(%s,%s)", ((5,5),(6,6)))
            注意： tup := 为2维度tup, 如果只有一行的参数，必须写成 (('2','2'),)，即第一对值后面的 ',' 号不能省略，否则报错
                   sql := sql 中的替换参数是 %s, 而不是 ?, 特别注意
                   用参数 '%s' 的好处， 可以不必管sql中的"'"号替换，和日期，文本的分割符
        """
        conn = self.pool.connection()
        cur = conn.cursor()

        # 返回值为受影响的行数
        if tup:
            tup = tuple(tup)
            if type(tup[0]) == type(()):
                r = cur.executemany(sql, tup)
            else:
                r = cur.execute(sql, tup)
        else:
            r = cur.execute(sql)

        # 2. 计算自增id
        aid = 0
        if getaid:
            L = cur.fetchall()
            aid = L[0][0]

        conn.commit()
        cur.close()
        conn.close()
        return aid

    def copy_from(self, file, table, columns):
        """ 插入 (可批量，和单独插入，并会返回影响行数)
        """
        conn = self.pool.connection()
        cur = conn.cursor()

        cur.copy_from(file, table, columns=columns)

        conn.commit()
        cur.close()
        conn.close()
        return

    def delete(self, sql, tup=()):
        """删除"""
        r = self.insert(sql, tup)
        return r

    def update(self, sql, tup=()):
        """修改"""
        r = self.insert(sql, tup)
        return r

    def exec_idu(self, sql, tup=()):
        """可执行 insert,delete,update"""
        r = self.insert(sql, tup)
        return r

    def close(self):
        conn = self.pool.connection()
        conn.close()
        self.pool.close()
        return 0

    def getaid(self, tname, colname):
        """ 获取刚插入的自增列的id
            tname   := 表名
            colname := 自增列的列名
        """

        sql = "SELECT max(%s) FROM %s" % (colname, tname)
        lT, iN = self.select(sql)
        id = lT[0][0]

        if id is None: id = 0
        return id

    def getnid(self, tname, colname):
        """ 获取某列的最大值 + 1
            tname   := 表名
            colname := 列名
        """
        return self.getaid(tname, colname) + 1


def pgdb():
    """ 数据库链接快速 """
    return DataBaseParent()
