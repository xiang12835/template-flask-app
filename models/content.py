
from base import db
from models.common import BaseModels
from models.user import UserInfo
from utils.date_util import datetime2str


class ContentCategory(BaseModels, db.Model):
    """内容类型表"""
    __tablename__ = "content_category"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(16), nullable=False, unique=True)


class ContentMain(BaseModels, db.Model):
    """内容主表"""
    __tablename__ = "content_main"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    title = db.Column(db.String(256), nullable=False)  # 内容标题
    user_id = db.Column(db.Integer)  # 用户id 内容发布人id
    user_nickname = db.Column(db.String(64))  # 用户昵称
    category_id = db.Column(db.Integer)  # 类别id
    content_url = db.Column(db.String(256))  # 内容url地址
    img_src = db.Column(db.String(255))  # 图片url
    cover_url = db.Column(db.String(256))  # 内容封面url地址
    content_time = db.Column(db.Integer)  # 内容时长
    # 当前审核状态 如果为0代表审核通过，1代表审核中，2审核未通过，3代表未审核
    audit_status = db.Column(db.Integer, default=3)
    clicks = db.Column(db.Integer, default=0)  # 播放次数
    likes = db.Column(db.Integer, default=0)  # 点赞数
    Favorites = db.Column(db.Integer, default=0)  # 收藏数
    tag = db.Column(db.String(512))  # 内容标签
    description = db.Column(db.String(512))  # 内容描述
    movie_id = db.Column(db.Integer)
    channel_id = db.Column(db.Integer)
    gif_path = db.Column(db.String(255))

    def json(self):
        user = UserInfo.query.get(self.user_id)
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "user_nickname": user.nickname,
            "user_avatar": user.avatar_url,
            "category_id": self.category_id,
            "content_url": self.content_url,
            "cover_url": self.cover_url,
            "content_time": self.content_time,
            "clicks": self.clicks if self.clicks else 0,
            "tag": self.tag,
            "description": self.description,
        }
        return resp_dict

    def to_dict(self):
        user = UserInfo.query.get(self.user_id)
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id,
            "user_nickname": user.nickname,
            "user_avatar": user.avatar_url,
            "category": self.category,
            "content_url": self.content_url,
            "cover_url": self.cover_url,
            "content_time": self.content_time,
            "clicks": self.clicks if self.clicks else 0,
            "likes": self.like_count(),
            "Favorites": self.collect_count(),
            "tag": self.tag,
            "description": self.description,
        }
        return resp_dict

    def to_rank_dict(self):
        rank_dict = {
            "id": self.id,
            "title": self.title,
        }
        return rank_dict

    @property
    def category(self):
        return ContentCategory.query.get(self.category_id).category_name

    def like_count(self):
        return ContentLike.query.filter_by(content_id=self.id, status=1).count()

    def collect_count(self):
        return ContentCollect.query.filter_by(content_id=self.id, status=1).count()


class ContentCollect(BaseModels, db.Model):
    """内容收藏表"""
    __tablename__ = "content_collect"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_id = db.Column(db.Integer)  # 视频id
    user_id = db.Column(db.Integer)  # 用户id


class ContentLike(BaseModels, db.Model):
    """内容点赞表"""
    __tablename__ = "content_like"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_id = db.Column(db.Integer)  # 视频id
    user_id = db.Column(db.Integer)  # 用户id


class ContentComment(BaseModels, db.Model):
    """内容评论表"""
    __tablename__ = "content_comment"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    content_id = db.Column(db.Integer, index=True)  # 视频id
    commenter_id = db.Column(db.Integer, index=True)  # 用户id 内容发布人id 评论发布者
    comment_content = db.Column(db.String(512), nullable=False)  # 评论内容
    commenter_nickname = db.Column(db.String(64), nullable=False)  # 用户昵称
    commenter_avatar_url = db.Column(db.String(256))  # 用户头像路径
    good = db.Column(db.Integer, default=0)
    bad = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'commenter_id': self.commenter_id,
            'commenter_nickname': self.commenter_nickname,
            'commenter_avatar_url': self.commenter_avatar_url,
            'comment_content': self.comment_content,
            'create_time': self.create_time,
            'good': self.good,
            'bad': self.bad,
        }

    def reply_info(self):
        replies = ContentReply.query.filter_by(
            content_id=self.content_id,
            comment_id=self.id,
            commenter_id=self.commenter_id,
        ).order_by(ContentReply.create_time.desc()).all()
        return [i.to_dict() for i in replies]

    def comment_reply_json(self):
        return {
            'id': self.id,
            'commenter_id': self.commenter_id,
            'commenter_nickname': self.commenter_nickname,
            'commenter_avatar_url': self.commenter_avatar_url,
            'comment_content': self.comment_content,
            'create_time': datetime2str(self.create_time),
            'good': self.good,
            'bad': self.bad,
            'replies': self.reply_info(),
        }


class ContentReply(BaseModels, db.Model):
    """内容回复表"""
    __tablename__ = "content_reply"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    content_id = db.Column(db.Integer, index=True)  # 视频id
    comment_id = db.Column(db.Integer, index=True)  # 评论id
    replyer_id = db.Column(db.Integer, index=True)  # 回复id
    commenter_id = db.Column(db.Integer, index=True)  # 用户id 内容发布人id 评论发布者
    replyer_nickname = db.Column(db.String(64))  # 用户昵称
    replyer_avatar_url = db.Column(db.String(256))  # 用户头像路径
    reply_content = db.Column(db.String(512), nullable=False)  # 回复内容
    good = db.Column(db.Integer, default=0)
    bad = db.Column(db.Integer, default=0)

    def __init__(self, content_id, comment_id, replyer_id, commenter_id, replyer_nickname, replyer_avatar_url,
                 reply_content):
        self.content_id = content_id
        self.comment_id = comment_id
        self.replyer_id = replyer_id
        self.commenter_id = commenter_id
        self.replyer_nickname = replyer_nickname
        self.replyer_avatar_url = replyer_avatar_url
        self.reply_content = reply_content

    def __repr__(self):
        return f"用户id为<{self.replyer_id}>的用户对视频ID为<{self.content_id}>的视频中用户ID为<{self.commenter_id}>的用户" \
            f"作的评论ID为<{self.comment_id}>的评论做的回复为<{self.reply_content}>"

    def to_dict(self):
        return {
            'id': self.id,
            'content_id': self.content_id,
            'comment_id': self.comment_id,
            'replyer_id': self.replyer_id,
            'commenter_id': self.commenter_id,
            'replyer_nickname': self.replyer_nickname,
            'replyer_avatar_url': self.replyer_avatar_url,
            'reply_content': self.reply_content,
            'create_time': datetime2str(self.create_time),
            'good': self.good,
            'bad': self.bad,
        }
        # return {key: getattr(self, key) for key in
        #         ['id', 'content_id', 'comment_id', 'replyer_id', 'commenter_id', 'replyer_nickname',
        #          'replyer_avatar_url', 'reply_content', 'create_time', 'good', 'bad']}


class ContentBarrage(BaseModels, db.Model):
    """内容弹幕表"""
    __tablename__ = "content_barrage"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    content_id = db.Column(db.Integer)  # 视频id
    user_id = db.Column(db.Integer)  # 用户id 内容发布人id 评论发布者
    barrage_content = db.Column(db.String(256), nullable=False)  # 弹幕内容
    play_time = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'barrage_content': self.barrage_content,
            'play_time': self.play_time,
        }


class ContentAudit(BaseModels, db.Model):
    """审核表"""
    __tablename__ = "content_audit"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_id = db.Column(db.Integer)  # 审核内容id
    user_id = db.Column(db.Integer)  # 审核者

    # 当前审核状态 如果为0代表审核通过，1代表审核中，2审核未通过，3代表未审核
    audit_status = db.Column(db.Integer, default=3)
    reason = db.Column(db.String(256))  # 未通过原因，status = 3 的时候使用


class ActionCategory(BaseModels, db.Model):
    """动作类型表"""
    __tablename__ = "action_category"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_name = db.Column(db.String(16), nullable=False, unique=True)  # 1播放 2收藏 3点赞


class StationLetters(BaseModels, db.Model):
    """站内信表"""
    __tablename__ = "station_letters"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 用户id
    letter_content = db.Column(db.String(256), nullable=False)  # 消息内容
    letter_category = db.Column(db.String(64))  # 消息类型
    user_id = db.Column(db.Integer)  # 接收人id
    content_id = db.Column(db.Integer)  # 内容id
    read_status = db.Column(db.Enum('0', '1'), default='0')  # 阅读状态  0未读 1已读


class CommentGood(BaseModels, db.Model):
    """评论点赞"""
    __tablename__ = "comment_good"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, index=True)
    comment_id = db.Column(db.Integer, index=True)


class CommentBad(BaseModels, db.Model):
    """评论点反"""
    __tablename__ = "comment_bad"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, index=True)
    comment_id = db.Column(db.Integer, index=True)


class ReplyGood(BaseModels, db.Model):
    """回复点赞"""
    __tablename__ = "reply_good"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, index=True)
    reply_id = db.Column(db.Integer, index=True)


class ReplyBad(BaseModels, db.Model):
    """回复点反"""
    __tablename__ = "reply_bad"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, index=True)
    reply_id = db.Column(db.Integer, index=True)
