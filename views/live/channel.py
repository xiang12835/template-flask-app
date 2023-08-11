import uuid

from flask import jsonify, request, g

from base import photos, db
from base.redprint import Redprint
from models.channel import Channel
from utils.common import auth_identify
from libs.http_lib import success

api = Redprint('channel')

# 创建直播频道
@api.route('/info', methods=['POST'])
@auth_identify
def channels():
    current_user = g.user
    # requestType = request.form['type']
    channel_name = request.form['channelName']
    topic = request.form['channelTopic']
    description = request.form['description']
    record = False
    if 'recordSelect' in request.form:
        record = True
    chat_enabled = False
    if 'chatEnabled' in request.form:
        chat_enabled = True

    new_uuid = str(uuid.uuid4())

    channel = Channel(current_user.id, new_uuid, channel_name, topic, record, chat_enabled, description)
    # 上传视频直播图片
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename != '':
            filename = photos.save(request.files['photo'], name=str(uuid.uuid4()) + '.')
            channel.image_location = filename
    channel.add(channel)
    return success('channel创建成功',data=channel.to_dict())
