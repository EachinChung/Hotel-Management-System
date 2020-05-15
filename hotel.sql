create database hotel;

use hotel;

create table user_group
(
    id          int unsigned not null primary key auto_increment,
    group_name  varchar(64)  not null unique,
    description varchar(200) not null,
    weight      int unsigned not null,
    purview     json         not null
);

create table user
(
    phone         char(11)     not null primary key,
    name          varchar(64)  not null,
    password_hash char(94)     not null,
    user_group_id int unsigned not null,
    foreign key (user_group_id) references user_group (id) on delete cascade on update cascade
);

create table room_type
(
    id               int unsigned not null primary key auto_increment,
    room_type        varchar(254) not null unique,
    number_of_beds   tinyint      not null,
    number_of_people tinyint      not null,
    price_tag        float        not null,
    update_datetime  datetime     not null,
    operator         varchar(64)  not null
);

create table room
(
    id              int          not null primary key,
    room_type_id    int unsigned not null,
    floor           tinyint      not null,
    status          tinyint      not null,
    is_discounted   tinyint      not null,
    update_datetime datetime     not null,
    operator        varchar(64)  not null,
    foreign key (room_type_id) references room_type (id) on delete cascade on update cascade
);

create table booking_order
(
    id             char(22)    not null primary key,
    rooms          json        not null,
    arrival_time   datetime    not null,
    check_out_time datetime    not null,
    phone          varchar(32) not null,
    booker         varchar(64) not null,
    remark         text        null,
    operator_phone char(11)    not null
);

create table group_order
(
    id             char(22)    not null primary key,
    rooms          json        not null,
    arrival_time   datetime    not null,
    check_out_time datetime    not null,
    phone          varchar(32) not null,
    booker         varchar(64) not null,
    remark         text        null,
    operator_phone char(11)    not null
);

create table check_in_order
(
    id char(22) not null primary key
);

# 以下为测试运行时，所必须的数据
INSERT INTO hotel.user_group (id, group_name, description, weight, purview)
VALUES (1, '超级管理员', '拥有所有权限，不可修改，不可删除。', 0, '{
  "room": {
    "add": true,
    "del": true,
    "list": true,
    "update": true
  },
  "user": {
    "add": true,
    "del": true,
    "list": true,
    "update": true
  },
  "room-type": {
    "add": true,
    "del": true,
    "list": true,
    "update": true
  }
}');
INSERT INTO hotel.user_group (id, group_name, description, weight, purview)
VALUES (2, '测试', '测试用户组，生产环境需删除', 1, '{
  "user": {
    "add": false,
    "del": false,
    "list": false,
    "update": false
  },
  "user-group": {
    "list": false,
    "purview": {
      "template": false
    }
  }
}');
INSERT INTO hotel.user_group (id, group_name, description, weight, purview)
VALUES (3, '测试缓存', '用来测试缓存的用户组，生产环境需删除', 2, '{
  "room": {
    "add": true,
    "del": true,
    "list": true,
    "update": true
  },
  "user": {
    "add": true,
    "del": true,
    "list": true,
    "update": true
  },
  "room-type": {
    "add": true,
    "del": true,
    "list": true,
    "update": true
  }
}');
INSERT INTO hotel.user_group (id, group_name, description, weight, purview)
VALUES (4, '无权限用户组', '没有权限的用户组，生产环境需删除', 10, '{}');

INSERT INTO hotel.user (phone, name, password_hash, user_group_id)
VALUES ('13711164450', '钟予乾',
        'pbkdf2:sha256:150000$xhALF1oo$554e1560e9c109fb79641ec5bc620caf86bf58682f638196b3d53d53173881ba', 1);
INSERT INTO hotel.user (phone, name, password_hash, user_group_id)
VALUES ('15811111111', '管理员',
        'pbkdf2:sha256:150000$xhALF1oo$554e1560e9c109fb79641ec5bc620caf86bf58682f638196b3d53d53173881ba', 1);
INSERT INTO hotel.user (phone, name, password_hash, user_group_id)
VALUES ('13311119999', '无权限用户',
        'pbkdf2:sha256:150000$1rYcjYw2$20880762603fcff70e2992f7c57d2b5670fbb63d6c5608b78465679cda9416fd', 4);

INSERT INTO hotel.room_type (id, room_type, number_of_beds, number_of_people, price_tag, update_datetime, operator)
VALUES (1, '标准大床房', 1, 2, 300, '2020-05-12 00:46:05', '钟予乾');
INSERT INTO hotel.room_type (id, room_type, number_of_beds, number_of_people, price_tag, update_datetime, operator)
VALUES (2, '海景大床房', 1, 2, 300, '2020-05-13 16:11:52', '钟予乾');

INSERT INTO hotel.room (id, room_type_id, floor, status, is_discounted, update_datetime, operator)
VALUES (1002, 1, 1, 0, 0, '2020-05-14 00:58:38', '钟予乾');