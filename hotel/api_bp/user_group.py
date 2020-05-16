from flask import Blueprint, g
from sqlalchemy.exc import IntegrityError

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
from hotel.extensions import db
from hotel.models import UserGroup
from hotel.purview import get_user_purview_from_cache, get_user_purview_from_mysql
from hotel.token import login_required, login_sudo_required

user_group_bp = Blueprint("user-group", __name__)


@user_group_bp.route("/purview")
@login_required  # 所有用户都要获取权限，所以仅需鉴权是否登录
def purview_bp() -> response_json:
    """
    获取权限
    :return:
    """
    purview = get_user_purview_from_cache()
    return response_json(dict(purview=purview, weight=int(g.session["weight"])))


@user_group_bp.route("/id-list")
@login_required
def user_group_id_list() -> response_json:
    """
    获取用户组id
    :return:
    """
    group_list = UserGroup.query.order_by(UserGroup.weight).all()
    items = tuple(map(lambda item: dict(
        id=item.id,
        weight=item.weight,
        group_name=item.group_name
    ), group_list))
    return response_json(dict(items=items))


@user_group_bp.route("/list", methods=["POST"])
@login_sudo_required
def user_group_list() -> response_json:
    """
    获取所有用户组信息
    :return:
    """
    page, per_page, query = get_request_body("page", "per_page", "query")

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


@user_group_bp.route("/add", methods=["POST"])
@login_sudo_required
def add_user_group() -> response_json:
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

    return response_json(msg=f"{group_name} 添加成功")


@user_group_bp.route("/update", methods=["POST"])
@login_sudo_required
def update_user_group() -> response_json:
    """
    修改用户组
    :return:
    """

    data = get_request_body("user_group_id", "group_name", "description", "weight")

    user_group = UserGroup.query.get(data[0])
    if user_group is None: raise APIError("该用户组不存在")
    if user_group.weight < 1: raise APIError("不能修改超级管理员")

    user_group.group_name = data[1]
    user_group.description = data[2]
    user_group.weight = data[3]
    db.session.add(user_group)
    db.session.commit()

    return response_json(msg=f"{data[1]} 修改成功")


@user_group_bp.route("/del", methods=["POST"])
@login_sudo_required
def del_user_group() -> response_json:
    """
    删除用户组
    :return:
    """
    user_group_id = get_request_body("user_group_id")[0]

    user_group = UserGroup.query.get(user_group_id)
    if user_group is None: raise APIError("该用户组不存在")
    if user_group.weight < 1: raise APIError("不能删除超级管理员")

    db.session.delete(user_group)
    db.session.commit()
    return response_json(msg=f"{user_group.group_name} 删除成功")
