## 项目使用说明
### 配置 env
- 请在根目录创建 .env 文件

```
# 数据库链接
# 例如: mysql+mysqlconnector://root:123456@localhost:3306/nfu
DATABASE_URL=xxxxxxx

# 各种jwt的签名(随机的字符串即可)
ACCESS_TOKEN=xxxxxxx
REFRESH_TOKEN=xxxxxxx

# Redis 密码
REDIS_PASSWORD=xxxxxxx

# host
API_URL=http://127.0.0.1:5000
FRONT_END_URL=http://127.0.0.1:8080
```

### 依赖库
- 项目依赖 [requirements.txt](requirements.txt)

```
➜ pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 开始运行程序

```
➜ cd hotel
➜ flask run
```
