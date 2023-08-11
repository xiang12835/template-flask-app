import time
import datetime
import jwt
from flask import current_app

from base import redis_store
from models.user import UserLogin
from utils import constants
from libs.http_lib import error, HttpCode, success
from config.config import Config

from libs.logger import json_log
user_action_log = json_log('user_action', 'logs/user_action.log')

class Auth(object):
    @staticmethod
    def encode_auth_token(user_id, login_time):
        """
        生成认证Token
        :param user_id: int
        :param login_time: int(timestamp)
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'iss': 'Barry',
                'data': {
                    'id': user_id,
                    'login_time': login_time
                }
            }
            return jwt.encode(
                payload,
                Config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            print(e)
            return error(code=HttpCode.auth_error, msg='没有生成对应的token')

    @staticmethod
    def decode_auth_token(auth_token):
        """
        验证Token
        :param auth_token:
        :return: integer|string
        """
        try:
            # payload = jwt.decode(auth_token, Config.SECRET_KEY, leeway=datetime.timedelta(days=1))
            # 取消过期时间验证
            payload = jwt.decode(auth_token, Config.SECRET_KEY, options={'verify_exp': False})
            if 'data' in payload and 'id' in payload['data']:
                return dict(code=HttpCode.ok, payload=payload)
            else:
                raise dict(code=HttpCode.auth_error, msg=jwt.InvalidTokenError)
        except jwt.ExpiredSignatureError:
            return dict(code=HttpCode.auth_error, msg='Token过期')
        except jwt.InvalidTokenError:
            return dict(code=HttpCode.auth_error, msg='无效Token')

    def authenticate(self, mobile, password):
        """
        用户登录，登录成功返回token，写将登录时间写入数据库；登录失败返回失败原因
        :param password:
        :return: json
        """
        user = UserLogin.query.filter_by(mobile=mobile).first()
        if not user:
            return error(code=HttpCode.auth_error, msg='请求的用户不存在')
        else:
            if user.check_password(password):
                login_time = int(time.time())
                try:
                    user.last_login_stamp = login_time
                    # print('👉👉   登陆的时间戳', login_time)
                    user.last_login = datetime.datetime.now()
                    user.update()
                except Exception as e:
                    current_app.logger.error(e)
                    return error(code=HttpCode.db_error, msg='登陆时间查询失败')
                # print('更新用户登陆时间')
                token = self.encode_auth_token(user.user_id, login_time)  # bytes

                token = str(token, encoding="utf-8")
                # print('👉login', token)
                # print(token)
                user_id = user.user_id
                # 存储到redis中
                try:
                    redis_store.set("jwt_token:%s" % user_id, token, constants.JWT_TOKEN_REDIS_EXPIRES)
                except Exception as e:
                    current_app.logger.error(e)
                    return error(code=HttpCode.db_error, msg="token保存redis失败")
                user_action_log.warning({
                    'user_id': user_id,
                    'url': '/passport/login',
                    'method': 'post',
                    'msg': 'login',
                    'event': 'login',
                })

                return success(msg='用户登陆成功', data={"token": token, "user_id": user_id})
            else:
                return error(code=HttpCode.parmas_error, msg='用户登陆密码输入错误')

    def identify(self, request):
        """
        用户鉴权
        :return: list
        """
        auth_header = request.headers.get('Authorization', None)
        if auth_header:
            auth_token_arr = auth_header.split(" ")
            if not auth_token_arr or auth_token_arr[0] != 'JWT' or len(auth_token_arr) != 2:
                return dict(code=HttpCode.auth_error, msg='请求未携带认证信息，认证失败')
            else:
                auth_token = auth_token_arr[1]
                payload_dict = self.decode_auth_token(auth_token)
                if 'payload' in payload_dict and payload_dict.get('code') == 200:
                    payload = payload_dict.get('payload')
                    user_id = payload.get('data').get('id')
                    login_time = payload.get('data').get('login_time')
                    # print('👉👉   解析出的时间戳', login_time)
                    user = UserLogin.query.filter_by(user_id=user_id).first()
                    if not user:  # 未在请求中找到对应的用户
                        return dict(code=HttpCode.auth_error, msg='用户不存在，查无此用户')
                    else:
                        # 通过user取出redis中的token
                        try:
                            # print(user_id)
                            redis_jwt_token = redis_store.get("jwt_token:%s" % user_id)
                            # print('👈redis', redis_jwt_token)
                        except Exception as e:
                            current_app.logger.error(e)
                            return dict(code=HttpCode.db_error, msg="redis查询token失败")
                        if not redis_jwt_token or redis_jwt_token != auth_token:
                            # print('👉👉   解析出来的token', auth_token)
                            return dict(code=HttpCode.auth_error, msg="jwt-token失效")
                        # print(type(user.last_login_stamp), type(login_time))
                        # print(user.last_login_stamp, login_time)
                        if user.last_login_stamp == login_time:

                            return dict(code=HttpCode.ok, msg='用户认证成功', data={"user_id": user.user_id})
                        else:
                            return dict(code=HttpCode.auth_error, msg='用户认证失败，需要再次登陆')
                else:
                    return dict(code=HttpCode.auth_error, msg=payload_dict.get('msg') or '用户认证失败，携带认证参数不合法')
        else:
            return dict(code=HttpCode.auth_error, msg='用户认证失败,请求未携带对应认证信息')
