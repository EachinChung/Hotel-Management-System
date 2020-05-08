from os import getenv
from time import time

from flask import request
from itsdangerous import BadSignature, TimedJSONWebSignatureSerializer

from hotel.common import safe_md5
from hotel.diy_error import DiyError
from hotel.my_redis import Redis


def get_token() -> str:
    """
    从请求头获取token
    :return:
    """

    try:
        token_type, token = request.headers["Authorization"].split(None, 1)
    except (KeyError, ValueError):
        raise DiyError("请重新登录", code=403)

    if token == "null" or token_type.lower() != "bearer":
        raise DiyError("请重新登录", code=403)

    return token


def _access_token(user) -> str:
    """
    生成访问令牌
    :param user:
    :return:
    """
    sign = f"{user.phone}-" + safe_md5(f"{user.name}{time()}{getenv('ACCESS_TOKEN')}")
    data = {
        "name": user.name,
        "phone": user.phone,
        "weight": user.user_group.weight,
        "purview": user.user_group.purview
    }

    Redis.hmset(sign, data)
    Redis.expire(sign, 3600)
    return sign


def create_token(user) -> dict:
    """
    生成令牌
    """

    return {
        "accessToken": _access_token(user),
        "refreshToken": generate_token({"phone": user.phone})
    }


def generate_token(data: dict, *, token_type: str = "REFRESH_TOKEN", expires_in: int = 2592000) -> str:
    """
    生成令牌
    :param data: 令牌的内容
    :param token_type: 令牌的类型，每一个类型对应不同的密钥
    :param expires_in: 有效时间
    :return: 令牌
    """
    s = TimedJSONWebSignatureSerializer(getenv(token_type), expires_in=expires_in)
    token = s.dumps(data).decode("ascii")
    return token


def validate_token(token: str, token_type: str = "REFRESH_TOKEN") -> dict:
    """
    验证令牌
    :param token: 令牌
    :param token_type: 令牌类型
    """
    s = TimedJSONWebSignatureSerializer(getenv(token_type))
    try:
        data = s.loads(token)
    except BadSignature:
        raise DiyError("请重新登录", code=403)
    else:
        return data
