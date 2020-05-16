from flask import Flask

from hotel.api_bp.oauth import oauth_bp
from hotel.api_bp.room import room_bp
from hotel.api_bp.room_type import room_type_bp
from hotel.api_bp.user import user_bp
from hotel.api_bp.user_group import user_group_bp
from hotel.common import response_json
from hotel.api_error import APIError
from hotel.extensions import db


def create_app(config_name=None) -> Flask:
    """
    加载基本配置
    :return:
    """
    app = Flask('hotel')
    app.config.from_pyfile('settings.py')

    # 本地开发由 flask-cors 提供 CORS
    if config_name is None:
        from flask_cors import CORS
        CORS(app)

    register_blueprints(app)
    register_extensions(app)
    register_errors(app)
    return app


def register_blueprints(app) -> None:
    """
    加载蓝本
    :param app:
    :return:
    """
    app.register_blueprint(oauth_bp, url_prefix="/oauth")
    app.register_blueprint(room_bp, url_prefix="/room")
    app.register_blueprint(room_type_bp, url_prefix="/room-type")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(user_group_bp, url_prefix="/user-group")


def register_extensions(app) -> None:
    """
    初始化拓展
    :param app:
    :return:
    """
    db.init_app(app)


def register_errors(app) -> None:
    """
    加载错误页
    :param app:
    :return:
    """

    @app.errorhandler(400)
    def page_not_found(e):
        return response_json(err=400, msg="请求报文存在语法错误"), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return response_json(err=404, msg="找不到此资源"), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return response_json(err=405, msg="方法不被允许"), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return response_json(err=500, msg="服务器内部错误"), 500

    @app.errorhandler(Exception)
    def the_api_error(e):
        """
        处理自定义错误
        :param e:
        :return:
        """
        if isinstance(e, APIError):
            return response_json(err=e.code, msg=e.message)
