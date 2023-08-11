import datetime
import subprocess

from flask import jsonify, request, abort, redirect

from base import db
from base.redprint import Redprint
from models.channel import Channel
from models.content import ContentMain
from models.stream import Stream
from models.user import UserInfo
from utils.constants import NGINX_RTMP_ADDRESS
from utils.date_util import normalize_date
from base.settings import  video_loc, url_suffix

api = Redprint('rtmp')

# 设置nginx的on_publish   加入权限验证
# on_publish http://验证服务器域名/check; #授权地址 推流时会请求
# on_publish_done  http://验证服务器域名/check; #推流结束时请求


@api.route('/rtmp')
def rtmp():

    data = {
        'time_data': 1,
        'count_data': 2,
    }
    return jsonify(data)


@api.route('/auth-key', methods=['POST'])
def streamkey_check():
    """
    推流权限认证，验证name是否是推流的key，如果需要验证账号密码可以加入相应的参数进行拼接
    :return:
    """
    key = request.form['name']
    channel = Channel.query.filter_by(stream_key=key).first()  # 查看直播 streamkey 是否存在
    current_time = datetime.datetime.now()
    if channel is not None:
        # 判断用户是否存在
        user = UserInfo.query.filter_by(id=channel.user_id).first()
        if user is not None:
            if user.is_streamer:
                if not user.active:
                    msg = {
                        'time': str(current_time),
                        'status': 'Unauthorized User - User has been Disabled',
                        'key': str(key)
                    }
                    print(msg)
                    return abort(400)
                msg = {
                    'time': str(current_time),
                    'status': 'Successful Key Auth',
                    'key': str(key),
                    'channel_name': str(channel.channel_name),
                    'user_id': str(channel.user_id)
                }
                print(msg)
                exist_streams = Stream.query.filter_by(channel_id=channel.id).all()
                # 查询视频流是否存在  如果存在直接删除
                if exist_streams:
                    for stream in exist_streams:
                        db.session.delete(stream)
                    db.session.commit()
                default_stream_name = normalize_date(str(current_time))
                if channel.default_stream_name != "":
                    default_stream_name = channel.default_stream_name
                new_stream = Stream(key, default_stream_name, int(channel.id), channel.topic)
                db.session.add(new_stream)
                db.session.commit()
                # if adaptive:  # 可以通过一个字段拆分判断选择哪儿一种推流方式, 重定向到对应的rtmp服务器走相应的逻辑
                print(channel.channel_loc)
                return redirect('rtmp://' + NGINX_RTMP_ADDRESS + '/stream-data/' + channel.channel_loc, code=302)
            else:
                msg = {
                    'time': str(current_time),
                    'status': 'Unauthorized User - Missing Streamer Role',
                    'key': str(key)
                }
                print(msg)
                return abort(400)
        else:
            msg = {
                'time': str(current_time),
                'status': 'Unauthorized User - No Such User',
                'key': str(key)
            }
            print(msg)
            return abort(400)
    else:
        msg = {
            'time': str(current_time),
            'status': 'Failed Key Auth',
            'key':str(key)
        }
        print(msg)
        return abort(400)


@api.route('/auth-user', methods=['POST'])
def user_auth_check():
    """
    推流验证，验证上面推流的key是否有效
    :return:
    """
    key = request.form['name']
    request_channel = Channel.query.filter_by(channel_loc=key).first()

    if request_channel is not None:
        authed_stream = Stream.query.filter_by(stream_key=request_channel.stream_key).first()

        if authed_stream is not None:
            msg = {
                'time': str(datetime.datetime.now()),
                'status': 'Successful Channel Auth',
                'key': str(request_channel.stream_key),
                'channelName': str(request_channel.channel_name)
            }
            print(msg)
            input_location = "rtmp://" + NGINX_RTMP_ADDRESS + ":1935/live/" + request_channel.channel_loc
            return 'ok'

        else:
            msg = {
                'time': str(datetime.datetime.now()),
                'status': 'Failed Channel Auth. No Authorized Stream Key',
                'channelName': str(key)
            }
            return abort(400)
    else:
        msg = {
            'time': str(datetime.datetime.now()),
            'status': 'Failed Channel Auth. Channel Loc does not match Channel',
            'channelName': str(key)
        }
        return abort(400)


@api.route('/deauth-user', methods=['POST'])
def user_deauth_check():
    """
    推流结束时请求
    :return:
    """
    key = request.form['name']

    authed_stream = Stream.query.filter_by(stream_key=key).all()

    # channelRequest = Channel.query.filter_by(stream_key=key).first()

    if authed_stream is not []:
        # 结束之后删除推流数据
        for stream in authed_stream:
            db.session.delete(stream)
            db.session.commit()

        return 'OK'
    else:
        msg = {
            'time': str(datetime.datetime.now()),
            'status': 'Stream Closure Failure - No Such Stream',
            'key': str(key)
        }
        print(msg)
        db.session.close()
        return abort(400)


@api.route('/playback', methods=['POST'])
def playback_auth_handler():
    stream = request.form['name']
    clientIP = request.form.get('addr')
    print(stream, clientIP)

    if clientIP == "127.0.0.1" or clientIP == "localhost":
        return 'OK'
    else:
        channel = Channel.query.filter_by(channel_loc=stream).first()
        print(channel)
        if channel is not None:
            print(channel.protected)
            if channel.protected:
                username = request.form['username']
                secureHash = request.form['hash']

                # 可以加入用户权限验证，没有用户就看不了

                return 'OK'
            else:
                # print('ok')
                return 'Ok'
    return 'ok'


@api.route('/auth-record', methods=['POST'])
def record_auth_check():
    key = request.form['name']
    channel = Channel.query.filter_by(channel_loc=key).first()
    # current_time = datetime.datetime.now()

    if channel is not None:
        user = UserInfo.query.filter_by(id=channel.user_id).first()

        if channel.record is True and user is not None:
            contents = ContentMain.query.filter_by(channel_id=channel.id).all()
            if contents:
                for content in contents:
                    db.session.delete(content)
                    db.session.commit()

            new_content = ContentMain()
            new_content.channel_id = channel.id
            new_content.title = channel.channel_name
            new_content.user_id = channel.user_id
            new_content.category_id = channel.topic

            new_content.add(new_content)

            return 'OK'
    return abort(400)


@api.route('/deauth-record', methods=['POST'])
def rec_Complete_handler():
    key = request.form['name']
    path = request.form['path']

    channel = Channel.query.filter_by(channel_loc=key).first()

    content = ContentMain.query.filter_by(channel_id=channel.id).first()

    video_path = path.replace('/tmp/', channel.channel_loc + '/')
    image_path = video_path.replace('.flv', '.png')
    gif_path = video_path.replace('.flv', '.gif')
    video_path = video_path.replace('.flv', '.mp4')

    content.img_src = url_suffix + video_loc + image_path
    content.cover_url = url_suffix + video_loc + image_path
    content.gif_path = url_suffix + video_loc + gif_path
    content.content_url = url_suffix + video_loc + video_path

    content.update()

    return 'OK'
