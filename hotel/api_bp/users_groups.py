from flask import Blueprint, g, request
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from hotel.api_error import APIError
from hotel.common import get_request_body, push_log, response_json
from hotel.extensions import db
from hotel.models import UserGroup
from hotel.purview import get_user_purview_from_cache, get_user_purview_from_mysql
from hotel.token import login_required, login_sudo_required

users_groups_bp = Blueprint("groups_users", __name__)


@users_groups_bp.route("/purview")
@login_required  # 所有用户都要获取权限，所以仅需鉴权是否登录
def purview_bp() -> response_json:
    """
    获取权限
    :return:
    """
    purview = get_user_purview_from_cache()
    return response_json(dict(purview=purview, weight=int(g.session["weight"])))


@users_groups_bp.route("/ids")
@login_required
def user_group_id_list() -> response_json:
    """
    获取用户组id
    :return:
    """
    group_list = UserGroup.query.filter(UserGroup.weight >= g.session["weight"]).order_by(UserGroup.weight).all()
    items = tuple(map(lambda item: dict(
        id=item.id,
        weight=item.weight,
        group_name=item.group_name
    ), group_list))
    return response_json(dict(items=items))


class GroupsUsersAPI(MethodView):
    decorators = [login_sudo_required]

    def get(self) -> response_json:
        """
        获取用户组
        :return:
        """
        page = request.args.get("page", default=1, type=int)
        per_page = request.args.get("per_page", default=2, type=int)
        query = request.args.get("query", default="")

        # 把数据库模型解析为 json
        def _decode(item):
            return dict(
                id=item.id,
                group_name=item.group_name,
                description=item.description,
                weight=item.weight,
                purview=get_user_purview_from_mysql(item.id)
            )

        group_list = UserGroup.query.filter(UserGroup.group_name.like(
            f"%{query}%")).order_by(UserGroup.weight).paginate(page=page, per_page=per_page)
        items = tuple(map(_decode, group_list.items))

        return response_json(dict(
            items=items,
            page=group_list.page,
            per_page=group_list.per_page,
            pages=group_list.pages,
            total=group_list.total
        ))

    def post(self) -> response_json:
        """
        添加用户组
        :return:
        """
        group_name, description, weight = get_request_body("group_name", "description", "weight")

        if weight < 1: raise APIError("不能创建权重小于 1 的账户组")
        user_group = UserGroup(group_name=group_name, description=description, weight=weight)

        try:
            db.session.add(user_group)
            db.session.commit()
        except IntegrityError:
            raise APIError("用户组重复")

        push_log(f"添加用户组 {user_group.group_name}")
        return response_json(msg=f"{group_name} 添加成功")


class GroupsUserAPI(MethodView):
    decorators = [login_sudo_required]

    def put(self, user_group_id) -> response_json:
        """
        修改用户组
        :param user_group_id:
        :return:
        """
        group_name, description, weight = get_request_body("group_name", "description", "weight")

        user_group = UserGroup.query.get(user_group_id)
        if user_group is None: raise APIError("该用户组不存在")
        if user_group.weight < 1: raise APIError("不能修改超级管理员")

        user_group.group_name = group_name
        user_group.description = description
        user_group.weight = weight
        db.session.add(user_group)
        db.session.commit()

        push_log(f"修改用户组 {user_group.group_name}")
        return response_json(msg=f"{group_name} 修改成功")

    def delete(self, user_group_id) -> response_json:
        """
        删除用户组
        :param user_group_id:
        :return:
        """
        user_group = UserGroup.query.get(user_group_id)
        if user_group is None: raise APIError("该用户组不存在")
        if user_group.weight < 1: raise APIError("不能删除超级管理员")

        db.session.delete(user_group)
        db.session.commit()

        push_log(f"删除用户组 {user_group.group_name}")
        return response_json(msg=f"{user_group.group_name} 删除成功")


users_groups_bp.add_url_rule("/", view_func=GroupsUsersAPI.as_view("rooms"), methods=("GET", "POST"))
users_groups_bp.add_url_rule("/<int:user_group_id>", view_func=GroupsUserAPI.as_view("room"), methods=("PUT", "DELETE"))
