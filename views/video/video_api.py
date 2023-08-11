
import datetime

import faiss
import logging
import random
import time
import tensorflow as tf
from tensorflow.keras import layers
from flask import current_app, g, request, session, jsonify

from base import redis_store
from models.content import ContentMain, ContentBarrage, ContentComment, ContentLike, ContentCollect, ContentReply, \
    CommentGood, CommentBad, ReplyGood, ReplyBad
from models.user import UserAction, UserFollower, UserPlay
from utils import constants
from utils.common import auth_identify, youke_identify
from utils.constants import MOVIES_REDIS_EXPIRES
from utils.gen_session import gen_session
from libs.hbase_lib import HappyHbase, color_list, color_list2
from libs.logger import json_log
from views.video import video_blu
from libs.http_lib import success, error, HttpCode

# setup_logger('user_action', 'logs/user_action.log')
user_action_log = json_log('user_action', 'logs/user_action.log')


@video_blu.route("/recommend", methods=['GET'])
@youke_identify
def recommend():
    """
    # 获取推荐视频信息
    # 请求路径: /video/recommend
    # 请求方式: GET
    :return:
    """
    if g.user:
        user_action_log.warning({
            'user_id': g.user.id,
            'url': f'/video/recommend',
            'method': 'get',
            'msg': 'video recommend',
            'event': 'recommend',
        })
        user_id = g.user.id
        movie_ids = guess_movies(user_id)
        videos = [ContentMain.query.filter_by(movie_id=i).first() for i in movie_ids]
        return success('获取推荐数据成功', data=[i.json() for i in videos])
    videos = ContentMain.query.filter_by(audit_status=0).all()
    choice_videos = random.sample(videos, 7)
    detail_info = []
    for i in choice_videos:
        detail_info.append(i.json())

    return success(msg='获取推荐信息成功', data=detail_info)


@video_blu.route("/hot")
@youke_identify
def hot():
    """
    # 获取热点视频信息
    # 请求路径: /video/hot
    # 请求方式: GET
    :return:
    """
    if g.user:
        user_action_log.warning({
            'user_id': g.user.id,
            'url': f'/video/hot',
            'method': 'get',
            'msg': 'video hot',
            'event': 'hot',
        })
    videos = ContentMain.query.filter_by(audit_status=0).all()
    choice_videos = random.sample(videos, 8)
    detail_info = []
    for i in choice_videos:
        detail_info.append(i.json())
    return success(msg='获取热点视频成功', data=detail_info)


@video_blu.route("/game")
@youke_identify
def game():
    """
    # 获取游戏视频信息
    # 请求路径: /video/game
    # 请求方式: GET
    :return:
    """
    if g.user:
        user_action_log.warning({
            'user_id': g.user.id,
            'url': f'/video/game',
            'method': 'get',
            'msg': 'video game',
            'event': 'hot',
        })
    games = ContentMain.query.filter(ContentMain.audit_status == 0, ContentMain.category_id == 2).all()
    choice_games = random.sample(games, 8)
    detail_info = []
    for i in choice_games:
        detail_info.append(i.json())
    return success(msg='获取游戏视频成功', data=detail_info)


@video_blu.route("/film_list")
def film_list():
    """
    # 获取电影视频信息
    # 请求路径: /video/film_list
    # 请求方式: GET
    :return:
    """
    user_action_log.warning(f'{g.user.id}获取电影视频列表信息')
    random_num = random.randint(1, 10)
    paginate = ContentMain.query.filter(ContentMain.status == 0, ContentMain.category_id == 1).paginate(random_num, 8)
    count = ContentMain.query.count()
    items = paginate.items
    detail_info = []
    for i in items:
        detail_info.append(i.json())
    data = {
        'count': count,
        "data": detail_info,
    }
    return success(msg='获取电影视频列表信息成功', data=data)


@video_blu.route('/rank')
def rank():
    """
    获取首页排行榜信息
    # 请求路径: /video/rank
    # 请求方式: GET
    :return:  json数据
        code: 0
        data:[{"id": id,"title": title},{}...,{"id": id,"title": title}]  len=10
    """
    rank_video = []
    # 查询前10条热门
    try:
        rank_video = ContentMain.query.filter(ContentMain.status == 0).order_by(ContentMain.clicks.desc()).limit(
            constants.CLICK_RANK_MAX_NEWS).all()
    except Exception as e:
        current_app.logger.error(e)
    if rank_video:
        # 将视频内容对象列表转成,字典列表
        rank_video_list = []
        for video in rank_video:
            rank_video_list.append(video.to_rank_dict())

        data = {
            "data": rank_video_list,
        }
        return success(msg='获取排行榜信息成功', data=data)
    else:
        return error(code=HttpCode.db_error, msg='未获取top10视频，查询有误')


@video_blu.route('/like/<int:video_id>', methods=['GET', 'POST'])
@auth_identify
def like(video_id):
    """
    点赞
    :param video_id:
    :return:
    """
    if request.method == 'GET':
        user_id = g.user.id
        # 点赞
        like = ContentLike.query.filter_by(content_id=video_id, user_id=user_id, status=1).first()
        return success(msg='获取点赞信息成功', data={'like': 1 if like else 0})

    data_dict = request.form
    user_id = g.user.id
    like = data_dict.get('like')
    try:
        like_event = ContentLike.query.filter_by(content_id=video_id, user_id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='查询点赞出错')
    if like_event:
        like_event.status = 1 if like == '1' else 0
        like_event.update()
        if like_event.status == 0:
            user_action_log.warning({
                'user_id': user_id,
                'url': f'/video/like/{video_id}',
                'method': 'post',
                'msg': 'video cancel like',
                'event': 'no_like',
            })
            return success(msg='取消点赞成功')
        else:
            user_action_log.warning({
                'user_id': user_id,
                'url': f'/video/like/{video_id}',
                'method': 'post',
                'msg': 'video like',
                'event': 'like',
            })
            return success(msg='点赞成功')
    like_event = ContentLike()
    like_event.user_id = user_id
    like_event.content_id = video_id
    like_event.status = 1 if like == '1' else 0
    like_event.add(like_event)
    if like_event.status == 0:
        user_action_log.warning({
            'user_id': user_id,
            'url': f'/video/like/{video_id}',
            'method': 'post',
            'msg': 'video cancel like',
            'event': 'no_like',
        })
        return success(msg='取消点赞成功')
    else:
        user_action_log.warning({
            'user_id': user_id,
            'url': f'/video/like/{video_id}',
            'method': 'post',
            'msg': 'video like',
            'event': 'like',
        })
        return success(msg='点赞成功')


@video_blu.route('/collect/<int:video_id>', methods=['GET', 'POST'])
@auth_identify
def collect(video_id):
    """
    收藏
    :param video_id:
    :return:
    """
    if request.method == 'GET':
        user_id = g.user.id
        collect = ContentCollect.query.filter_by(content_id=video_id, user_id=user_id, status=1).first()
        return success(msg='获取收藏信息成功', data={'collect': 1 if collect else 0})

    data_dict = request.form
    user_id = g.user.id
    collect = data_dict.get('collect')
    try:
        collect_event = ContentCollect.query.filter_by(content_id=video_id, user_id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='查询收藏出错')
    if collect_event:
        collect_event.status = 1 if collect == '1' else 0
        collect_event.update()
        if collect_event.status == 0:
            user_action_log.warning({
                'user_id': user_id,
                'url': f'/video/collect/{video_id}',
                'method': 'post',
                'msg': 'video cancel collect',
                'event': 'no_collect',
            })
            return success(msg='取消收藏成功')
        else:
            user_action_log.warning({
                'user_id': user_id,
                'url': f'/video/collect/{video_id}',
                'method': 'post',
                'msg': 'video collect',
                'event': 'collect',
            })
            return success(msg='收藏成功')
    collect_event = ContentCollect()
    collect_event.user_id = user_id
    collect_event.content_id = video_id
    collect_event.status = 1 if collect == '1' else 0
    collect_event.add(collect_event)

    if collect_event.status == 0:
        user_action_log.warning({
            'user_id': user_id,
            'url': f'/video/collect/{video_id}',
            'method': 'post',
            'msg': 'video cancel collect',
            'event': 'no_collect',
        })
        return success(msg='取消收藏成功')
    else:
        user_action_log.warning({
            'user_id': user_id,
            'url': f'/video/collect/{video_id}',
            'method': 'post',
            'msg': 'video collect',
            'event': 'collect',
        })
        return success(msg='收藏成功')


@video_blu.route('/follow/<int:video_id>', methods=['GET', 'POST'])
@auth_identify
def follow(video_id):
    """
    关注
    :param video_id:
    :return:
    """
    if request.method == 'GET':
        user_id = g.user.id
        # 查询视频
        video = ContentMain.query.get(video_id)
        video_user_id = video.user_id
        # 关注
        follow = UserFollower.query.filter_by(user_id=video_user_id, follower_id=user_id, status='1').first()

        return success(msg='获取关注信息成功', data={'follow': 1 if follow else 0})

    data_dict = request.form
    user_id = g.user.id
    video = ContentMain.query.get(video_id)
    video_user_id = video.user_id
    follow = data_dict.get('follow')
    try:
        follow_event = UserFollower.query.filter_by(user_id=video_user_id, follower_id=user_id).first()
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='查询收藏出错')
    if follow_event:
        follow_event.status = '1' if follow == '1' else '0'
        follow_event.update()
        if follow_event.status == '0':
            user_action_log.warning({
                'user_id': user_id,
                'url': f'/video/follow/{video_id}',
                'method': 'post',
                'msg': 'video cancel follow',
                'event': 'no_follow',
            })
            return success(msg='取消关注成功')
        else:
            user_action_log.warning({
                'user_id': user_id,
                'url': f'/video/follow/{video_id}',
                'method': 'post',
                'msg': 'video follow',
                'event': 'follow',
            })
            return success(msg='关注成功')
    else:
        follow_event = UserFollower()
        follow_event.user_id = user_id
        follow_event.follower_id = video_user_id
        follow_event.status = '1' if follow == '1' else '0'
        follow_event.add(follow_event)
        if follow_event.status == '0':
            user_action_log.warning({
                'user_id': user_id,
                'url': f'/video/follow/{video_id}',
                'method': 'post',
                'msg': 'video cancel follow',
                'event': 'no_follow',
            })
            return success(msg='取消关注成功')
        else:
            user_action_log.warning({
                'user_id': user_id,
                'url': f'/video/follow/{video_id}',
                'method': 'post',
                'msg': 'video follow',
                'event': 'follow',
            })
            return success(msg='关注成功')


@video_blu.route('/related/<int:video_id>')
@auth_identify
def related(video_id):
    """
    # 获取视频相关视频信息
    # 请求路径: /video/related/<int:video_id>
    # 请求方式: GET
    :param video_id:
    :return:
    """
    # 查询视频
    try:
        video = ContentMain.query.get(video_id)
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg="视频查询失败")

    if video:
        tag = video.tag
        videos = ContentMain.query.filter(ContentMain.tag.contains(tag), ContentMain.status == 1,
                                          ContentMain.id != video_id).all()
        if len(videos) < 5:
            return success(msg='相关视频获取成功', data=[i.json() for i in videos])
        else:
            tmp = random.sample(videos, 5)
            return success(msg='获取视频详情信息成功', data=[i.json() for i in tmp])
    else:
        return error(code=HttpCode.db_error, msg='没有查到相关视频，查询有误')


@video_blu.route('/destroy/<int:video_id>', methods=['POST'])
@auth_identify
def destroy(video_id):
    """
    视频销毁接口，获取用户观看视频的播放时间
    :param video_id, play_time， tab
    :return:
    """
    # 获取当前用户观看视频的时间
    play_time = request.form.get('play_time')
    type = request.form.get('type')
    cur_time = request.form.get('cur_time')
    # 获取用户的信息
    user_id = g.user.id
    session = gen_session(user_id, video_id, cur_time)
    if type == 'end':
        user_action_log.warning({
            'user_id': user_id,
            'video_id': video_id,
            'url': f'/video/destroy/{video_id}',
            'method': 'post',
            'msg': 'video end',
            'event': 'end',
            'session': session,
            'play_time': play_time,
        })
        # 查询视频
        try:
            video = ContentMain.query.get(video_id)
        except Exception as e:
            current_app.logger.error(e)
            return error(code=HttpCode.db_error, msg="视频查询失败")
        if not video:
            return error(code=HttpCode.db_error, msg="没有获取对应视频信息")

        # 查询当前状态的用户观看时长是否存在
        exist_user_play = UserPlay.query.filter_by(user_id=user_id, content_id=video_id).first()
        if not exist_user_play:
            user_play = UserPlay()
            user_play.user_id = user_id
            user_play.content_id = video_id
            user_play.play_time = float(play_time) if play_time else 0
            user_play.add(user_play)
        else:
            exist_user_play.play_time = float(play_time) if play_time else 0
            exist_user_play.update()
        return success(msg=f'用户退出播放成功，获取用户id:{user_id}观看视频id:{video_id}的播放时间')

    elif type == 'start':

        user_action_log.warning({
            'user_id': user_id,
            'video_id': video_id,
            'url': f'/video/destroy/{video_id}',
            'method': 'post',
            'msg': 'video start',
            'event': 'start',
            'session': session,
            'play_time': play_time,
        })

        return success(msg=f'用户开始播放成功，用户id:{user_id}开始观看视频id:{video_id}')

    else:

        user_action_log.warning({
            'user_id': user_id,
            'video_id': video_id,
            'url': f'/video/destroy/{video_id}',
            'method': 'post',
            'msg': 'video stop',
            'event': 'stop',
            'session': session,
            'play_time': play_time,
        })

        return success(msg=f'用户停止播放成功，用户id:{user_id}停止观看视频id:{video_id}')


@video_blu.route('/detail/<int:video_id>')
@auth_identify
def play(video_id):
    """
    # 获取视频详情信息
    # 请求路径: /video/detail/<int:video_id>
    # 请求方式: GET
    :param video_id:
    :return:
    """
    # 获取用户的信息
    user_id = g.user.id
    user_action_log.warning({
        'user_id': user_id,
        'video_id': video_id,
        'url': f'/video/detail/{video_id}',
        'method': 'get',
        'msg': 'video detail',
        'event': 'play',
    })

    # 查询视频
    try:
        video = ContentMain.query.get(video_id)
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg="视频查询失败")

    if video:
        # 查询有这个视频的话  增加点击量
        if not video.clicks:
            video.clicks = 1
            # 保存到数据库
            video.update()
        else:
            video.clicks += 1
            video.update()

        # 修改用户动作表
        content_id = video.id
        user_action = UserAction()
        user_action.action_id = 1  # 播放数据存储
        user_action.user_id = user_id
        user_action.content_id = content_id
        # 保存到数据库
        user_action.add(user_action)
        # 查询视频播放情况
        try:
            user_play = UserPlay.query.filter_by(user_id=user_id, content_id=content_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return error(code=HttpCode.db_error, msg="视频播放查询失败")

        play_time = user_play.play_time if user_play else 0

        video_info = video.to_dict()
        video_info['play_time'] = play_time

        return success(msg='获取视频详情信息成功', data={'video_info': video_info, 'time': int(time.time())})
    else:
        return error(code=HttpCode.db_error, msg='没有此视频，查询有误')


@video_blu.route('/barrage/<int:video_id>', methods=['GET', 'POST'])
@auth_identify
def barrage(video_id):
    """
    # 获取视频弹幕信息
    # 请求路径: /video/barrage/<int:video_id>
    # 请求方式: GET
    :param video_id:
    :return:
    """
    if request.method == 'GET':
        try:
            video_barrage = ContentBarrage.query.filter_by(content_id=video_id).all()
        except Exception as e:
            current_app.logger.error(e)
            return error(code=HttpCode.db_error, msg="视频弹幕查询失败")

        barrage_list = [i.to_dict() for i in video_barrage]
        return success(msg='获取视频弹幕成功', data=barrage_list)

    user_id = g.user.id
    data_dict = request.form
    play_time = data_dict.get('play_time')
    barrage_content = data_dict.get('barrage_content')

    video_barrage = ContentBarrage()
    video_barrage.content_id = video_id
    video_barrage.user_id = user_id
    video_barrage.play_time = play_time
    video_barrage.barrage_content = barrage_content

    try:
        video_barrage.add(video_barrage)
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='弹幕增加失败')

    user_action_log.warning({'user_id': user_id,
                             'video_id': video_id,
                             'url': f'/video/barrage/{video_id}',
                             'method': 'post', 'msg': 'send barrage',
                             'event': 'barrage',
                             'play_time': play_time})
    return success(msg='发弹幕成功')


@video_blu.route('/comment/<int:video_id>', methods=['GET', 'POST'])
@auth_identify
def comment(video_id):
    """
    评论
    :param video_id:
    :return:
    """
    if request.method == 'GET':
        try:
            video_comments = ContentComment.query.filter_by(content_id=video_id).order_by(
                ContentComment.create_time.desc()).all()
        except Exception as e:
            current_app.logger.error(e)
            return error(code=HttpCode.db_error, msg="视频评论查询失败")
        comment_list = [i.comment_reply_json() for i in video_comments]
        return success(msg='获取视频评论成功', data=comment_list)
    user = g.user
    user_id = user.id
    nickname = user.nickname
    avatar_url = user.avatar_url
    data_dict = request.form
    comment_content = data_dict.get('textarea')
    comment = ContentComment()
    comment.content_id = video_id
    comment.commenter_id = user_id
    comment.comment_content = comment_content
    comment.commenter_avatar_url = avatar_url
    comment.commenter_nickname = nickname

    try:
        comment.add(comment)
    except Exception as e:
        current_app.logger.error(e)
        return error(code=HttpCode.db_error, msg='增加评论失败')

    user_action_log.warning({
        'user_id': user_id,
        'video_id': video_id,
        'url': f'/video/comment/{video_id}',
        'method': 'post',
        'msg': 'send comment',
        'event': 'comment',
    })
    return success(msg='发评论成功')


@video_blu.route('/comment/action/<int:comment_id>', methods=['POST'])
@auth_identify
def comment_action(comment_id):
    data_dict = request.form
    type = data_dict.get('type')
    comment = ContentComment.query.get(comment_id)
    user = g.user
    user_id = user.id
    if type == 'good':
        comment_good = CommentGood.query.filter_by(user_id=user_id, comment_id=comment_id).first()
        if comment_good:
            return success(msg='此评论已经点过赞了，无需继续点赞，你的赞已经添加，稍安勿躁！')
        else:
            comment.good += 1
            comment.update()
            return success(msg='给评论点赞成功')
    else:
        comment_bad = CommentBad.query.filter_by(user_id=user_id, comment_id=comment_id).first()
        if comment_bad:
            return success(msg='此评论已经点过反了，无需继续点反，你的赞反已经添加，稍安勿躁！')
        else:
            comment.bad += 1
            comment.update()
            return success(msg='给评论点反成功')


@video_blu.route('/reply/action/<int:reply_id>', methods=['POST'])
@auth_identify
def reply_action(reply_id):
    data_dict = request.form
    type = data_dict.get('type')
    reply = ContentReply.query.get(reply_id)
    user = g.user
    user_id = user.id
    if type == 'good':
        reply_good = ReplyGood.query.filter_by(user_id=user_id, reply_id=reply_id).first()
        if reply_good:
            return success(msg='此回复已经点过赞了，无需继续点赞，你的赞已经添加，稍安勿躁！')
        else:
            reply.good += 1
            reply.update()
            return success(msg='给回复点赞成功')
    else:
        reply_bad = ReplyBad.query.filter_by(user_id=user_id, reply_id=reply_id).first()
        if reply_bad:
            return success(msg='此回复已经点过反了，无需继续点反，你的赞反已经添加，稍安勿躁！')
        else:
            reply.bad += 1
            reply.update()
            return success(msg='给回复点反成功')


@video_blu.route('/reply/<int:comment_id>', methods=['POST'])
@auth_identify
def reply(comment_id):
    user = g.user
    data_dict = request.form
    reply_content = data_dict.get('textarea')
    comment = ContentComment.query.get(comment_id)
    video_id = comment.content_id
    reply = ContentReply(content_id=video_id, comment_id=comment.comment_id, replyer_id=user.id,
                         commenter_id=comment.commenter_id, replyer_nickname=user.nickname,
                         replyer_avatar_url=user.avatar_url, reply_content=reply_content)
    # reply.content_id = video_id
    # reply.comment_id = comment.comment_id
    # reply.replyer_id = user.id
    # reply.commenter_id = comment.commenter_id
    # reply.replyer_nickname = user.nickname
    # reply.replyer_avatar_url = user.avatar_url
    # reply.reply_content = reply_content
    reply.add(reply)
    user_action_log.warning({
        'user_id': user.id,
        'video_id': video_id,
        'url': f'/video/reply/{comment_id}',
        'method': 'post',
        'msg': 'reply comment',
        'event': 'reply',
    })
    return success(msg='回复成功')


@video_blu.route('hbase')
def hbase():
    data = {'time_x_data': ['4012', '10702', '17308', '5773', '13307', '10680', '6896', '9453', '15493', '10649'],
            'time_y_data': [{'value': 602, 'name': '4012', 'itemStyle': {'color': '#080808'}},
                            {'value': 446, 'name': '10702', 'itemStyle': {'color': '#436EEE'}},
                            {'value': 426, 'name': '17308', 'itemStyle': {'color': '#CD00CD'}},
                            {'value': 426, 'name': '5773', 'itemStyle': {'color': '#CD2990'}},
                            {'value': 420, 'name': '13307', 'itemStyle': {'color': '#CD3700'}},
                            {'value': 408, 'name': '10680', 'itemStyle': {'color': '#CD6839'}},
                            {'value': 396, 'name': '6896', 'itemStyle': {'color': '#CD919E'}},
                            {'value': 394, 'name': '9453', 'itemStyle': {'color': '#CDB38B'}},
                            {'value': 392, 'name': '15493', 'itemStyle': {'color': '#CDC9C9'}},
                            {'value': 390, 'name': '10649', 'itemStyle': {'color': '#D1EEEE'}}],
            'counts_x_data': ['4012', '6662', '10061', '15362', '5773', '10680', '12009', '12401', '16039', '4550'],
            'counts_y_data': [{'value': 15, 'name': '4012', 'itemStyle': {'color': '#FF9966'}},
                              {'value': 13, 'name': '6662', 'itemStyle': {'color': '#FF6666'}},
                              {'value': 12, 'name': '10061', 'itemStyle': {'color': '#FFCCCC'}},
                              {'value': 12, 'name': '15362', 'itemStyle': {'color': '#CC9966'}},
                              {'value': 12, 'name': '5773', 'itemStyle': {'color': '#666666'}},
                              {'value': 11, 'name': '10680', 'itemStyle': {'color': '#CC9999'}},
                              {'value': 11, 'name': '12009', 'itemStyle': {'color': '#FF6666'}},
                              {'value': 11, 'name': '12401', 'itemStyle': {'color': '#FFFF66'}},
                              {'value': 11, 'name': '16039', 'itemStyle': {'color': '#99CC66'}},
                              {'value': 11, 'name': '4550', 'itemStyle': {'color': '#CCFFFF'}}]}

    return success('ok', data=data)


@video_blu.route('statistics')
def statistics():
    hap = HappyHbase(host='10.20.10.168', port=9090)
    play_counts_list, play_times_list = hap.scan_start_stop(b'video')
    hap.close()
    # 封装数据
    # 播放时长排行前10
    time_x_data = [i.get('content_id') for i in play_times_list]
    time_y_data = [{
        'value': v.get('play_time'),
        'name': ContentMain.query.get(v.get('content_id')).first().title,
        'itemStyle': {
            'color': color_list[k]
        }
    } for k, v in enumerate(play_times_list)]
    counts_x_data = [i.get('content_id') for i in play_counts_list]
    counts_y_data = [{
        'value': v.get('play_counts'),
        'name': ContentMain.query.get(v.get('content_id')).first().title,
        'itemStyle': {
            'color': color_list2[k]
        }
    } for k, v in enumerate(play_counts_list)]
    data = {
        'time_x_data': time_x_data,
        'time_y_data': time_y_data,
        'counts_x_data': counts_x_data,
        'counts_y_data': counts_y_data,
    }

    return success('ok', data=data)


# movie_index = faiss.read_index('/opt/cili/data/faiss-movie.index')
# with open('movie_id.txt', 'r') as f:
#     movie_id_list = eval(f.read())

movie_id_list = []

@video_blu.route('/guess')
# @auth_identify
def guess():
    start_time = datetime.datetime.now()
    # user_id = g.user.id
    user_id = 5
    # 从redis取出redis_movies
    redis_movies = None
    try:
        redis_movies = redis_store.get(f'guess_movie_for: {user_id}')
    except Exception as e:
        current_app.logger.errer(e)
    if not redis_movies or len(redis_movies) < 8:
        hap = HappyHbase(host='10.20.36.137', port=19090)
        next_user_id = user_id + 1
        user_embedding = hap.eb_scan_start_stop('user', f'{user_id:06d}', f'{next_user_id:06d}')
        topk = 100
        D, I = movie_index.search(user_embedding, topk)

        guess_movie_ids = [i for i in I[0] if i in movie_id_list]
        two_tower_user_embedding = hap.two_tower_scan_start_stop('user', f'{user_id:06d}', f'{next_user_id:06d}')

        movie_score_dict = {}
        for i in guess_movie_ids:
            score = two_tower_score(i, hap, two_tower_user_embedding)
            if not score:
                continue
            movie_score_dict[i] = score
        # movie_score_dict = {i: two_tower_score(i, hap, two_tower_user_embedding) for i in guess_movie_ids}
        # movie_score_dict = dict(zip(guess_movie_ids, score_list))
        order_movie = sorted(movie_score_dict.items(), key=lambda item: item[1], reverse=True)
        guess_movie_id_list = [int(i[0]) for i in order_movie]

        # 保存到redis
        try:
            redis_store.set(f'guess_movie_for: {user_id}', guess_movie_id_list, MOVIES_REDIS_EXPIRES)
        except Exception as e:
            current_app.logger.error(e)
        hap.close()
        print_cost(start_time, 'all')
        return success(msg='获取推荐成功', data=guess_movie_id_list[:8])
    guess_movie_id_list = redis_movies[:8]
    try:
        redis_store.set(f'guess_movie_for: {user_id}', redis_movies[8:], MOVIES_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
    return success(msg='获取推荐成功', data=guess_movie_id_list)


def print_cost(start_time, msg):
    stop_time = datetime.datetime.now()
    cost = stop_time - start_time
    print(cost, msg)


def two_tower_score(movie_id, hap, two_tower_user_embedding):
    two_tower_movie_embedding = hap.two_tower_scan_start_stop('movie', f'{movie_id:06d}', f'{movie_id + 1:06d}')
    if two_tower_movie_embedding is None:
        return None
    dot_user_movie = tf.reduce_sum(two_tower_user_embedding * two_tower_movie_embedding, axis=1)
    dot_user_movie = tf.expand_dims(dot_user_movie, 1)
    output = layers.Dense(1, activation='sigmoid')(dot_user_movie)
    return output[0][0].numpy()


def guess_movies(user_id):
    redis_movies = None
    try:
        redis_movies = redis_store.get(f'guess_movie_for: {user_id}')
    except Exception as e:
        current_app.logger.errer(e)

    redis_movies_list = eval(redis_movies) if redis_movies else None
    if not redis_movies or len(redis_movies_list) < 7:

        hap = HappyHbase(host='10.20.36.137', port=19090)
        next_user_id = user_id + 1
        user_embedding = hap.eb_scan_start_stop('user', f'{user_id:06d}', f'{next_user_id:06d}')
        topk = 100
        D, I = movie_index.search(user_embedding, topk)

        guess_movie_ids = [i for i in I[0] if i in movie_id_list]
        two_tower_user_embedding = hap.two_tower_scan_start_stop('user', f'{user_id:06d}', f'{next_user_id:06d}')

        movie_score_dict = {}
        for i in guess_movie_ids:
            score = two_tower_score(i, hap, two_tower_user_embedding)
            if not score:
                continue
            movie_score_dict[i] = score
        order_movie = sorted(movie_score_dict.items(), key=lambda item: item[1], reverse=True)
        guess_movie_id_list = [int(i[0]) for i in order_movie]

        try:
            redis_store.set(f'guess_movie_for: {user_id}', str(guess_movie_id_list[7:]), MOVIES_REDIS_EXPIRES)
        except Exception as e:
            current_app.logger.error(e)
        hap.close()
        return guess_movie_id_list[:7]

    guess_movie_id_list = redis_movies_list[:7]
    try:
        redis_store.set(f'guess_movie_for: {user_id}', str(redis_movies_list[7:]), MOVIES_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
    return guess_movie_id_list
