from uuid import uuid4

from base import db
from .channel import Channel


class Stream(db.Model):
    __tablename__ = "live_stream"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255))
    channel_id = db.Column(db.Integer)
    stream_key = db.Column(db.String(255))
    stream_name = db.Column(db.String(255))
    topic = db.Column(db.Integer)
    current_viewers = db.Column(db.Integer)
    total_viewers = db.Column(db.Integer)

    def __init__(self, stream_key, stream_name, channel_id, topic):
        self.uuid = str(uuid4())
        self.stream_key = stream_key
        self.stream_name = stream_name
        self.channel_id = channel_id
        self.current_viewers = 0
        self.total_viewers = 0
        self.topic = topic

    def __repr__(self):
        return '<id %r>' % self.id

    def add_viewer(self):
        self.current_viewers = self.current_viewers + 1
        db.session.commit()

    def remove_viewer(self):
        self.current_viewers = self.current_viewers - 1
        db.session.commit()

    def serialize(self):
        # 如果设计到推流分为不同的方案  可以设置参数处理
        channel = Channel.query.get(self.channel_id)
        channel_loc = channel.channel_loc
        user_id = channel.user_id
        stream_url = '/live/' + channel_loc + '/index.m3u8'
        return {
            'id': self.id,
            'uuid': self.uuid,
            'channel_id': self.channel_id,
            'channel_loc': channel_loc,
            'user_id': user_id,
            'stream_page': '/view/' + channel_loc + '/',
            'stream_url': stream_url,
            'stream_name': self.stream_name,
            'thumbnail': '/stream-thumb/' + channel_loc + '.png',
            'gif_location': '/stream-thumb/' + channel_loc + '.gif',
            'topic': self.topic,
            'current_viewers': self.current_viewers,
            'total_viewers': self.total_viewers,
        }
