
import re
import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, session, redirect, url_for, g

from base.redprint import Redprint
from models.content import ContentMain, ContentComment, ContentReply, ContentLike, ContentCollect
from models.user import UserInfo, UserLogin
from utils.common import admin_login_data
from libs.http_lib import error, HttpCode, success


api = Redprint('index')


@api.route('/')
@admin_login_data
def admin_index():
    if not g.user:
        return redirect(url_for('admin.login'))
    return render_template('X-admin/index.html')


@api.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('X-admin/login.html')

    data_dict = request.form
    mobile = data_dict.get('username')
    password = data_dict.get('password')
    # 1验证手机号格式
    if not re.match('1[3456789]\\d{9}', mobile):
        return error(HttpCode.parmas_error, msg="手机号格式不正确")
    # 2.校验参数
    if not all([mobile, password]):
        return error(HttpCode.parmas_error, msg="参数不完整")

    # 3.通过手机号取出用户对象
    try:
        user_login = UserLogin.query.filter(UserLogin.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return error(HttpCode.db_error, msg="数据库查询异常")

    # 4.判断用户对象是否存在
    if not user_login:
        return error(HttpCode.parmas_error, msg="该用户不存在")

    # 5.判断密码是否正确
    if not user_login.check_password(password):
        return error(HttpCode.parmas_error, msg="密码输入错误")
    user = UserInfo.query.get(user_login.user_id)
    # 6.记录用户登陆状态
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    return success('登陆成功', data=user.to_dict())


@api.route('/logout')
def logout():
    session.pop("user_id", "")
    session.pop("name", "")

    # 返回响应
    return redirect(url_for('admin.login'))


@api.route('/welcome')
@admin_login_data
def welcome():
    # 视频数 用户数 评论数 回复数
    video_nums = ContentMain.query.count()
    users_nums = UserInfo.query.count()
    comments_nums = ContentComment.query.count()
    reply_nums = ContentReply.query.count()
    like_nums = ContentLike.query.count()
    collect_nums = ContentCollect.query.count()
    # 获取用户统计数据
    data_statistics = get_user_count()

    data = {
        'video_nums': video_nums,
        'comments_nums': comments_nums,
        'users_nums': users_nums,
        'reply_nums': reply_nums,
        'like_nums': like_nums,
        'collect_nums': collect_nums,
    }
    data.update(data_statistics)
    # print(data)
    return render_template('X-admin/welcome.html', data=data)


def get_user_count():
    # 查询总人数
    total_count = 0
    try:
        total_count = UserInfo.query.count()
        # print('当前用户数量',total_count)
    except Exception as e:
        current_app.logger.error(e)

    # 查询月新增数
    mon_count = 0
    now = time.localtime()
    try:
        mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
        mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
        mon_count = UserInfo.query.filter(UserInfo.create_time >= mon_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    # 查询日新增数
    day_count = 0
    day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
    try:
        day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
        day_count = UserInfo.query.filter(UserInfo.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)
    day_rate = round(day_count / total_count, 4) * 100
    mon_rate = round(mon_count / total_count, 4) * 100
    # 查询图表信息
    # 获取到当天00:00:00时间

    now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # 定义空数组，保存数据
    active_date = []
    active_count = []

    # 依次添加数据，再反转
    for i in range(0, 31):
        begin_date = now_date - timedelta(days=i)
        end_date = now_date - timedelta(days=(i - 1))
        active_date.append(begin_date.strftime('%Y-%m-%d'))
        count = 0
        try:
            # count = UserInfo.query.join(UserLogin, UserInfo.id == UserLogin.user_id).filter(
            #     UserInfo.is_admin != 1, UserLogin.last_login >= begin_date,
            #     UserLogin.last_login < end_date
            # ).count()
            count = UserLogin.query.filter(
                UserLogin.last_login >= begin_date,
                UserLogin.last_login < end_date
            ).count()
        except Exception as e:
            current_app.logger.error(e)
        active_count.append(count)

    active_date.reverse()
    active_count.reverse()

    data = {"total_count": total_count, "mon_count": mon_count, "day_count": day_count, "active_date": active_date,
            "active_count": active_count, 'day_rate': day_rate, 'mon_rate': mon_rate}

    return data

