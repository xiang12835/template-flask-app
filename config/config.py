
import logging
import os
from redis import StrictRedis
from base.settings import BASE_DIR

class Config:
    DEBUG = True
    LEVEL_LOG = logging.INFO
    SECRET_KEY = 'slajfasfjkajfj'
    SQL_HOST = '127.0.0.1'
    SQL_USERNAME = 'root'
    SQL_PASSWORD = 'root'
    SQL_PORT = 3306
    SQL_DB = 'videodb'
    # SQL_HOST = os.getenv('SQL_HOST')
    # SQL_USERNAME = os.getenv('SQL_USERNAME')
    # SQL_PASSWORD = os.getenv('SQL_PASSWORD')
    # SQL_PORT = os.getenv('SQL_PORT')
    # SQL_DB = os.getenv('SQL_DB')

    UPLOADED_PHOTOS_DEST = os.path.join(BASE_DIR, 'images')
    UPLOADED_DEFAULT_DEST = os.path.join(BASE_DIR, 'images')

    JSON_AS_ASCII = False
    # 数据库的配置
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_HOST}:{SQL_PORT}/{SQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 指定session使用什么来存储
    SESSION_TYPE = 'redis'
    # 指定session数据存储在后端的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 是否使用secret_key签名你的sessin
    SESSION_USE_SIGNER = True
    # 设置过期时间，要求'SESSION_PERMANENT', True。而默认就是31天
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24  # 一天有效期


class DevConfig(Config):
    pass


class ProConfig(Config):
    LEVEL_LOG = logging.ERROR
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/videodb"


class TestConfig(Config):
    pass


config_dict = {
    'dev': DevConfig,
    'pro': ProConfig,
    'test': TestConfig,
}
