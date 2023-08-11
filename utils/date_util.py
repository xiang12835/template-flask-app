'''
Author: your name
Date: 2021-06-02 15:46:02
LastEditTime: 2023-07-26 12:14:23
LastEditors: your name
Description: In User Settings Edit
FilePath: /Flask-Project/api/utils/date_utils.py
'''
import calendar
import datetime
import time


def datetime2str(date_format):
    """
    时间格式转时间字符串
    :param date:
    :return:
    """
    date_str = datetime.datetime.strftime(date_format, "%Y-%m-%d %H:%M")
    return date_str


def get_current_month_start_and_end(date):
    """
    年份 date(2017-09-08格式)
    :param date:
    :return:本月第一天日期和本月最后一天日期
    """
    if date.count('-') != 2:
        raise ValueError('- is error')
    year, month = str(date).split('-')[0], str(date).split('-')[1]
    end = calendar.monthrange(int(year), int(month))[1]
    start_date = '%s-%s-01' % (year, month)
    end_date = '%s-%s-%s' % (year, month, end)
    return start_date, end_date


def get_current_month_start_and_end_no_day(date):
    """
    年份 date(2017-09格式)
    :param date:
    :return:本月第一天日期和本月最后一天日期
    """
    if date.count('-') != 1:
        raise ValueError('- is error')
    year, month = str(date).split('-')[0], str(date).split('-')[1]
    end = calendar.monthrange(int(year), int(month))[1]
    start_date = '%s-%s-01' % (year, month)
    end_date = '%s-%s-%s' % (year, month, end)
    return start_date, end_date


def datestr2timestamp(date_str):
    """
    时间字符串转时间戳
    :param date_str:
    :return:
    """
    timeArray = time.strptime(date_str, "%Y-%m-%d")

    # 转换为时间戳
    timeStamp = int(time.mktime(timeArray))

    return timeStamp


def datestr2timestamp_hms(date_str):
    """
    时间字符串转时间戳
    :param date_str:
    :return:
    """
    timeArray = time.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    # 转换为时间戳
    timeStamp = int(time.mktime(timeArray))

    return timeStamp


def str2stamp_hms(time_str):
    timeArray = time.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    # 转换为时间戳:
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def stamp2str(timeStamp):
    timeArray = time.localtime(timeStamp)
    strTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return strTime


def normalize_date(dateStr):
    return str(dateStr)[:19]


if __name__ == '__main__':
    print(get_current_month_start_and_end_no_day('2023-04'))
