
import logging
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from utils.file_util import make_dir
import os

LOG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)) + os.sep + "logs"


def setup_log(logger_name='flask_log', log_file='logs/log', level=logging.INFO):
    """根据创建app时的配置环境，加载日志等级。setup_log 函数将日志记录到文件中"""
    
    # 创建日志文件
    make_dir(LOG_ROOT)

    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式             日志记录时间   日志等级   输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(asctime)s - %(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger(logger_name).addHandler(file_log_handler)
    # formatter = jsonlogger.JsonFormatter('%(asctime) %(levelname) %(module) %(funcName) %(lineno) %(message)')
    # app.logger.handlers[0].setFormatter(formatter)
    return file_log_handler


def setup_logger(logger_name, log_file, level=logging.INFO):
    """ setup_logger 函数同时记录日志到文件和控制台上
    %(asctime)s 即日志记录时间，精确到毫秒
    %(levelname)s 即此条日志级别
    %(filename)s 即触发日志记录的python文件名
    %(funcName)s 即触发日志记录的函数名
    %(lineno)s 即触发日志记录代码的行号
    %(message)s 这项即调用如app.logger.info(‘info log’)中的参数，即message
    :param logger_name:
    :param log_file:
    :param level:
    :return:
    """
    # 创建日志对象
    log = logging.getLogger(logger_name)
    # 设置格式，'% (asctime) s: %(message) s'，即日志记录时间和日志内容
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    # 创建一个文件处理器，将日志内容输出到名为log_file的文件中。
    file_handler = logging.FileHandler(log_file, mode='w')
    # 将日志格式设置为文件处理器的格式
    file_handler.setFormatter(formatter)
    # 创建一个流处理器，将日志内容输出到控制台
    stream_handler = logging.StreamHandler()
    # 将日志格式设置为流处理器的格式
    stream_handler.setFormatter(formatter)
    # 将日志级别设置为传入的参数level
    log.setLevel(level)
    # 将文件处理器和流处理器添加至日志对象中
    log.addHandler(file_handler)
    log.addHandler(stream_handler)
    return log
    

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname


def json_log(logger_name, log_file, level=logging.INFO):
    """json_log 函数则是将日志以 json 格式记录到文件中"""
    logging.basicConfig(level=level)  # 调试debug级
    log = logging.getLogger(logger_name)
    # log_handler = logging.StreamHandler()
    log_handler = logging.FileHandler(log_file)
    # formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    # formatter = jsonlogger.JsonFormatter(json_encoder=json.JSONEncoder)
    log_handler.setFormatter(formatter)
    log.addHandler(log_handler)
    return log
