from werkzeug.security import check_password_hash, generate_password_hash

from hotel.extensions import db


class UserGroup(db.Model):
    """
    用户组
    """
    id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String)
    description = db.Column(db.String)
    weight = db.Column(db.Integer)
    purview = db.Column(db.String)


class User(db.Model):
    """
    用户表
    """
    phone = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    password_hash = db.Column(db.String)
    user_group_id = db.Column(db.Integer, db.ForeignKey("user_group.id"))
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
