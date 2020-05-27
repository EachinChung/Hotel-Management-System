create database hotel;

use hotel;

create table login_log
(
    id         int unsigned not null primary key auto_increment,
    ip         int unsigned not null,
    user       varchar(64)  not null,
    user_phone char(11)     not null,
    user_group varchar(64)  not null,
    datetime   datetime     not null,
    index user_index (user),
    index user_phone_index (user_phone)
);

create table log
(
    id         int unsigned not null primary key auto_increment,
    ip         int unsigned not null,
    user       varchar(64)  not null,
    user_group varchar(64)  not null,
    message    varchar(254) not null,
    datetime   datetime     not null,
    index user_index (user)
);

create table user_group
(
    id          int unsigned not null primary key auto_increment,
    group_name  varchar(64)  not null unique,
    description varchar(200) not null,
    weight      int unsigned not null
);

create table purview_user
(
    user_group_id  int unsigned not null primary key,
    add_purview    tinyint      not null,
    del_purview    tinyint      not null,
    get_purview    tinyint      not null,
    update_purview tinyint      not null,
    set_activation tinyint      not null,
    foreign key (user_group_id) references user_group (id) on delete cascade on update cascade
);

create table purview_room
(
    user_group_id  int unsigned not null primary key,
    add_purview    tinyint      not null,
    del_purview    tinyint      not null,
    get_purview    tinyint      not null,
    update_purview tinyint      not null,
    set_discounted tinyint      not null,
    foreign key (user_group_id) references user_group (id) on delete cascade on update cascade
);

create table purview_room_type
(
    user_group_id  int unsigned not null primary key,
    add_purview    tinyint      not null,
    del_purview    tinyint      not null,
    get_purview    tinyint      not null,
    update_purview tinyint      not null,
    set_price      tinyint      not null,
    foreign key (user_group_id) references user_group (id) on delete cascade on update cascade
);

create table user
(
    phone         char(11)     not null primary key,
    name          varchar(64)  not null,
    password_hash char(94)     not null,
    user_group_id int unsigned not null,
    is_activation tinyint      not null,
    foreign key (user_group_id) references user_group (id) on delete cascade on update cascade
);

create table room_type
(
    id               int unsigned not null primary key auto_increment,
    room_type        varchar(64)  not null unique,
    number_of_beds   tinyint      not null,
    number_of_people tinyint      not null,
    price_tag        float        not null,
    update_datetime  datetime     not null,
    operator         varchar(64)  not null
);

create table room_type_price
(
    id              int unsigned not null primary key auto_increment,
    room_type_id    int unsigned not null,
    customer_type   varchar(64)  not null,
    price           float        not null,
    check_out_time  time         not null,
    update_datetime datetime     not null,
    operator        varchar(64)  not null,
    foreign key (room_type_id) references room_type (id) on delete cascade on update cascade
);

create table room
(
    id              int          not null primary key,
    room_type_id    int unsigned not null,
    floor           int          not null,
    status          tinyint      not null,
    is_discounted   tinyint      not null,
    update_datetime datetime     not null,
    operator        varchar(64)  not null,
    foreign key (room_type_id) references room_type (id) on delete cascade on update cascade
);

create table room_calendar
(
    id           int unsigned not null primary key auto_increment,
    booking_id   char(22),
    check_in_id  char(22),
    room_id      int,
    room_type_id int unsigned not null,
    date         date         not null,
    index calendar_data (date),
    index booking (booking_id),
    index check_in (check_in_id)
);

create table booking_order
(
    id             char(22)     not null primary key,
    arrival_date   date         not null,
    check_out_date date         not null,
    phone          varchar(32)  not null,
    booker         varchar(64)  not null,
    remark         varchar(200) null,
    operator_phone char(11)     not null
);

create table group_order
(
    id char(22) not null primary key
);

create table check_in_order
(
    id char(22) not null primary key
);

# 以下为测试运行时，所必须的数据
INSERT INTO hotel.user_group (id, group_name, description, weight)
VALUES (1, '超级管理员', '拥有所有权限，不可修改，不可删除。', 0);
INSERT INTO hotel.user_group (id, group_name, description, weight)
VALUES (2, '测试', '测试用户组，生产环境需删除', 1);
INSERT INTO hotel.user_group (id, group_name, description, weight)
VALUES (3, '测试缓存', '用来测试缓存的用户组，生产环境需删除', 2);
INSERT INTO hotel.user_group (id, group_name, description, weight)
VALUES (4, '无权限用户组', '没有权限的用户组，生产环境需删除', 10);

INSERT INTO hotel.purview_user (user_group_id, add_purview, del_purview, get_purview, update_purview, set_activation)
VALUES (1, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_user (user_group_id, add_purview, del_purview, get_purview, update_purview, set_activation)
VALUES (2, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_user (user_group_id, add_purview, del_purview, get_purview, update_purview, set_activation)
VALUES (3, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_user (user_group_id, add_purview, del_purview, get_purview, update_purview, set_activation)
VALUES (4, 0, 0, 0, 0, 0);

INSERT INTO hotel.purview_room (user_group_id, add_purview, del_purview, get_purview, update_purview, set_discounted)
VALUES (1, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_room (user_group_id, add_purview, del_purview, get_purview, update_purview, set_discounted)
VALUES (2, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_room (user_group_id, add_purview, del_purview, get_purview, update_purview, set_discounted)
VALUES (3, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_room (user_group_id, add_purview, del_purview, get_purview, update_purview, set_discounted)
VALUES (4, 0, 0, 0, 0, 0);

INSERT INTO hotel.purview_room_type (user_group_id, add_purview, del_purview, get_purview, update_purview, set_price)
VALUES (1, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_room_type (user_group_id, add_purview, del_purview, get_purview, update_purview, set_price)
VALUES (2, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_room_type (user_group_id, add_purview, del_purview, get_purview, update_purview, set_price)
VALUES (3, 1, 1, 1, 1, 1);
INSERT INTO hotel.purview_room_type (user_group_id, add_purview, del_purview, get_purview, update_purview, set_price)
VALUES (4, 0, 0, 0, 0, 0);

INSERT INTO hotel.user (phone, name, password_hash, user_group_id, is_activation)
VALUES ('13711164450', '钟予乾',
        'pbkdf2:sha256:150000$xhALF1oo$554e1560e9c109fb79641ec5bc620caf86bf58682f638196b3d53d53173881ba', 1, 1);
INSERT INTO hotel.user (phone, name, password_hash, user_group_id, is_activation)
VALUES ('15811111111', '管理员',
        'pbkdf2:sha256:150000$xhALF1oo$554e1560e9c109fb79641ec5bc620caf86bf58682f638196b3d53d53173881ba', 1, 1);
INSERT INTO hotel.user (phone, name, password_hash, user_group_id, is_activation)
VALUES ('13311119999', '测试用户',
        'pbkdf2:sha256:150000$84Cq9cAE$02d2ed3026fb6867d69c8c1f7a40f92949ae3fbda6e00adc02bb584ad0a2c97f', 2, 1);

INSERT INTO hotel.room_type (id, room_type, number_of_beds, number_of_people, price_tag, update_datetime, operator)
VALUES (1, '标准大床房', 1, 2, 300, '2020-05-12 00:46:05', '钟予乾');

INSERT INTO hotel.room (id, room_type_id, floor, status, is_discounted, update_datetime, operator)
VALUES (1002, 1, 1, 0, 0, '2020-05-14 00:58:38', '钟予乾');