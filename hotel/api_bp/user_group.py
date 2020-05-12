from json import loads

from flask import Blueprint, g

from hotel.common import response_json
from hotel.models import User
from hotel.my_redis import Redis
from hotel.token import login_required

user_group_bp = Blueprint("user-group", __name__)


@user_group_bp.route("/purview")
@login_required  # 所有用户都要获取权限，所以仅需鉴权是否登录
def get_purview() -> response_json:
    """
    获取权限
    :return:
    """
    purview = Redis.get(f"{g.session['phone']}-purview")

    if purview is None:
        user = User.query.get(g.session["phone"])
        Redis.set(f"{g.session['phone']}-purview", user.user_group.purview, expire=None)
        purview = loads(user.user_group.purview)
    else:
        purview = loads(purview)

    return response_json(purview)
