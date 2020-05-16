from flask import Blueprint

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
from hotel.models import User
from hotel.token import create_token, get_token, validate_token

oauth_bp = Blueprint("oauth", __name__)


@oauth_bp.route("/login", methods=["POST"])
def login_bp() -> response_json:
    """
    登陆接口，获取令牌
    return: json
    """

    phone, password = get_request_body("phone", "password")

    if not phone.isdigit():
        raise APIError("提交信息不合法")

    user = User.query.get(phone)
    if user is None:
        raise APIError("该账号不存在")

    if not user.validate_password(password):
        raise APIError("密码错误")

    response_data = {
        "name": user.name,
        "token": create_token(user),
        "user_group": user.user_group.group_name
    }

    return response_json(response_data)


@oauth_bp.route('/refresh')
def refresh_token() -> response_json:
    """
    刷新令牌
    :return: json
    """
    data = validate_token(get_token())
    user = User.query.get(data["phone"])
    if user is None: raise APIError("该账号已被注销")
    return response_json(create_token(user))
