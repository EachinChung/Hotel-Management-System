from datetime import datetime

from flask import Blueprint, g, request
from sqlalchemy.exc import IntegrityError

from hotel.common import response_json
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
    try:
        data = request.get_json()
        room_type = data["room_type"]
        number_of_beds = data["number_of_beds"]
        number_of_people = data["number_of_people"]
        price_tag = data["price_tag"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    room_type = RoomType(
        room_type=room_type,
        number_of_beds=number_of_beds,
        number_of_people=number_of_people,
        price_tag=price_tag,
        update_datetime=datetime.today(),
        operator=g.session["name"]
    )
    try:
        db.session.add(room_type)
        db.session.commit()
    except IntegrityError:
        return response_json(err=1, msg="房间类型重复")

    return response_json({}, msg=f"{room_type.room_type} 添加成功")


@room_type_bp.route("/update", methods=["POST"])
@login_purview_required
def update_room_type():
    """
    修改房型
    :return:
    """
    try:
        data = request.get_json()
        room_type_id = data["room_type_id"]
        the_type = data["room_type"]
        number_of_beds = data["number_of_beds"]
        number_of_people = data["number_of_people"]
        price_tag = data["price_tag"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    room_type = RoomType.query.get(room_type_id)
    if room_type is None:
        return response_json(err=1, msg="该房型不存在")

    room_type.room_type = the_type
    room_type.number_of_beds = number_of_beds
    room_type.number_of_people = number_of_people
    room_type.price_tag = price_tag
    room_type.update_datetime = datetime.today()
    room_type.operator = g.session["name"]

    try:
        db.session.add(room_type)
        db.session.commit()
    except IntegrityError:
        return response_json(err=1, msg="房间类型重复")

    return response_json(msg=f"{the_type} 修改成功")


@room_type_bp.route("/del", methods=["POST"])
@login_purview_required
def del_room_type():
    """
    删除房型
    :return:
    """
    try:
        data = request.get_json()
        room_type_id = data["room_type_id"]
    except (KeyError, TypeError):
        return response_json({}, err=1, msg="缺少参数")

    room_type = RoomType.query.get(room_type_id)
    if room_type is None:
        return response_json({}, err=1, msg="该房型不存在")

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
