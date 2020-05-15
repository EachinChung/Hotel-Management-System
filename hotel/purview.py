from json import dumps, loads

from flask import g

from hotel.extensions import db
from hotel.models import PurviewRoom, PurviewRoomType, PurviewUser, User
from hotel.my_redis import Redis


def init_user_purview(user_group_id) -> None:
    """
    初始化权限
    :param user_group_id:
    :return:
    """
    purview_user = PurviewUser(user_group_id=user_group_id)
    purview_room = PurviewRoom(user_group_id=user_group_id)
    purview_room_type = PurviewRoomType(user_group_id=user_group_id)

    db.session.add(purview_user)
    db.session.add(purview_room)
    db.session.add(purview_room_type)
    db.session.commit()


def get_user_purview_from_mysql(user_group_id, recursive: bool = False) -> dict:
    """
    从 MySQL 获取权限
    :param recursive:
    :param user_group_id:
    :return:
    """
    purview_user = PurviewUser.query.get(user_group_id)
    purview_room = PurviewRoom.query.get(user_group_id)
    purview_room_type = PurviewRoomType.query.get(user_group_id)

    if not recursive and purview_user is None:
        init_user_purview(user_group_id)
        return get_user_purview_from_mysql(user_group_id, True)

    if recursive and purview_user is None:
        return {}

    purview = {
        "user": purview_user.get_dict(),
        "room": purview_room.get_dict(),
        "room-type": purview_room_type.get_dict()
    }

    return purview


def get_user_purview_from_cache() -> dict:
    """
    从缓存获取用户权限
    :return:
    """
    purview = Redis.get(f"{g.session['phone']}-purview")

    if purview is None:
        user = User.query.get(g.session["phone"])
        purview = get_user_purview_from_mysql(user.user_group_id)
        Redis.set(f"{user.phone}-purview", dumps(purview), expire=None)
    else:
        purview = loads(purview)

    return purview
