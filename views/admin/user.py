
from flask import render_template, current_app, abort, request, g, url_for, redirect

from base.redprint import Redprint
from models.user import UserInfo, UserLogin
from utils.common import admin_login_data
from libs.http_lib import success, error, HttpCode


api = Redprint('user')


@api.route('/')
@admin_login_data
def users_index():
    if not g.user:
        return redirect(url_for('admin.login'))
    # 用户列表  默认获取的是第一页的数据   使用静态模版文件渲染方式默认提取第一页的数据 其他需要跳转页码可以有对应的接口获取对应的数据
    # paginate = None
    # try:
    #     paginate = UserInfo.query.filter(
    #         UserInfo.create_time != '').order_by(
    #         UserInfo.create_time.desc()).paginate(1, 10, False)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     abort(404)
    # data = [i.to_dict() for i in paginate.items]
    # print(data)
    # print(paginate.total)
    return render_template('X-admin/member-list1.html')


@api.route('/data')
@admin_login_data
def users_data():
    if not g.user:
        return redirect(url_for('admin.login'))
    # 动态表格的数据接口
    page = int(request.args.get('page'))
    limit = int(request.args.get('limit'))
    paginate = None
    try:
        paginate = UserInfo.query.filter(
            UserInfo.create_time != '').order_by(
            UserInfo.create_time.desc()).paginate(page, limit, False)
    except Exception as e:
        current_app.logger.error(e)
    return {
        'code': 0,
        'msg': '获取用户信息成功',
        'count': paginate.total,
        'data': [i.to_dict() for i in paginate.items],
    }


@api.route('/update', methods=['post'])
@admin_login_data
def update():
    if not g.user:
        return redirect(url_for('admin.login'))
    dict_data = request.json
    id = dict_data.get('id')
    field = dict_data.get('field')
    value = dict_data.get('value')
    user = UserInfo.query.get(id)
    if field == 'nickname':
        user.nickname = value
    if field == 'sex':
        user.sex = '2' if value else '1'
    user.update()
    return success('用户信息修改成功')


@api.route('/del/<int:user_id>', methods=['post'])
@admin_login_data
def delete(user_id):
    """停用用户"""
    if not g.user:
        return redirect(url_for('admin.login'))
    user = UserLogin.query.filter_by(user_id=user_id).first()
    if not user:
        return error(HttpCode.parmas_error, '查无此用户')
    user.status = '0'
    user.update()
    return success('用户停用成功')


@api.route('/statistics')
@admin_login_data
def users_statistics():
    if not g.user:
        return redirect(url_for('admin.login'))
    return render_template('X-admin/welcome_user.html')


@api.route('/add', methods=['GET', 'POST'])
@admin_login_data
def add():
    if not g.user:
        return redirect(url_for('admin.login'))
    if request.method == "GET":
        return render_template('X-admin/member-add.html')

    data_dict = request.json
    phone = data_dict.get('phone')
    username = data_dict.get('username')
    password = data_dict.get('password')

    # 创建用户
    user = UserInfo()
    user.mobile = phone
    user.nickname = username
    user.add(user)
    user_login = UserLogin()
    user_login.mobile = phone
    user_login.password = password
    user_login.add(user_login)
    if not all([user, user_login]):
        return error(HttpCode.db_error, '用户创建失败')
    return success('用户添加成功')
