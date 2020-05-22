from datetime import datetime

from flask import Blueprint, g, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from hotel.api_error import APIError
from hotel.common import get_request_body, push_log, response_json
from hotel.extensions import db
from hotel.models import RoomType, RoomTypePrice
from hotel.token import login_purview_required, login_required

rooms_types_bp = Blueprint("rooms_types", __name__)


@rooms_types_bp.route("/ids")
@login_required
def room_type_id_list() -> response_json:
    """
    房间类型id列表
    :return:
    """
    room_types = RoomType.query.all()
    items = list(map(lambda item: dict(room_type_id=item.id, room_type=item.room_type), room_types))
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
        query = request.args.get("query", default="")

        def _decode(item):
            return dict(
                room_type_id=item.id,
                room_type=item.room_type,
                number_of_beds=item.number_of_beds,
                number_of_people=item.number_of_people,
                price_tag=item.price_tag,
                update_datetime=item.update_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                operator=item.operator
            )

        room_types = RoomType.query.filter(
            RoomType.room_type.like(f"%{query}%")
        ).paginate(page=page, per_page=per_page)
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

        push_log(f"添加房型 {room_type.room_type}")
        return response_json(msg=f"{data[0]} 添加成功")


class RoomsTypeAPI(MethodView):
    @login_purview_required("room_type", "update")
    def put(self, room_type_id: int):
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

        push_log(f"修改房型 {room_type.room_type}")
        return response_json(msg=f"{data[0]} 修改成功")

    @login_purview_required("room_type", "del")
    def delete(self, room_type_id: int):
        """
        删除房型
        :return:
        """

        room_type = RoomType.query.get(room_type_id)
        if room_type is None: raise APIError("该房型不存在")

        db.session.delete(room_type)
        db.session.commit()

        push_log(f"删除房型 {room_type.room_type}")
        return response_json(msg=f"{room_type.room_type} 删除成功")


class RoomsTypesPricesAPI(MethodView):
    @login_required
    def get(self, room_type_id: int):
        """
        获取房型价格
        :param room_type_id:
        :return:
        """
        room_type_price = RoomTypePrice.query.filter_by(room_type_id=room_type_id).all()

        def _decode(item):  # 把数据库模型解析为 json
            return dict(
                id=item.id,
                room_type_id=item.room_type_id,
                customer_type=item.customer_type,
                price=item.price,
                update_datetime=item.update_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                operator=item.operator
            )

        items = list(map(_decode, room_type_price))
        return response_json(dict(items=items))

    @login_purview_required("room_type", "set_price")
    def post(self, room_type_id: int):
        """
        新增房型价格
        :param room_type_id:
        :return:
        """
        customer_type, price = get_request_body("customer_type", "price")

        room_type_price = RoomTypePrice(
            room_type_id=room_type_id,
            customer_type=customer_type,
            price=price,
            update_datetime=datetime.today(),
            operator=g.session["name"]
        )

        db.session.add(room_type_price)
        db.session.commit()

        push_log(f"房型{room_type_id}，添加价格")
        return response_json({}, msg=f"{customer_type} 添加成功")


class RoomsTypesPriceAPI(MethodView):
    @login_purview_required("room_type", "set_price")
    def put(self, room_type_id: int, price_id: int):
        customer_type, price = get_request_body("customer_type", "price")

        room_type_price = RoomTypePrice.query.get(price_id)
        if room_type_price is None: raise APIError("该价格类型不存在")
        if room_type_price.room_type_id != room_type_id: raise APIError("提交信息不合法")

        room_type_price.customer_type = customer_type
        room_type_price.price = price
        room_type_price.update_datetime = datetime.today()
        room_type_price.operator = g.session["name"]

        db.session.add(room_type_price)
        db.session.commit()

        push_log(f"房型{room_type_id}，修改价格")
        return response_json(msg=f"{customer_type} 修改成功")

    @login_purview_required("room_type", "set_price")
    def delete(self, room_type_id: int, price_id: int):
        """
        删除房型价格
        :param room_type_id:
        :param price_id:
        :return:
        """
        room_type_price = RoomTypePrice.query.get(price_id)
        if room_type_price is None: raise APIError("该价格类型不存在")
        if room_type_price.room_type_id != room_type_id: raise APIError("提交信息不合法")

        db.session.delete(room_type_price)
        db.session.commit()

        push_log(f"删除房型{room_type_id}的{room_type_price.customer_type}价格")
        return response_json(msg=f"{room_type_price.customer_type} 删除成功")


rooms_types_bp.add_url_rule(
    rule="",
    view_func=RoomsTypesAPI.as_view("rooms"),
    methods=("GET", "POST")
)

rooms_types_bp.add_url_rule(
    rule="/<int:room_type_id>",
    view_func=RoomsTypeAPI.as_view("room"),
    methods=("PUT", "DELETE")
)

rooms_types_bp.add_url_rule(
    rule="/<int:room_type_id>/prices",
    view_func=RoomsTypesPricesAPI.as_view("rooms_prices"),
    methods=("GET", "POST")
)

rooms_types_bp.add_url_rule(
    rule="/<int:room_type_id>/prices/<int:price_id>",
    view_func=RoomsTypesPriceAPI.as_view("rooms_price"),
    methods=("PUT", "DELETE")
)
