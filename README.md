## 项目使用说明
### 配置 env
- 请在根目录创建 .env 文件

```
# host
API_URL=http://127.0.0.1:5000
FRONT_END_URL=http://127.0.0.1:8080

# 刷新token的密钥(随机的字符串即可)
REFRESH_TOKEN=xxxxxxx

# 数据库链接
# MySQL url 例: mysql+mysqlconnector://root:123456@localhost:3306/nfu
DATABASE_URL=xxxxxxx
# Redis 密码
REDIS_PASSWORD=xxxxxxx
```

### 安装依赖库
- 项目依赖 [requirements.txt](requirements.txt)

```
➜ pip3 install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 开始运行程序

```
➜ cd hotel
➜ flask run
```

### 运行测试用例

```
➜ python -m unittest -v
```
