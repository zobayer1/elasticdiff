from redis import Redis


class RedisDb:

    def __init__(self, conf):
        print(conf)
        self.db = Redis(host=conf.get('host', 'localhost'), port=conf.get('port', 6379), db=conf.get('id', 0))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self

    def set(self, key, value):
        self.db.set(key, value)

    def get(self, key):
        return self.db.get(key)
