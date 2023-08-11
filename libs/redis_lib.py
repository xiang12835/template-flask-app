from redis import ConnectionPool, Redis
import pickle,traceback
from libs.logger import log
from libs.date_util import *


class PythonNativeRedisClient(object):
    """A simple redis client for storing and retrieving native python datatypes."""

    def __init__(self, client):
        """Initialize client."""
        self.client = client

    def __len__(self):
        return bool(self.client)

    def chk(self):
        if self.client:
            try:
                self.client.ping()
            except:
                self.client.connection_pool.disconnect()
                self.client = None

    def set(self, key, value, time=0, **kwargs):
        """Store a value in Redis."""
        # self.chk()
        if not self.client:
            log('redis set fail, client=%s' % (self.client), 'redis-set.log')
            return False

        res = self.client.set(key, pickle.dumps(value), **kwargs)
        if res and time:  # 有效期
            self.client.expire(key, time)
        # log('redis set success, %s'%(key), 'redis-set.log')
        return res

    def get(self, key):
        """Retrieve a value from Redis."""
        # self.chk()
        if not self.client:
            log('redis get fail, client=%s' % (self.client), 'redis-get.log')
            return None

        val = self.client.get(key)
        if val:
            val = pickle.loads(val, encoding='utf-8')
            # log('redis get %s = %s'%(key, val), 'redis-get.log')
            return val
        # log('redis get %s = None'%(key), 'redis-get.log')
        return None

    def delete(self, key):
        # self.chk()
        if not self.client: return None
        self.client.delete(key)

    def get_stats(self):
        # self.chk()
        if not self.client: return [('info', {})]
        return [('info', self.client.info())]


def redis_client(s='', host='localhost', port=6379, password=''):
    # password = 'asplpl88'
    max_connections = None  # 最大连接数
    error_connect = 0  # 重连次数上限
    while True:
        try:
            pool = ConnectionPool(host=host, port=port, db=0, password=password, max_connections=max_connections)
            redis = Redis(connection_pool=pool)
            redis.ping()
        except Exception as e:
            log(e)
            log('redis连接失败,正在等待1秒后尝试重连')
            log(traceback.format_exc(limit=20))
            error_connect += 1
            if error_connect >= 1:
                return PythonNativeRedisClient(None)
            time.sleep(1)  # 暂停1秒重连
            continue
        log('redis# %s time %s' % (s, getToday(9)))
        return PythonNativeRedisClient(redis)


RC = redis_client('get')


def RC_get(key):
    global RC
    key = str(key)
    d = None

    try:
        d = RC.get(key)
    except:
        log(traceback.format_exc(limit=20))

    return d


def RC_set(key, d, time=0, sync=1):
    # time = 10,  #过期删除的秒数
    global RC
    key = str(key)

    try:
        RC.set(key, d, time)
    except:
        log(traceback.format_exc(limit=20))
        RC = redis_client('set')
    return


def RC_incr(key, maxTo1=0):
    # 整数自增生成器：从1开始，自动+1, 并返回结果 MC_set("key","1")  #值必须是字符串格式
    # maxTo1: 0|maxint, 0-不限制最大,  maxint-超过最大自动变为1开始

    key = str(key)
    v = RC_get(key)
    if not v:
        v = 1
    else:
        v += 1

    if maxTo1 and v > maxTo1: v = 1
    RC_set(key, v)
    return v


def RC_delete(key):
    global RC
    key = str(key)

    r = ''
    try:
        r = RC.delete(key)
    except:
        log(traceback.format_exc(limit=20))
        RC = redis_client('del')
    return r
