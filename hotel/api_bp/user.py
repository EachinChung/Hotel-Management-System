from flask import Blueprint, g
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from hotel.api_error import APIError
from hotel.common import get_request_body, response_json
from hotel.extensions import db
from hotel.models import User, UserGroup
from hotel.my_redis import Redis
from hotel.token import login_purview_required

user_bp = Blueprint("user", __name__)


@user_bp.route("/add", methods=["POST"])
@login_purview_required
def add_user() -> response_json:
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

    user = User(phone=phone, name=name, user_group_id=user_group_id)
    user.set_password(phone)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        raise APIError("账号重复")

    return response_json(msg=f"{name} 添加成功")


@user_bp.route("/update", methods=["POST"])
@login_purview_required
def update_user() -> response_json:
    """
    修改用户
    :return:
    """

    phone, name, user_group_id = get_request_body("phone", "name", "user_group_id")

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


@user_bp.route("/del", methods=["POST"])
@login_purview_required
def del_user() -> response_json:
    """
    删除用户
    :return:
    """

    phone = get_request_body("phone")[0]

    if not phone.isdigit(): raise APIError("提交信息不合法")

    if g.session["phone"] == phone: raise APIError("不能删除当前账户")

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


@user_bp.route("/list", methods=["POST"])
@login_purview_required
def user_list() -> response_json:
    """
    用户列表
    :return:
    """

    page, per_page, query = get_request_body("page", "per_page", "query")

    def _decode(item):  # 把数据库模型解析为 json
        return dict(
            phone=item[0],
            name=item[1],
            user_group=item[2],
            user_group_id=item[3]
        )

    users = db.session.query(User.phone, User.name, UserGroup.group_name, User.user_group_id).join(
        User, User.user_group_id == UserGroup.id).filter(
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
