
import re

from flask import request, current_app, make_response, g

from base import redis_store
from models.user import UserLogin, UserInfo
from views.user import user_blu
from utils.captcha_util import captcha
from utils.auth_helper import Auth
from utils.common import auth_identify
from utils.constants import IMAGE_CODE_REDIS_EXPIRES
from libs.http_lib import error, HttpCode, success

from libs.logger import json_log
user_action_log = json_log('user_action', 'logs/user_action.log')

@user_blu.route('/logout', methods=['POST'])
def logout():
    """
    # 退出登录(restful)
    # 请求路径: /passport/logout
    # 请求方式: POST
    # 请求参数: 无
    """
    response = Auth().identify(request)
    if response.get('code') == 200:
        user_id = response.get('data')['user_id']
        # 查询用户对象
        # 查询redis中的值  删除token相关信息
        try:
            redis_store.delete("jwt_token:%s" % user_id)
        except Exception as e:
            current_app.logger.error(e)
            return error(code=HttpCode.db_error, msg='redis删除token错误')

        user_action_log.warning({
            'user_id': user_id,
            'url': '/passport/logout',
            'method': 'post',
            'msg': 'logout',
            'event': 'logout',
        })
        # 返回响应
        return success(msg="退出登录成功")

    else:
        return success(msg=response.get('msg'))


@user_blu.route('/login', methods=['POST'])
def login():
    """
    登录接口
    :return:
    """
    data_dict = request.form
    mobile = data_dict.get('mobile')
    password = data_dict.get('password')
    img_code_id = data_dict.get("img_code_id")
    img_code = data_dict.get("img_code")
    # 判断参数对不对 需要有些验证
    # 2.校验参数
    if not all([mobile, password, img_code_id, img_code]):
        return error(code=HttpCode.parmas_error, msg='参数不完整')

    # 3.通过手机号取出用户对象
    try:
        user_login = UserLogin.query.filter(UserLogin.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='查询手机号异常')
    # 验证拿到的这个手机号  是否在我们的登录信息中存在  异常捕获
    # user_login = UserLogin.query.filter(UserLogin.mobile == mobile).first()
    # 判断我们的用户信息不在返回错误的响应码
    if not user_login:
        return error(code=HttpCode.db_error, msg='用户不存在')
    try:
        redis_img_code = redis_store.get(f'img_code: {img_code_id}')
        # print(redis_img_code)
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='验证码数据库查询异常')
    if not redis_img_code:
        return error(code=HttpCode.parmas_error, msg='验证码不存在')
    if img_code.lower() != redis_img_code.lower():
        return error(code=HttpCode.parmas_error, msg='验证码匹配不成功')
    return Auth().authenticate(mobile, password)


@user_blu.route('/register', methods=['POST'])
def register():
    """
    注册接口
    :return: code msg
    """
    data_dict = request.form
    mobile = data_dict.get('mobile')
    password = data_dict.get('password')
    img_code_id = data_dict.get('img_code_id')  # cur_id
    img_code = data_dict.get('img_code')  # 填写的code

    if not all([mobile, password, img_code_id, img_code]):
        return error(code=HttpCode.parmas_error, msg='注册所需参数不能为空')

    # 2.1验证手机号格式
    if not re.match('1[3456789]\\d{9}', mobile):
        return error(code=HttpCode.parmas_error, msg='手机号格式不正确')

    # 3.通过手机号取出redis中的验证码
    redis_img_code = None
    # 从redis取出img_code_id对应的验证码
    try:
        redis_img_code = redis_store.get(f'img_code: {img_code_id}')
    except Exception as e:
        current_app.logger.errer(e)

    if not redis_img_code:
        return error(HttpCode.parmas_error, 'redis图片验证码获取失败')

    if img_code.lower() != redis_img_code.lower():
        return error(HttpCode.parmas_error, '图片验证码不正确')

    user_info = UserInfo()
    user_info.mobile = mobile
    user_info.nickname = mobile
    user_info.add(user_info)

    user_login = UserLogin()
    user_login.mobile = mobile
    user_login.password = password
    user_login.user_id = user_info.id
    user_login.add(user_login)

    return success('注册成功')


@user_blu.route('/image_code')
def img_code():
    """
    生成图像验证码
    :return: 图片的响应
    """
    # 1.获取请求参数,args是获取?后面的参数
    cur_id = request.args.get('cur_id')
    pre_id = request.args.get('pre_id')
    # 2.生成图片验证码
    name, text, img_data = captcha.captcha.generate_captcha()
    # 3.保存到redis
    try:
        redis_store.set(f'img_code: {cur_id}', text, IMAGE_CODE_REDIS_EXPIRES)
        # 判断是否有上一个uuid,如果存在则删除
        if pre_id:
            redis_store.delete(f'img_code: {pre_id}')
    except Exception as e:
        current_app.logger.error(e)
        return error(HttpCode.db_error, 'redis存储失败')
    # 4. 返回图片验证码
    response = make_response(img_data)
    response.headers["Content-Type"] = "image/jpg"

    return response


@user_blu.route('/check_mobile', methods=['POST'])
def check_mobile():
    """
    验证手机号
    # 请求路径: /passport/check_mobile
    # 请求方式: POST
    # 请求参数: mobile
    :return:code,msg
    """
    data_dict = request.form
    mobile = data_dict.get('mobile')

    try:
        users = UserLogin.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='查询用户信息异常')

    if mobile in [i.mobile for i in users]:
        return error(code=HttpCode.parmas_error, msg='手机号已存在，请重新输入')

    return success(msg=f'{mobile}，此手机号可以使用')
