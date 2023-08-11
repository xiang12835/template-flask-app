import os

BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), "."))

site_protocol = 'http://'

site_address = '10.20.36.137'

url_suffix = 'http://10.20.36.137:10080'
video_loc = '/videos/'
img_loc = '/stream-thumb/'
gif_loc = '/stream-thumb/'



def setup_lg(app, log_handler):
    app.logger.addHandler(log_handler)


def setup_db(app, db):
    db.init_app(app)


def setup_redis(app):
    pass

def setup_http(app):
    # @app.before_request
    # def before_request():
    #     interface = request.path
    #     print(interface)
    #     if '/login' in interface:
    #         return None
    #     else:
    #         if request.method == 'OPTIONS':
    #             pass
    #         else:
    #             print('**'*50)
    #             redirect(interface)

    @app.after_request
    def add_header(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Request-Method'] = "POST, PUT, GET, OPTIONS, DELETE"
        return response

