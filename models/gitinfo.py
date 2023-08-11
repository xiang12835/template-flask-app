from base import db
from models.common import BaseModels


class GithubInfo(BaseModels, db.Model):
    """站内信表"""
    __tablename__ = "github_info"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    account = db.Column(db.String(128))  # github 账号
    name = db.Column(db.String(64))  # 名字
    mobile = db.Column(db.String(16))  # 名字
    sex = db.Column(db.Enum('0', '1'), default='0')  # 阅读状态  男0 1女

    def to_dict(self):
        res = {
            "id": self.id,
            "account": self.account,
            "name": self.name,
            "mobile": self.mobile,
            "sex": self.sex,
        }
        return res


class GitUser(BaseModels, db.Model):
    """用户"""
    __tablename__ = "git_user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户编号
    name = db.Column(db.String(32), nullable=False, unique=True)  # 用户昵称
    mobile = db.Column(db.String(16), unique=True, nullable=False)  # 手机号
    password = db.Column(db.String(13), nullable=False)  # 密码
    isadmin = db.Column(db.Enum('0', '1'), default='0')  # 管理员
    role_id = db.Column(db.Integer, default=0)
    last_login_time = db.Column(db.String(32))
    ip = db.Column(db.String(32))

    def to_dict(self):
        res = {
            "id": self.id,
            "name": self.name,
            "mobile": self.mobile,
            "password": self.password,
            "isadmin": self.isadmin,
            "role_id": self.role_id,
            "last_login_time": self.last_login_time,
            "ip": self.ip,
        }
        return res
