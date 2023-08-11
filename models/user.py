
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from base import db
from .common import BaseModels
from models.message import Message


class UserInfo(BaseModels, db.Model):
    """用户信息表"""
    __tablename__ = "user_info"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    nickname = db.Column(db.String(64), nullable=False)  # 用户昵称
    mobile = db.Column(db.String(16))  # 手机号
    avatar_url = db.Column(db.String(256))  # 用户头像路径
    signature = db.Column(db.String(256))  # 签名
    sex = db.Column(db.Enum('0', '1', '2'), default='0')  # 1男  2 女 0 暂不填写
    birth_date = db.Column(db.DateTime)  # 出生日期
    role_id = db.Column(db.Integer)  # 角色id
    is_admin = db.Column(db.SmallInteger, default=0)
    is_streamer = db.Column(db.SmallInteger, default=0)
    active = db.Column(db.SmallInteger, default=0)
    last_message_read_time = db.Column(db.DateTime)

    def new_messages_counts(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient_id=self.id).filter(Message.timestamp > last_read_time).count()

    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'mobile': self.mobile,
            'avatar_url': self.avatar_url,
            'sex': self.sex,
        }


class UserLogin(BaseModels, db.Model):
    """用户登陆表"""
    __tablename__ = "user_login"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    mobile = db.Column(db.String(16), unique=True, nullable=False)  # 手机号
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    user_id = db.Column(db.Integer)  # 用户id
    last_login = db.Column(db.DateTime, default=datetime.now)  # 最后一次登录时间
    last_login_stamp = db.Column(db.Integer)  # 最后一次登录时间

    @property
    def password(self):
        raise AttributeError('密码属性不能直接获取')

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    # 传入的是明文，校验明文和数据库里面的hash之后密码 正确true
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserFollower(BaseModels, db.Model):
    """用户追随表"""
    __tablename__ = "user_follower"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    user_id = db.Column(db.Integer)  # 用户id
    follower_id = db.Column(db.Integer)  # 追随者id
    status = db.Column(db.Enum('0', '1'), default='1')

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "user_id": self.user_id,
            "follower_id": self.follower_id,
        }
        return resp_dict


class UserContent(BaseModels, db.Model):
    """用户发布内容表"""
    __tablename__ = "user_content"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    user_id = db.Column(db.Integer)  # 用户id
    content_id = db.Column(db.Integer)  # 内容id

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "user_id": self.user_id,
            "content_id": self.content_id,
        }
        return resp_dict


class UserAction(BaseModels, db.Model):
    """动作表"""
    __tablename__ = "user_action"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)  # 用户id
    content_id = db.Column(db.Integer)  # 内容id
    action_id = db.Column(db.Integer)  # 动作id


class UserPlay(BaseModels, db.Model):
    """用户播放视频表"""
    __tablename__ = "user_play"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)  # 用户id
    content_id = db.Column(db.Integer)  # 内容id
    play_time = db.Column(db.Float)  # 视频播放时长
