import redis


class RedisClient:
    def __init__(self, host='host.docker.internal', port=6379, db=0):
        self.redis_client = redis.StrictRedis(host=host, port=port, db=db)

    def get_redis(self):
        """
        Obtém uma uma instancia do Redis.
        """
        return self.redis_client
