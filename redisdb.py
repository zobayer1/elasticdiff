from redis import StrictRedis, WatchError


class RedisDb:

    def __init__(self, conf):
        self.db = StrictRedis(host=conf.get('host', 'localhost'),
                              port=conf.get('port', 6379),
                              db=conf.get('id', 0),
                              password=conf.get('password', ''),
                              )
        self.reset()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self

    def atomic_update(self, key, value):
        with self.db.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(key)
                    current_value = pipe.get(key)
                    if current_value:
                        value = value + '#' + current_value.decode('utf-8')
                    pipe.multi()
                    pipe.set(key, value.encode('utf-8'))
                    pipe.execute()
                    break
                except WatchError:
                    continue

    def find_diff(self):
        for key in self.db.scan_iter('*'):
            value = self.db.get(key).decode('utf-8')
            if value.count('#') != 1:
                for part in value.split('#'):
                    yield(tuple(part.split(':')))

    def reset(self):
        for key in self.db.scan_iter('*'):
            self.db.delete(key)
