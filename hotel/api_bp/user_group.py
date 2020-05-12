from flask import Blueprint, g

from hotel.common import get_user_purview, response_json
from hotel.token import login_required

user_group_bp = Blueprint("user-group", __name__)


@user_group_bp.route("/purview")
@login_required  # 所有用户都要获取权限，所以仅需鉴权是否登录
def get_purview_bp() -> response_json:
    """
    获取权限
    :return:
    """
    purview = get_user_purview()
    return response_json(dict(purview=purview, weight=g.session["weight"]))
