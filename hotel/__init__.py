from datetime import datetime
from traceback import format_exc

from flask import Flask, request

from hotel.api_bp.oauth import oauth_bp
from hotel.api_bp.rooms import rooms_bp
from hotel.api_bp.rooms_types import rooms_types_bp
from hotel.api_bp.users import users_bp
from hotel.api_bp.users_groups import users_groups_bp
from hotel.api_error import APIError
from hotel.common import response_json
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
    app.register_blueprint(rooms_bp, url_prefix="/rooms")
    app.register_blueprint(rooms_types_bp, url_prefix="/rooms/types")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(users_groups_bp, url_prefix="/users/groups")


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
    def page_not_found(e) -> response_json:
        return response_json(err=400, msg="请求报文存在语法错误"), 400

    @app.errorhandler(404)
    def page_not_found(e) -> response_json:
        return response_json(err=404, msg="找不到此资源"), 404

    @app.errorhandler(405)
    def method_not_allowed(e) -> response_json:
        return response_json(err=405, msg="方法不被允许"), 405

    @app.errorhandler(Exception)
    def the_api_error(e) -> response_json:
        if isinstance(e, APIError):
            return response_json(err=e.code, msg=e.message)

        with open("err.log", "a") as f:
            f.write(f"\n{request.url} - {request.remote_addr}")
            f.write(datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
            f.write(format_exc())
            f.write("\n")

        return response_json(err=500, msg="服务器内部错误"), 500
