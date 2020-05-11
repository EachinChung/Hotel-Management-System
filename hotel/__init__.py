from flask import Flask, jsonify

from hotel.api_bp.oauth import oauth_bp
from hotel.api_bp.room_type import room_type_bp
from hotel.api_bp.user import user_bp
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
    app.register_blueprint(room_type_bp, url_prefix="/room-type")
    app.register_blueprint(user_bp, url_prefix="/user")


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
        return jsonify(message='400 错误 – 请求报文存在语法错误'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(message='404 错误 – 找不到此资源'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(message='405 错误 – 方法不被允许'), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify(message='500 错误 – 服务器内部错误'), 500
