from flask import Blueprint, g

from hotel.common import get_user_purview, response_json
from hotel.models import UserGroup
from hotel.token import login_required, login_purview_required

user_group_bp = Blueprint("user-group", __name__)


@user_group_bp.route("/purview")
@login_required  # 所有用户都要获取权限，所以仅需鉴权是否登录
def purview_bp() -> response_json:
    """
    获取权限
    :return:
    """
    purview = get_user_purview()
    return response_json(dict(purview=purview, weight=g.session["weight"]))


@user_group_bp.route("/id-list")
@login_required  # 所有用户都要获取权限，所以仅需鉴权是否登录
def user_group_id_list() -> response_json:
    """
    获取用户组id
    :return:
    """

    # 把数据库模型解析为 json
    def _decode(item):
        return dict(
            id=item.id,
            group_name=item.group_name
        )

    group_list = UserGroup.query.all()
    items = tuple(map(_decode, group_list))
    return response_json(dict(items=items))


@user_group_bp.route("/list")
@login_purview_required
def user_group_list() -> response_json:
    """
    获取所有用户组信息
    :return:
    """

    # 把数据库模型解析为 json
    def _decode(item):
        return dict(
            id=item.id,
            group_name=item.group_name,
            weight=item.weight,
            purview=item.purview
        )

    group_list = UserGroup.query.all()
    items = tuple(map(_decode, group_list))
    return response_json(dict(items=items))
