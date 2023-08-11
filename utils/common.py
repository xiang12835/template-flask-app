from flask import session, current_app, g, request
from functools import wraps
from flask import request, current_app, make_response
from utils.auth_helper import Auth
from libs.http_lib import error, HttpCode



def admin_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # 获取用户编号
        user_id = session.get("user_id")
        # 查询用户对象
        user = None
        if user_id:
            try:
                from models.user import UserInfo
                user = UserInfo.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        # 使用g对象保存
        g.user = user

        return view_func(*args, **kwargs)

    return wrapper


def user_login_data(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # 获取用户编号
        user_id = session.get("user_id")
        # print(user_id)
        # 查询用户对象
        user = None
        if user_id:
            try:
                from models.gitinfo import GitUser
                user = GitUser.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        # 使用g对象保存
        g.user = user

        return view_func(*args, **kwargs)

    return wrapper


def auth_identify(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        response = Auth().identify(request)
        if response.get('code') == 200:
            user_id = response.get('data')['user_id']
            # 查询用户对象
            user = None
            if user_id:
                try:
                    from models.user import UserInfo
                    user = UserInfo.query.get(user_id)
                except Exception as e:
                    current_app.logger.error(e)
            # 使用g对象保存
            g.user = user

            return view_func(*args, **kwargs)

        else:
            return error(HttpCode.auth_error, response.get('msg'))

    return wrapper


def youke_identify(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        response = Auth().identify(request)
        if response.get('code') == 200:
            user_id = response.get('data')['user_id']
            # 查询用户对象
            user = None
            if user_id:
                try:
                    from models.user import UserInfo
                    user = UserInfo.query.get(user_id)
                except Exception as e:
                    current_app.logger.error(e)
            # 使用g对象保存
            g.user = user

            return view_func(*args, **kwargs)

        else:
            g.user = None
            return view_func(*args, **kwargs)

    return wrapper


def check_file_type(filename):
    """
    检查文件类型
    :param filename:
    :return:
    """
    file_type = ['jpg', 'png', 'PNG']
    # 获取文件后缀
    ext = filename.split('.')[1]
    # 判断文件是否是允许上传得类型
    if ext in file_type:
        return True
    else:
        return False
