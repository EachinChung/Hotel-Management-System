from datetime import datetime

from flask import Blueprint, g, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
from hotel.extensions import db
from hotel.models import RoomType
from hotel.token import login_purview_required, login_required

rooms_types_bp = Blueprint("rooms_types", __name__)


@rooms_types_bp.route("/ids")
@login_required
def room_type_id_list() -> response_json:
    """
    房间类型id列表
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


class RoomsTypesAPI(MethodView):

    @login_purview_required("room_type", "get")
    def get(self) -> response_json:
        """
        获取房间类型
        :return:
        """
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=2, type=int)

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

        room_types = RoomType.query.paginate(page=page, per_page=per_page)
        items = list(map(_decode, room_types.items))

        return response_json(dict(
            items=items,
            page=room_types.page,
            per_page=room_types.per_page,
            pages=room_types.pages,
            total=room_types.total
        ))

    @login_purview_required("room_type", "add")
    def post(self):
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


class RoomsTypeAPI(MethodView):
    @login_purview_required("room_type", "update")
    def put(self, room_type_id):
        """
        修改房型
        :return:
        """

        data = get_request_body("room_type", "number_of_beds", "number_of_people", "price_tag")

        room_type = RoomType.query.get(room_type_id)
        if room_type is None: raise APIError("该房型不存在")

        room_type.room_type = data[0]
        room_type.number_of_beds = data[1]
        room_type.number_of_people = data[2]
        room_type.price_tag = data[3]
        room_type.update_datetime = datetime.today()
        room_type.operator = g.session["name"]

        try:
            db.session.add(room_type)
            db.session.commit()
        except IntegrityError:
            raise APIError("房间类型重复")

        return response_json(msg=f"{data[0]} 修改成功")

    @login_purview_required("room_type", "del")
    def delete(self, room_type_id):
        """
        删除房型
        :return:
        """

        room_type = RoomType.query.get(room_type_id)
        if room_type is None: raise APIError("该房型不存在")

        db.session.delete(room_type)
        db.session.commit()
        return response_json({}, msg=f"{room_type.room_type} 删除成功")


rooms_types_bp.add_url_rule("/", view_func=RoomsTypesAPI.as_view("rooms"), methods=("GET", "POST"))
rooms_types_bp.add_url_rule("/<int:room_type_id>", view_func=RoomsTypeAPI.as_view("room"), methods=("PUT", "DELETE"))
