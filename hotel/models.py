from werkzeug.security import check_password_hash, generate_password_hash

from hotel.extensions import db


class LoginLog(db.Model):
    """
    登录日志表
    """
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.Integer)
    user = db.Column(db.String, index=True)
    user_phone = db.Column(db.String, index=True)
    user_group = db.Column(db.String)
    datetime = db.Column(db.DateTime)


class Log(db.Model):
    """
    日志表
    """
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.Integer)
    user = db.Column(db.String)
    user_group = db.Column(db.String)
    message = db.Column(db.String)
    datetime = db.Column(db.DateTime)


class UserGroup(db.Model):
    """
    用户组
    """
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String)
    description = db.Column(db.String)
    weight = db.Column(db.Integer)


# noinspection DuplicatedCode
class PurviewUser(db.Model):
    """
    用户权限表
    """
    user_group_id = db.Column(db.Integer, db.ForeignKey("user_group.id"), primary_key=True)
    add_purview = db.Column(db.Boolean, default=False)
    del_purview = db.Column(db.Boolean, default=False)
    get_purview = db.Column(db.Boolean, default=False)
    update_purview = db.Column(db.Boolean, default=False)
    set_activation = db.Column(db.Boolean, default=False)

    def get_dict(self):
        return {
            "add": self.add_purview, "del": self.del_purview,
            "get": self.get_purview, "update": self.update_purview,
            "set_activation": self.set_activation
        }


# noinspection DuplicatedCode
class PurviewRoom(db.Model):
    """
    房间权限表
    """
    user_group_id = db.Column(db.Integer, db.ForeignKey("user_group.id"), primary_key=True)
    add_purview = db.Column(db.Boolean, default=False)
    del_purview = db.Column(db.Boolean, default=False)
    get_purview = db.Column(db.Boolean, default=False)
    update_purview = db.Column(db.Boolean, default=False)
    set_discounted = db.Column(db.Boolean, default=False)

    def get_dict(self):
        return {
            "add": self.add_purview, "del": self.del_purview,
            "get": self.get_purview, "update": self.update_purview,
            "set_discounted": self.set_discounted
        }


# noinspection DuplicatedCode
class PurviewRoomType(db.Model):
    """
    房间类型权限表
    """
    user_group_id = db.Column(db.Integer, db.ForeignKey("user_group.id"), primary_key=True)
    add_purview = db.Column(db.Boolean, default=False)
    del_purview = db.Column(db.Boolean, default=False)
    get_purview = db.Column(db.Boolean, default=False)
    update_purview = db.Column(db.Boolean, default=False)
    set_price = db.Column(db.Boolean, default=False)

    def get_dict(self):
        return {
            "add": self.add_purview, "del": self.del_purview,
            "get": self.get_purview, "update": self.update_purview,
            "set_price": self.set_price
        }


class User(db.Model):
    """
    用户表
    """
    phone = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    password_hash = db.Column(db.String)
    user_group_id = db.Column(db.Integer, db.ForeignKey("user_group.id"))
    is_activation = db.Column(db.Boolean, default=True)
    user_group = db.relationship('UserGroup')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class RoomType(db.Model):
    """
    房间类型表
    """
    id = db.Column(db.Integer, primary_key=True)
    room_type = db.Column(db.String, unique=True)
    number_of_beds = db.Column(db.Integer)
    number_of_people = db.Column(db.Integer)
    price_tag = db.Column(db.Float)
    update_datetime = db.Column(db.DateTime)
    operator = db.Column(db.String)


class RoomTypePrice(db.Model):
    """
    房间类型价格表
    """
    id = db.Column(db.Integer, primary_key=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey("room_type.id"))
    customer_type = db.Column(db.String)
    price = db.Column(db.Float)
    check_out_time = db.Column(db.Time)
    update_datetime = db.Column(db.DateTime)
    operator = db.Column(db.String)


class Room(db.Model):
    """
    房间表
    """
    id = db.Column(db.Integer, primary_key=True)
    room_type_id = db.Column(db.Integer, db.ForeignKey("room_type.id"))
    floor = db.Column(db.Integer)
    status = db.Column(db.Integer, default=0)
    is_discounted = db.Column(db.Boolean, default=False)
    update_datetime = db.Column(db.DateTime)
    operator = db.Column(db.String)
    room_type = db.relationship('RoomType')
