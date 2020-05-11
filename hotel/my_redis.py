from flask import current_app
from redis import StrictRedis


class Redis:
    """
    redis数据库操作
    """

    @staticmethod
    def _get_r():
        pool = current_app.config['REDIS_POOL']
        return StrictRedis(connection_pool=pool)

    @classmethod
    def set(cls, key: str, value: str, expire=300) -> None:
        """
        写入键值对
        :param key:
        :param value:
        :param expire:
        :return:
        """
        r = cls._get_r()
        r.set(key, value, ex=expire)

    @classmethod
    def get(cls, key: str) -> str:
        """
        读取键值对内容
        :param key:
        :return:
        """
        r = cls._get_r()
        value = r.get(key)
        return value

    @classmethod
    def hset(cls, name: str, key: str, value: str) -> None:
        """
        写入hash表
        :param name:
        :param key:
        :param value:
        :return:
        """
        r = cls._get_r()
        r.hset(name, key, value)

    @classmethod
    def hmset(cls, name: str, mapping: dict) -> None:
        """
        在name对应的hash中批量设置键值对
        :param name:
        :param mapping:
        :return:
        """
        r = cls._get_r()
        r.hmset(name, mapping)

    @classmethod
    def hget(cls, name: str, key: str) -> str:
        """
        读取指定hash表的键值
        :param name:
        :param key:
        :return:
        """
        r = cls._get_r()
        value = r.hget(name, key)
        return value

    @classmethod
    def hmget(cls, name: str, keys: tuple) -> list:
        """
        读取指定hash表的所有给定字段的值
        :param keys:
        :param name:
        :return:
        """
        r = cls._get_r()
        value = r.hmget(name, keys)
        return value

    @classmethod
    def hgetall(cls, name: str) -> dict:
        """
        获取指定hash表所有的值
        :param name:
        :return:
        """
        r = cls._get_r()
        return r.hgetall(name)

    @classmethod
    def delete(cls, *names: str) -> None:
        """
        删除一个或者多个
        :param names:
        :return:
        """
        r = cls._get_r()
        r.delete(*names)

    @classmethod
    def hdel(cls, name: str, key: str) -> None:
        """
        删除指定hash表的键值
        :param name:
        :param key:
        :return:
        """
        r = cls._get_r()
        r.hdel(name, key)

    @classmethod
    def expire(cls, name: str, expire: int = 300) -> None:
        """
        设置过期时间
        :param name:
        :param expire:
        :return:
        """
        r = cls._get_r()
        r.expire(name, expire)
