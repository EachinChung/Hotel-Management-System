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
        "user": {
            "add": False,
            "del": False,
            "update": False,
            "list": False,
        },
        "user-group": {
            "purview": {
                "template": False
            },
            "list": False,
        }
    }
    return response_json(data)
