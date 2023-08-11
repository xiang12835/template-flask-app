

import uuid

from base import db
from .common import BaseModels


class Channel(BaseModels, db.Model):
    __tablename__ = "live_channel"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    stream_key = db.Column(db.String(255), unique=True)
    channel_name = db.Column(db.String(255))
    channel_loc = db.Column(db.String(255), unique=True)
    topic = db.Column(db.Integer)  # 类别
    views = db.Column(db.Integer)  # 总播放人数
    current_viewers = db.Column(db.Integer)  # 当前播放人数
    record = db.Column(db.Boolean)  # 是否可以录制回放
    chat_enabled = db.Column(db.Boolean)  # 是否可以聊天
    image_location = db.Column(db.String(255))
    description = db.Column(db.String(2048))
    default_stream_name = db.Column(db.String(255))  # 录制回放的命名
    protected = db.Column(db.Boolean)

    def __init__(self, user_id, stream_key, channel_name, topic, record, chat_enabled, description):
        self.user_id = user_id
        self.stream_key = stream_key
        self.channel_name = channel_name
        self.channel_loc = str(uuid.uuid4())
        self.topic = topic
        self.views = 0
        self.currentViewers = 0
        self.record = record
        self.chat_enabled = chat_enabled
        self.description = description
        self.defaultStreamName = ""
        self.protected = False

    def __repr__(self):
        return '<id %r>' % self.user_id

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'channel_name': self.channel_name,
            'channel_loc': self.channel_loc,
            'topic': self.topic,
            'views': self.views,
            'stream_key': self.stream_key,
            'currentViewers': self.currentViewers,
            'record': self.record,
            'chat_enabled': self.chat_enabled,
            'description': self.description,
        }
