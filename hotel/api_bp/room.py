from datetime import datetime

from flask import Blueprint, g
from sqlalchemy.exc import IntegrityError

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
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
    room_id, room_type_id, floor = get_request_body("room_id", "room_type_id", "floor")
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
        raise APIError("房间重复")

    return response_json(msg=f"{room_id} 添加成功")


@room_bp.route("/update", methods=["POST"])
@login_purview_required
def update_room():
    """
    修改房间
    :return:
    """

    data = get_request_body("room_id", "room_type_id", "floor", "is_discounted")

    room = Room.query.get(data[0])
    if room is None:
        raise APIError("该房间不存在")

    room.floor = data[2]
    room.room_type_id = data[1]
    room.is_discounted = data[3]
    room.update_datetime = datetime.today()
    room.operator = g.session["name"]

    db.session.add(room)
    db.session.commit()

    return response_json(msg=f"{data[0]} 修改成功")


@room_bp.route("/del", methods=["POST"])
@login_purview_required
def del_room():
    """
    删除房间
    :return:
    """
    room_id = get_request_body("room_id")

    room = Room.query.get(room_id)
    if room is None:
        raise APIError("该房间不存在")

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
    page, per_page = get_request_body("page", "per_page")

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
