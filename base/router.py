from views.hello_view import hello_bp
from views.demo_api import demo_bp

from views.admin import admin_blu
from views.video import video_blu
from views.auth import auth_blu
from views.index import index_blu
from views.message import msg_blu
from views.live import live_blu
from views.user import user_blu

def register_router(app):
    app.register_blueprint(hello_bp)
    app.register_blueprint(demo_bp)

    app.register_blueprint(admin_blu)
    app.register_blueprint(video_blu)
    app.register_blueprint(auth_blu)
    app.register_blueprint(index_blu)
    app.register_blueprint(msg_blu)
    app.register_blueprint(live_blu)
    app.register_blueprint(user_blu)


    
