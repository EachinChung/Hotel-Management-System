from flask import Blueprint

from hotel.common import response_json
from hotel.token import login_purview_required

user_group_bp = Blueprint("user-group", __name__)


@user_group_bp.route("/purview/template")
@login_purview_required
def template() -> response_json:
    """
    权限模板
    :return:
    """
    data = {
        "room-type": {
            "add": True,
            "del": True,
            "update": True,
            "list": True,
        }
    }
    return response_json(data)
