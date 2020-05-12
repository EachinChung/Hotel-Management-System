from hashlib import md5
from json import loads

from flask import g, jsonify

from hotel.models import User
from hotel.my_redis import Redis


def safe_md5(s: str) -> str:
    """
    封装的 md5 离散值
    :param s:
    :return:
    """
    # 解决字符串和bytes类型
    if not isinstance(s, bytes):
        s = bytes(s, encoding='utf-8')

    return md5(s).hexdigest().upper()


def get_user_purview():
    """
    获取用户权限
    :return:
    """
    purview = Redis.get(f"{g.session['phone']}-purview")

    if purview is None:
        user = User.query.get(g.session["phone"])
        Redis.set(f"{g.session['phone']}-purview", user.user_group.purview, expire=None)
        purview = loads(user.user_group.purview)
    else:
        purview = loads(purview)

    return purview


def response_json(data: dict = None, err: int = 0, msg: str = "ok") -> jsonify:
    """
    统一响应json的格式
    :param data:
    :param err:
    :param msg:
    :return:
    """
    if data is None: data = {}
    return jsonify(data=data, err=err, msg=msg)
