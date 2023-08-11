
import time

from flask import current_app, redirect, render_template, jsonify, request, session, g, logging, abort

from base import db
from models.gitinfo import GithubInfo, GitUser
from views.index import index_blu
from utils.common import user_login_data
from libs.http_lib import error, HttpCode, success


@index_blu.route('/favicon.ico')
def web_logo():
    return current_app.send_static_file("favicon.ico")


@index_blu.route('/')
@user_login_data
def index():
    if not g.user:
        return redirect('/login')
    return render_template('index/index.html')


@index_blu.route('/github_info')
@user_login_data
def github_info():
    if not g.user:
        return redirect('/login')
    info = GithubInfo.query.all()
    info_list = [i.to_dict() for i in info]
    data = {
        'code': 0,
        'count': len(info_list),
        'data': info_list,
    }
    return jsonify(data)


@index_blu.route('/github_create', methods=['POST'])
@user_login_data
def github_create():
    if not g.user:
        return redirect('/login')
    stu_info = GithubInfo()
    stu_info.name = ''
    stu_info.mobile = g.user.mobile[4:]
    stu_info.account = ''
    # 提交缴费信息到数据库中
    try:
        db.session.add(stu_info)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return error(code=HttpCode.db_error, msg='创建失败')

    return success(msg="创建成功")


@index_blu.route('/github_upgrade', methods=['POST'])
@user_login_data
def github_upgrade():
    if not g.user:
        return redirect('/login')
    dict_data = request.json
    id = dict_data.get('id')
    # print(id)
    field = dict_data.get('field')
    value = dict_data.get('value')
    github_info = GithubInfo.query.get(id)
    if field == 'account':
        github_info.account = value
        github_info.mobile = g.user.mobile[4:]
    if field == 'name':
        github_info.name = value
        github_info.mobile = g.user.mobile[4:]
    if field == 'sex':
        github_info.sex = value
    if field == 'mobile':
        github_info.mobile = value

    try:
        db.session.add(github_info)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return error(code=HttpCode.db_error, msg='数据库查询失败')

    return success(msg='获取数据成功')


@index_blu.route('/login')
def login():
    return render_template('login/login.html')


@index_blu.route('/git_login', methods=['POST'])
def git_login():
    """
    1.获取参数
    2.校验参数
    3.通过手机号取出用户对象
    4.判断用户对象是否存在
    5.判断密码是否正确
    6.记录用户登陆状态
    7.返回前端页面
    :return:
    """
    # 1.获取参数
    dict_data = request.json
    mobile = dict_data.get("userName")
    password = dict_data.get("password")
    # 2.校验参数
    if not all([mobile, password]):
        return error(code=HttpCode.parmas_error, msg='请求参数不完整')

    # 3.通过手机号取出用户对象
    try:
        user = GitUser.query.filter(GitUser.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='数据库查询失败')

    # 4.判断用户对象是否存在
    if not user:
        return error(code=HttpCode.auth_error, msg='用户不存在')

    # 5.判断密码是否正确
    if user.password != password:
        return error(code=HttpCode.parmas_error, msg='密码输入不正确')

    # 获取登录状态   ip  登录时间  存入数据库
    last_login_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    ip = get_request_ip()

    user.last_login_time = last_login_time
    user.ip = ip
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()

    # 6.记录用户登陆状态
    session["user_id"] = user.id
    session["name"] = user.name
    session["mobile"] = user.mobile

    # 7.返回前端页面
    return success(msg='获取数据成功')


def get_request_ip():
    '''获取请求方的ip'''
    try:
        # ip = request.remote_addr
        _ip = request.headers['X-Real-Ip']
        return _ip
    except Exception as e:
        current_app.logger.error(e)


@index_blu.route('/logout')
def logout():
    # 清除session中的数据
    # session.clear()
    session.pop("user_id", "")
    session.pop("name", "")
    session.pop("mobile", "")

    # 返回响应
    return redirect('/login')


@index_blu.route('/week/<int:ass_id>')
def assignment(ass_id):
    if ass_id == 3:
        return render_template('index/lesson1-assignment.html')
    elif ass_id == 4:
        return render_template('index/lesson2-assignment.html')
    elif ass_id == 6:
        return render_template('index/django1-ass.html')
    else:
        abort(404)
