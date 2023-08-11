
from flask import url_for, render_template, g, redirect, request
from sqlalchemy import func

from base import db
from base.redprint import Redprint
from models.content import ContentMain
from models.user import UserPlay
from utils.common import admin_login_data
from libs.http_lib import success

api = Redprint('video')

color_list = ["#D1EEEE", "#CDC9C9", "#CDB38B", "#CD919E", "#CD6839", "#CD3700", "#CD2990", "#CD00CD", "#436EEE",
              "#080808"]
color_list2 = ["#FF9966", "#FF6666", "#FFCCCC", "#CC9966", "#666666", "#CC9999", "#FF6666", "#FFFF66", "#99CC66",
               "#CCFFFF"]
color_list.reverse()
color_list2.reverse()


@api.route('/statistics')
@admin_login_data
def video_statistics():
    if not g.user:
        return redirect(url_for('admin.login'))
    time_data = play_time_statistics()
    count_data = play_count_statistics()
    data = {
        'time_data': time_data,
        'count_data': count_data,
    }
    return render_template('X-admin/welcome1.html', data=data)


def play_time_statistics():
    # data = UserPlay.query(UserPlay.content_id, func.sum(UserPlay.play_time)).Group_by(UserPlay.content_id).all()
    data = db.session.query(UserPlay.content_id, func.sum(UserPlay.play_time)).group_by(
        UserPlay.content_id).all()
    tmp = sorted(data, key=lambda x: x[1], reverse=True)[:10]

    x_data = [i[0] for i in tmp]
    y_data = [{
        'value': int(v[1]),
        'name': ContentMain.query.get(v[0]).title,
        'itemStyle': {
            'color': color_list[k]
        },
    } for k, v in enumerate(tmp) if len(v) == 2]

    return {
        'x_data': x_data,
        'y_data': y_data,
    }


def play_count_statistics():
    data = db.session.query(UserPlay.content_id, func.count(UserPlay.user_id)).group_by(
        UserPlay.content_id).all()
    tmp = sorted(data, key=lambda x: x[1], reverse=True)[:10]

    x_data = [i[0] for i in tmp]
    y_data = [{
        'value': int(v[1]),
        'name': ContentMain.query.get(v[0]).title,
        'itemStyle': {
            'color': color_list2[k]
        },
    } for k, v in enumerate(tmp) if len(v) == 2]

    return {
        'x_data': x_data,
        'y_data': y_data,
    }


@api.route('/')
@admin_login_data
def video_index():
    if not g.user:
        return redirect(url_for('admin.login'))

    return render_template('X-admin/order-list.html')


@api.route('/data')
@admin_login_data
def video_data():
    if not g.user:
        return redirect(url_for('admin.login'))
    page = int(request.args.get('page'))
    limit = int(request.args.get('limit'))

    paginate = ContentMain.query.order_by(ContentMain.clicks.desc()).paginate(page, limit)

    return {
        'code': 0,
        'msg': '获取用户信息成功',
        'count': paginate.total,
        'data': [i.to_dict() for i in paginate.items],
    }


@api.route('/del_data')
@admin_login_data
def video_del_data():
    if not g.user:
        return redirect(url_for('admin.login'))
    page = int(request.args.get('page'))
    limit = int(request.args.get('limit'))

    paginate = ContentMain.query.filter(ContentMain.status == 0).order_by(ContentMain.clicks.desc()).paginate(page,
                                                                                                             limit)

    return {
        'code': 0,
        'msg': '获取用户信息成功',
        'count': paginate.total,
        'data': [i.to_dict() for i in paginate.items],
    }


@api.route('/del')
@admin_login_data
def video_del():
    if not g.user:
        return redirect(url_for('admin.login'))

    return render_template('X-admin/order-list-del.html')
