from json import dumps, loads

from flask import Blueprint, g, request
from sqlalchemy.exc import IntegrityError

from hotel.common import get_user_purview, response_json
from hotel.extensions import db
from hotel.models import UserGroup
from hotel.token import login_required, login_sudo_required

user_group_bp = Blueprint("user-group", __name__)


@user_group_bp.route("/purview")
@login_required  # 所有用户都要获取权限，所以仅需鉴权是否登录
def purview_bp() -> response_json:
    """
    获取权限
    :return:
    """
    purview = get_user_purview()
    return response_json(dict(purview=purview, weight=int(g.session["weight"])))


@user_group_bp.route("/id-list")
@login_required
def user_group_id_list() -> response_json:
    """
    获取用户组id
    :return:
    """
    group_list = UserGroup.query.all()
    items = tuple(map(lambda item: dict(id=item.id, group_name=item.group_name), group_list))
    return response_json(dict(items=items))


@user_group_bp.route("/list", methods=["POST"])
@login_sudo_required
def user_group_list() -> response_json:
    """
    获取所有用户组信息
    :return:
    """
    try:
        data = request.get_json()
        page = data["page"]
        per_page = data["per_page"]
        query = data["query"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    # 把数据库模型解析为 json
    def _decode(item):
        return dict(
            id=item.id,
            group_name=item.group_name,
            description=item.description,
            weight=item.weight,
            purview=loads(item.purview)
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
    try:
        data = request.get_json()
        group_name = data["group_name"]
        description = data["description"]
        weight = data["weight"]
        purview = data["purview"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    if not isinstance(purview, dict):
        return response_json(err=1, msg="提交信息不合法")

    if weight < 1: return response_json(err=1, msg="不能创建权重小于 1 的账户组")
    user_group = UserGroup(group_name=group_name, description=description, weight=weight, purview=dumps(purview))

    try:
        db.session.add(user_group)
        db.session.commit()
    except IntegrityError:
        return response_json(err=1, msg="用户组重复")

    return response_json(msg=f"{group_name} 添加成功")


@user_group_bp.route("/update", methods=["POST"])
@login_sudo_required
def update_user_group() -> response_json:
    """
    修改用户组
    :return:
    """
    try:
        data = request.get_json()
        user_group_id = data["user_group_id"]
        group_name = data["group_name"]
        description = data["description"]
        weight = data["weight"]
        purview = data["purview"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    if not isinstance(purview, dict):
        return response_json(err=1, msg="提交信息不合法")

    user_group = UserGroup.query.get(user_group_id)
    if user_group is None: return response_json(err=1, msg="该用户组不存在")
    if user_group.weight < 1: return response_json(err=1, msg="不能修改超级管理员")

    user_group.group_name = group_name
    user_group.description = description
    user_group.weight = weight
    user_group.purview = dumps(purview)
    db.session.add(user_group)
    db.session.commit()

    return response_json(msg=f"{group_name} 修改成功")


@user_group_bp.route("/del", methods=["POST"])
@login_sudo_required
def del_user_group() -> response_json:
    """
    删除用户组
    :return:
    """
    try:
        data = request.get_json()
        user_group_id = data["user_group_id"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    user_group = UserGroup.query.get(user_group_id)
    if user_group is None: return response_json(err=1, msg="该用户组不存在")
    if user_group.weight < 1: return response_json(err=1, msg="不能删除超级管理员")

    db.session.delete(user_group)
    db.session.commit()
    return response_json(msg=f"{user_group.group_name} 删除成功")
