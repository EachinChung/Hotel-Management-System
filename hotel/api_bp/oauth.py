from datetime import datetime

from flask import Blueprint, request
from flask.views import MethodView
from sqlalchemy import func, insert

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
from hotel.extensions import db
from hotel.models import LoginLog, User
from hotel.token import create_token, get_token, validate_token

oauth_bp = Blueprint("oauth", __name__)


class OauthAPI(MethodView):

    @staticmethod
    def post() -> response_json:
        """
        登陆接口，获取令牌
        return: json
        """

        phone, password = get_request_body("phone", "password")
        if not phone.isdigit(): raise APIError("提交信息不合法")

        user = User.query.get(phone)
        if user is None: raise APIError("该账号不存在")
        if not user.validate_password(password): raise APIError("密码错误")
        if not user.is_activation: raise APIError("该账号暂为冻结状态，请联系管理员")

        response_data = {
            "name": user.name,
            "token": create_token(user),
            "user_group": user.user_group.group_name
        }

        db.session.execute(insert(LoginLog, {
            "ip": func.inet_aton(request.remote_addr),
            "user": user.name,
            "user_phone": phone,
            "user_group": user.user_group.group_name,
            "datetime": datetime.today()
        }))
        db.session.commit()

        return response_json(response_data)

    @staticmethod
    def patch() -> response_json:
        """
        刷新令牌
        :return: json
        """
        data = validate_token(get_token())
        user = User.query.get(data["phone"])
        if user is None: raise APIError("该账号已被注销")
        if not user.is_activation: raise APIError("该账号暂为冻结状态，请联系管理员")
        return response_json(create_token(user))


oauth_bp.add_url_rule(rule="", view_func=OauthAPI.as_view("oauth"), methods=("POST", "PATCH"))
