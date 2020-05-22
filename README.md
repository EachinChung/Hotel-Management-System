## 简介
[![_](https://img.shields.io/badge/python-3.8.3-informational.svg)](https://www.python.org/)
[![_](https://img.shields.io/badge/mysql-8.0.20-9cf.svg)](https://www.mysql.com/)
[![_](https://img.shields.io/badge/redis-6.0.3-red.svg)](https://redis.io/)

一个酒店后台系统的后端，基于 Python、MySQL 和 Redis 实现。

[项目前端地址](https://github.com/EachinChung/Hotel-Front-End)

## 项目使用说明
### 安装依赖库
- 项目依赖 [requirements.txt](requirements.txt)

```
➜ pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 配置 env
- 请在根目录创建 .env 文件

```
# 刷新token的密钥(随机的字符串即可)
REFRESH_TOKEN=xxxxxxx

# 数据库链接
# MySQL url 例: mysql+mysqlconnector://root:123456@localhost:3306/nfu
DATABASE_URL=xxxxxxx
# Redis 密码
REDIS_PASSWORD=xxxxxxx
```

### 初始化 MySQL

```
➜ mysql -u root -p < hotel.sql
```

### 开始运行程序

```
➜ cd hotel
➜ flask run
```

### 运行测试用例

```
# 运行单元测试
➜ coverage run -m unittest discover

# 生成测试报告
➜ coverage html

# 清除测试报告，仅删除 .coverage 文件
➜ coverage erase
```

## 开源说明
此代码仅用于学习，未经许可，不能用于其他用途。