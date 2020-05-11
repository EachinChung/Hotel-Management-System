create database hotel;

use hotel;

create table user_group
(
    id         int unsigned not null primary key auto_increment,
    group_name varchar(64)  not null,
    weight     int unsigned not null,
    purview    json         not null
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
