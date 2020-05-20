from functools import wraps
from os import getenv
from time import time

from flask import g, request
from itsdangerous import BadSignature, TimedJSONWebSignatureSerializer

from hotel.api_error import APIError
from hotel.common import safe_md5
from hotel.my_redis import Redis
from hotel.purview import get_user_purview_from_cache


def get_token() -> str:
    """
    从请求头获取token
    :return:
    """

    try:
        token_type, token = request.headers["Authorization"].split(None, 1)
    except (KeyError, ValueError):
        raise APIError("请重新登录", code=401)

    if token == "null" or token_type.lower() != "bearer":
        raise APIError("请重新登录", code=401)

    return token


def _access_token(user) -> str:
    """
    生成访问令牌
    :param user:
    :return:
    """
    sign = f"{user.phone}-" + safe_md5(f"{user.name}{time()}")
    data = {
        "name": user.name,
        "phone": user.phone,
        "weight": user.user_group.weight
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
        raise APIError("请重新登录", code=401)
    else:
        return data


def login_required(func):
    """
    检查用户的access_token是否合法
    因为有账号才能拿到token，故不考虑，账号不存在的情况

    使用flask的g对象，全局储存 user 数据

    :param func: 使用此装饰器的函数
    :return: 指向新函数，或者返回错误
    """

    @wraps(func)
    def wrapper(*args, **kw):
        # 验证 token 是否有效
        token = get_token()
        g.session = Redis.hgetall(token)
        if not g.session: raise APIError("请重新登录", code=401)
        return func(*args, **kw)

    return wrapper


def login_sudo_required(func):
    """
    检查用户的access_token是否合法
    因为有账号才能拿到token，故不考虑，账号不存在的情况

    使用flask的g对象，全局储存 user 数据

    :param func: 使用此装饰器的函数
    :return: 指向新函数，或者返回错误
    """

    @wraps(func)
    def wrapper(*args, **kw):

        # 验证 token 是否有效
        token = get_token()
        g.session = Redis.hgetall(token)

        if not g.session: raise APIError("请重新登录", code=401)
        if int(g.session["weight"]) != 0: raise APIError("该用户非超级管理员")
        return func(*args, **kw)

    return wrapper


def login_purview_required(*purview):
    """
    接口需要权限
    :param purview:
    :return:
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):

            token = get_token()  # 验证 token 是否有效
            g.session = Redis.hgetall(token)

            if not g.session: raise APIError("请重新登录", code=401)
            purview_required = get_user_purview_from_cache()

            for item in purview: purview_required = purview_required[item]
            if not purview_required: raise APIError("该用户组没有权限")

            return func(*args, **kw)

        return wrapper

    return decorator
