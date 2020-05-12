from json import loads

from flask import Blueprint, request

from hotel.common import response_json
from hotel.diy_error import DiyError
from hotel.models import User
from hotel.token import create_token, get_token, validate_token

oauth_bp = Blueprint("oauth", __name__)


@oauth_bp.route("/login", methods=["POST"])
def login_bp() -> response_json:
    """
    登陆接口，获取令牌
    return: json
    """

    try:
        data = request.get_json()
        phone = data["phone"]
        password = data["password"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    if not phone.isdigit():
        return response_json(err=1, msg="提交信息不合法")

    user = User.query.get(phone)
    if user is None:
        return response_json(err=1, msg="该账号不存在")

    if not user.validate_password(password):
        return response_json(err=1, msg="密码错误")

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

    try:  # 验证 token 是否通过
        data = validate_token(get_token())
    except DiyError as err:
        return response_json(err=err.code, msg=err.message)

    return response_json(create_token(User.query.get(data["phone"])))
