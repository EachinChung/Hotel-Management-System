from hashlib import md5

from flask import jsonify


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
