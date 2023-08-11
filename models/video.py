from base import db

class VideoInfo(db.Model):
    __tablename__ = "video_info"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imdb_id = db.Column(db.String(16), unique=True)  # IMDB数据库中电影的唯一ID
    movie_id = db.Column(db.String(16))  # 电影ID
    tmdb_id = db.Column(db.String(16))  # TMDB数据库中电影的唯一ID
    title = db.Column(db.String(255))  # 标题
    little_img_src = db.Column(db.String(255))  # 排行小图片路径  45*67
    detail_url = db.Column(db.String(255))  # 详情页面url
    rating = db.Column(db.String(255))  # 排行得分
    time = db.Column(db.String(255))  # 时长
    catogery = db.Column(db.String(255))  # 分类
    show_info = db.Column(db.String(255))  # 上映信息
    summary_text = db.Column(db.String(255))  # 摘要描述
    director = db.Column(db.String(255))  # 摘要描述
    writers = db.Column(db.String(255))  # 作者
    stars = db.Column(db.String(255))  # 明星
    storyline = db.Column(db.String(255))  # 情节描述
    img_src = db.Column(db.String(255))  # 182-268
    video_img_src = db.Column(db.String(255))  # 477-268
    video_href = db.Column(db.String(255))  # 视频详情url
    true_video_url = db.Column(db.String(1024))  # 真实视频url
    local_video_src = db.Column(db.String(255))  # 本地视频路径
    new_video_url = db.Column(db.String(255))  # 服务器视频url
    local_img_src = db.Column(db.String(255))  # 服务器本地imgurl
    new_img_url = db.Column(db.String(255))  # 服务器外网imgurl
    local_video_img_src = db.Column(db.String(255))  # 服务器本地videoimgurl
    new_video_img_url = db.Column(db.String(255))  # 服务器外网vi
    download_timeout = db.Column(db.String(16))
    download_slot = db.Column(db.String(16))
    download_latency = db.Column(db.String(32))
    depth = db.Column(db.String(16))

