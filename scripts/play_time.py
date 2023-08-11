
import random
import time
from tqdm import tqdm
import requests

from .user import content_id_list, gen_data


# 需修改成自己的URL(前端项目访问的地址)
HOST_URL = ''


class UserToken:
    def __init__(self, mobile):
        self.mobile = mobile
        self.password = '111111'
        self.login_url = HOST_URL + '/auth/login'
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

    @property
    def token(self):
        # /auth/login 获取token
        while True:
            token_data = self.get_token()
            if self.get_token().get('code') == 200:
                return token_data.get('data').get('token')

    def get_token(self):
        form_data = {
            'mobile': self.mobile,
            'password': self.password,
        }
        try:
            res = requests.post(self.login_url, headers=self.headers, data=form_data)
            if res.status_code == 200:
                return res.json()
        except Exception as e:
            print('Error', e.args)


class PlayAction:
    """生成action日志  请求对应接口"""

    def __init__(self, mobile):
        self.auth_token = 'JWT ' + UserToken(mobile).token  # 用户的认证信息
        self.play_type = PlayType(random.randint(1, 5), random.randint(1, 5)).ran_constitute  # 播放动作类型列表
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': self.auth_token
        }

    def action(self):
        cur_time = random.randint(11111111, 66666666)

        video_ids = content_id_list()
        for video_id in video_ids:
            # print(video_id)
            time.sleep(0.01)
            for type in self.play_type:
                time.sleep(0.01)
                play_time = random.randint(10, 120)
                # print(type)
                self.ping(play_time, cur_time, video_id, type)

    def ping(self, play_time, cur_time, video_id, type):
        form_data = {
            'play_time': play_time,
            'type': type,
            'cur_time': cur_time,
        }
        req_url = HOST_URL + '/video/destroy/' + str(video_id)
        try:
            res = requests.post(req_url, headers=self.headers, data=form_data)
            print(res.json())
        except Exception as e:
            print('Error', e.args)


# 请求接口  记录action日志
# /destroy/<int:video_id>   play_time， tab， cur_id
# session = gen_session(user_id, video_id, cur_time)  记录同一用户的行为
# type start,stop,end  需随机生成播放停止结束事件   start,stop,随机出现  end结尾必须有

class PlayType:
    """['start', 'stop', 'stop', 'end']"""

    def __init__(self, start_count, stop_count):
        self.start_count = start_count  # 随机开始次数1-5
        self.stop_count = stop_count

    @property
    def ran_constitute(self):
        start_list = ['start'] * self.start_count
        stop_list = ['stop'] * self.stop_count
        constitute = start_list + stop_list
        random.shuffle(constitute)
        constitute.append('end')
        return constitute


if __name__ == '__main__':
    # gen_data()  用来获取测试用户的列表  可以随机来控制给哪儿些用户加播放数据
    for mobile in tqdm(gen_data()):
        PlayAction(mobile).action()  # 给所有的视频增加播放事件
        # 可以进类里面修改相应的视频列表来随机给哪儿写视频增加播放数据
