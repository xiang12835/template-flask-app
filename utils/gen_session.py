

import hashlib


def gen_session(user_id, video_id, cur_time):
    m = hashlib.md5()
    m.update(str(user_id).encode("utf8"))
    m.update(str(video_id).encode("utf8"))
    m.update(str(cur_time).encode("utf8"))
    session = m.hexdigest()
    return session
