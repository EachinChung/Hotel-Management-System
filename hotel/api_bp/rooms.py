from datetime import datetime

from flask import Blueprint, g, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
from hotel.extensions import db
from hotel.models import Room
from hotel.token import login_purview_required

rooms_bp = Blueprint("rooms", __name__)


class RoomsAPI(MethodView):
    @login_purview_required("room", "get")
    def get(self) -> response_json:
        """
        获取所有房间
        :return:
        """
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=2, type=int)

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

    @login_purview_required("room", "add")
    def post(self) -> response_json:
        """
        增加房间
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


class RoomAPI(MethodView):
    @login_purview_required("room", "update")
    def put(self, room_id) -> response_json:
        """
        修改房间
        :param room_id:
        :return:
        """
        room_type_id, floor, is_discounted = get_request_body("room_type_id", "floor", "is_discounted")

        room = Room.query.get(room_id)
        if room is None:
            raise APIError("该房间不存在")

        room.floor = floor
        room.room_type_id = room_type_id
        room.is_discounted = is_discounted
        room.update_datetime = datetime.today()
        room.operator = g.session["name"]

        db.session.add(room)
        db.session.commit()

        return response_json(msg=f"{room_id} 修改成功")

    @login_purview_required("room", "del")
    def delete(self, room_id) -> response_json:
        """
        删除房间
        :param room_id:
        :return:
        """

        room = Room.query.get(room_id)
        if room is None:
            raise APIError("该房间不存在")

        db.session.delete(room)
        db.session.commit()

        return response_json(msg=f"{room_id} 删除成功")


rooms_bp.add_url_rule("/", view_func=RoomsAPI.as_view("rooms"), methods=("GET", "POST"))
rooms_bp.add_url_rule("/<int:room_id>", view_func=RoomAPI.as_view("room"), methods=("PUT", "DELETE"))
