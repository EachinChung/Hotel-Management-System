from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from hotel.common import response_json
from hotel.extensions import db
from hotel.models import User
from hotel.token import login_required

user_bp = Blueprint("user", __name__)


@user_bp.route("/add", methods=["POST"])
@login_required
def add_user() -> response_json:
    """
    添加用户
    :return:
    """
    try:
        data = request.get_json()
        phone = data["phone"]
        name = data["name"]
        user_group_id = data["user_group_id"]
    except (KeyError, TypeError):
        return response_json({}, err=1, msg="缺少参数")

    # 如果电话或权限不是数字，则是非法提交
    if not phone.isdigit() or type(user_group_id) is not int:
        return response_json({}, err=1, msg="提交信息不合法")

    user = User(phone=phone, name=name, user_group_id=user_group_id)
    user.set_password(phone)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        return response_json({}, err=1, msg="账号重复")

    return response_json({}, msg=f"{name} 添加成功")
