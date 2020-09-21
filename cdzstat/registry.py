from cdzstat.utils import current_timestamp


class BaseQueueRegistry:

    key_template = 'cdzstat:registry:{0}'

    def __init__(self, name='default', connection=None):
        self.conection = connection
        self.name = name

        self.queue_key = self.key_template.format(self.name)

    def add(self, key, ttl, pipeline=None):
        """Adds a key to a registry with expire time of now + ttl"""
        score = current_timestamp() + ttl

        if pipeline is not None:
            return pipeline.zadd(self.queue_key, {key: score})

        return self.conection.zadd(self.queue_key, {key: score})
