from datetime import datetime

from flask import Blueprint, g
from sqlalchemy.exc import IntegrityError

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
from hotel.extensions import db
from hotel.models import RoomType
from hotel.token import login_purview_required

room_type_bp = Blueprint("room-type", __name__)


@room_type_bp.route("/add", methods=["POST"])
@login_purview_required
def add_room_type():
    """
    添加房型
    :return:
    """

    data = get_request_body("room_type", "number_of_beds", "number_of_people", "price_tag")

    room_type = RoomType(
        room_type=data[0],
        number_of_beds=data[1],
        number_of_people=data[2],
        price_tag=data[3],
        update_datetime=datetime.today(),
        operator=g.session["name"]
    )

    try:
        db.session.add(room_type)
        db.session.commit()
    except IntegrityError:
        raise APIError("房间类型重复")

    return response_json({}, msg=f"{data[0]} 添加成功")


@room_type_bp.route("/update", methods=["POST"])
@login_purview_required
def update_room_type():
    """
    修改房型
    :return:
    """

    data = get_request_body("room_type_id", "room_type", "number_of_beds", "number_of_people", "price_tag")

    room_type = RoomType.query.get(data[0])
    if room_type is None: raise APIError("该房型不存在")

    room_type.room_type = data[1]
    room_type.number_of_beds = data[2]
    room_type.number_of_people = data[3]
    room_type.price_tag = data[4]
    room_type.update_datetime = datetime.today()
    room_type.operator = g.session["name"]

    try:
        db.session.add(room_type)
        db.session.commit()
    except IntegrityError:
        raise APIError("房间类型重复")

    return response_json(msg=f"{data[1]} 修改成功")


@room_type_bp.route("/del", methods=["POST"])
@login_purview_required
def del_room_type():
    """
    删除房型
    :return:
    """
    room_type_id = get_request_body("room_type_id")

    room_type = RoomType.query.get(room_type_id)
    if room_type is None: raise APIError("该房型不存在")

    db.session.delete(room_type)
    db.session.commit()
    return response_json({}, msg=f"{room_type.room_type} 删除成功")


@room_type_bp.route("/list")
@login_purview_required
def room_type_list() -> response_json:
    """
    房间类型列表
    :return:
    """

    def _decode(item):
        return dict(
            room_type_id=item.id,
            room_type=item.room_type,
            number_of_beds=item.number_of_beds,
            number_of_people=item.number_of_people,
            price_tag=item.price_tag,
            update_datetime=item.update_datetime,
            operator=item.operator
        )

    room_types = RoomType.query.all()
    items = list(map(_decode, room_types))
    return response_json(dict(items=items))
