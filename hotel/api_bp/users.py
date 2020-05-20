from flask import Blueprint, g, request
from flask.views import MethodView
from sqlalchemy import or_

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
from hotel.extensions import db
from hotel.models import User, UserGroup
from hotel.my_redis import Redis
from hotel.token import login_purview_required

users_bp = Blueprint("users", __name__)


class UsersAPI(MethodView):
    @login_purview_required("user", "get")
    def get(self) -> response_json:
        """
        获取用户
        :return:
        """
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=2, type=int)
        query = request.args.get("query", default="")

        def _decode(item):  # 把数据库模型解析为 json
            return dict(
                phone=item[0].phone,
                name=item[0].name,
                user_group=item[1].group_name,
                user_group_id=item[0].user_group_id,
                is_activation=item[0].is_activation
            )

        users = db.session.query(User, UserGroup).join(
            User, User.user_group_id == UserGroup.id).filter(UserGroup.weight >= g.session["weight"]).filter(
            or_(User.name.like(f"%{query}%"), User.phone.like(f"%{query}%"))
        ).order_by(UserGroup.weight).order_by(User.name).paginate(page=page, per_page=per_page)
        items = tuple(map(_decode, users.items))

        return response_json(dict(
            items=items,
            page=users.page,
            per_page=users.per_page,
            pages=users.pages,
            total=users.total
        ))

    @login_purview_required("user", "add")
    def post(self) -> response_json:
        """
        添加用户
        :return:
        """
        phone, name, user_group_id = get_request_body("phone", "name", "user_group_id")

        # 如果电话或权限不是数字，则是非法提交
        if not phone.isdigit(): raise APIError("提交信息不合法")

        user_group = UserGroup.query.get(user_group_id)
        if user_group is None: raise APIError("该用户组不存在")

        if int(g.session["weight"]) >= user_group.weight:
            raise APIError("只能创建比自己权重低的账户")

        user = User.query.get(phone)
        if user is not None: raise APIError("账号重复")

        user = User(phone=phone, name=name, user_group_id=user_group_id)
        user.set_password(phone)

        db.session.add(user)
        db.session.commit()

        return response_json(msg=f"{name} 添加成功")


class UserAPI(MethodView):
    @login_purview_required("user", "set_activation")
    def patch(self, phone):
        """
        修改用户状态
        :param phone:
        :return:
        """
        is_activation = get_request_body("is_activation")[0]
        user = User.query.get(phone)
        if user is None: raise APIError("该用户不存在")

        if int(g.session["weight"]) >= user.user_group.weight:
            raise APIError("只能修改比自己权重低的账户状态")

        user.is_activation = is_activation

        Redis.fuzzy_delete(phone)
        db.session.add(user)
        db.session.commit()
        Redis.fuzzy_delete(phone)

        message = "激活状态" if is_activation else "非激活状态"
        return response_json(msg=f"{user.name} 修改为{message}")

    @login_purview_required("user", "update")
    def put(self, phone) -> response_json:
        """
        修改用户
        :param phone:
        :return:
        """
        name, user_group_id = get_request_body("name", "user_group_id")
        user = User.query.get(phone)
        if user is None: raise APIError("该用户不存在")

        if int(g.session["weight"]) >= user.user_group.weight:
            raise APIError("只能修改比自己权重低的账户")

        user_group = UserGroup.query.get(user_group_id)
        if user_group is None: raise APIError("该用户组不存在")

        if int(g.session["weight"]) >= user_group.weight:
            raise APIError("只能修改为比自己权重低的账户")

        user.name = name
        user.user_group_id = user_group_id

        # 两次刷新缓存，防止数据污染
        Redis.fuzzy_delete(phone)
        db.session.add(user)
        db.session.commit()
        Redis.fuzzy_delete(phone)

        return response_json(msg=f"{name} 修改成功")

    @login_purview_required("user", "del")
    def delete(self, phone) -> response_json:
        """
        删除用户
        :param phone:
        :return:
        """
        if g.session["phone"] == str(phone): raise APIError("不能删除当前账户")

        user = User.query.get(phone)
        if user is None: raise APIError("该账号不存在")

        if int(g.session["weight"]) >= user.user_group.weight:
            raise APIError("只能删除比自己权重低的账户")

        # 两次刷新缓存，防止数据污染
        Redis.fuzzy_delete(phone)
        db.session.delete(user)
        db.session.commit()
        Redis.fuzzy_delete(phone)

        return response_json(msg=f"{user.name} 删除成功")


users_bp.add_url_rule("/", view_func=UsersAPI.as_view("users"), methods=("GET", "POST"))
users_bp.add_url_rule("/<int:phone>", view_func=UserAPI.as_view("user"), methods=("PATCH", "PUT", "DELETE"))
