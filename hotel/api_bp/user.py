from flask import Blueprint, g, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from hotel.common import response_json
from hotel.diy_error import DiyError
from hotel.extensions import db
from hotel.models import User, UserGroup
from hotel.token import login_purview_required

user_bp = Blueprint("user", __name__)


def _get_user_data() -> tuple:
    """
    获取请求头的用户数据
    :return:
    """
    try:
        data = request.get_json()
        phone = data["phone"]
        name = data["name"]
        user_group_id = data["user_group_id"]
    except (KeyError, TypeError):
        raise DiyError("缺少参数")

    # 如果电话或权限不是数字，则是非法提交
    if not phone.isdigit():
        raise DiyError("提交信息不合法")

    return phone, name, user_group_id


@user_bp.route("/add", methods=["POST"])
@login_purview_required
def add_user() -> response_json:
    """
    添加用户
    :return:
    """
    try:
        phone, name, user_group_id = _get_user_data()
    except DiyError as err:
        return response_json(err=err.code, msg=err.message)

    # 如果电话或权限不是数字，则是非法提交
    if not phone.isdigit():
        return response_json(err=1, msg="提交信息不合法")

    user_group = UserGroup.query.get(user_group_id)
    if user_group is None:
        return response_json(err=1, msg="该用户组不存在")

    if int(g.session["weight"]) >= user_group.weight:
        return response_json(err=1, msg="只能创建比自己权重低的账户")

    user = User(phone=phone, name=name, user_group_id=user_group_id)
    user.set_password(phone)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        return response_json(err=1, msg="账号重复")

    return response_json(msg=f"{name} 添加成功")


@user_bp.route("/update", methods=["POST"])
@login_purview_required
def update_user() -> response_json:
    """
    修改用户
    :return:
    """
    try:
        phone, name, user_group_id = _get_user_data()
    except DiyError as err:
        return response_json(err=err.code, msg=err.message)

    user = User.query.get(phone)
    if user is None:
        return response_json(err=1, msg="该用户不存在")

    if int(g.session["weight"]) >= user.user_group.weight:
        return response_json(err=1, msg="只能修改比自己权重低的账户")

    user_group = UserGroup.query.get(user_group_id)
    if user_group is None:
        return response_json(err=1, msg="该用户组不存在")

    if int(g.session["weight"]) >= user_group.weight:
        return response_json(err=1, msg="只能修改为比自己权重低的账户")

    user.name = name
    user.user_group_id = user_group_id
    db.session.add(user)
    db.session.commit()

    return response_json(msg=f"{name} 修改成功")


@user_bp.route("/del", methods=["POST"])
@login_purview_required
def del_user() -> response_json:
    """
    删除用户
    :return:
    """
    try:
        data = request.get_json()
        phone = data["phone"]
    except (KeyError, TypeError):
        return response_json(err=1, msg="缺少参数")

    if not phone.isdigit():
        return response_json(err=1, msg="提交信息不合法")

    if g.session["phone"] == phone:
        return response_json(err=1, msg="不能删除当前账户")

    user = User.query.get(phone)
    if user is None:
        return response_json(err=1, msg="该账号不存在")

    if int(g.session["weight"]) >= user.user_group.weight:
        return response_json(err=1, msg="只能删除比自己权重低的账户")

    db.session.delete(user)
    db.session.commit()
    return response_json(msg=f"{user.name} 删除成功")


@user_bp.route("/list", methods=["POST"])
@login_purview_required
def user_list() -> response_json:
    """
    用户列表
    :return:
    """
    try:
        data = request.get_json()
        page = data["page"]
        per_page = data["per_page"]
        query = data["query"]
    except (KeyError, TypeError):
        return response_json({}, err=1, msg="缺少参数")

    def _decode(item):  # 把数据库模型解析为 json
        return dict(phone=item.phone, name=item.name, user_group=item.user_group.group_name)

    users = User.query.filter(or_(
        User.name.like(f"%{query}%"),
        User.phone.like(f"%{query}%")
    )).paginate(page=page, per_page=per_page)
    items = tuple(map(_decode, users.items))

    return response_json(dict(
        items=items,
        page=users.page,
        per_page=users.per_page,
        pages=users.pages,
        total=users.total
    ))
