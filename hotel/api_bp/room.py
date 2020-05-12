from datetime import datetime

from flask import Blueprint, g, request
from sqlalchemy.exc import IntegrityError

from hotel.common import response_json
from hotel.extensions import db
from hotel.models import Room
from hotel.token import login_purview_required

room_bp = Blueprint("room", __name__)


@room_bp.route("/add", methods=["POST"])
@login_purview_required
def add_room():
    """
    添加房间
    :return:
    """
    try:
        data = request.get_json()
        room_id = data["room_id"]
        room_type_id = data["room_type_id"]
        floor = data["floor"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    room = Room(
        id=room_id,
        floor=floor,
        room_type_id=room_type_id,
        update_datetime=datetime.today(),
        operator=g.session["name"]
    )

    try:
        db.session.add(room)
        db.session.commit()
    except IntegrityError:
        return response_json(err=1, msg="房间重复")

    return response_json(msg=f"{room_id} 添加成功")


@room_bp.route("/update", methods=["POST"])
@login_purview_required
def update_room():
    """
    修改房间
    :return:
    """
    try:
        data = request.get_json()
        room_id = data["room_id"]
        room_type_id = data["room_type_id"]
        floor = data["floor"]
        is_discounted = data["is_discounted"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    room = Room.query.get(room_id)
    if room is None:
        return response_json(err=1, msg="该房间不存在")

    room.room_type_id = room_type_id
    room.floor = floor
    room.is_discounted = is_discounted
    room.update_datetime = datetime.today()
    room.operator = g.session["name"]

    db.session.add(room)
    db.session.commit()

    return response_json(msg=f"{room_id} 修改成功")


@room_bp.route("/del", methods=["POST"])
@login_purview_required
def del_room():
    """
    删除房间
    :return:
    """
    try:
        data = request.get_json()
        room_id = data["room_id"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    room = Room.query.get(room_id)
    if room is None:
        return response_json(err=1, msg="该房间不存在")

    db.session.delete(room)
    db.session.commit()

    return response_json(msg=f"{room_id} 删除成功")


@room_bp.route("/list", methods=["POST"])
@login_purview_required
def room_list() -> response_json:
    """
    房间列表
    :return:
    """
    try:
        data = request.get_json()
        page = data["page"]
        per_page = data["per_page"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    def _decode(item):
        return dict(
            id=item.id,
            floor=item.floor,
            room_type=item.room_type.room_type,
            is_discounted=item.is_discounted,
            update_datetime=item.update_datetime,
            operator=item.operator
        )

    rooms = Room.query.paginate(page=page, per_page=per_page)
    items = list(map(_decode, rooms.items))

    return response_json(dict(
        items=items,
        page=rooms.page,
        per_page=rooms.per_page,
        pages=rooms.pages,
        total=rooms.total
    ))
