from cdzstat.utils import current_timestamp


class BaseQueueRegistry:

    key_template = 'cdzstat:registry:{0}'

    def __init__(self, name='default', connection=None):
        self.connection = connection
        self.name = name

        self.queue_key = self.key_template.format(self.name)

    def __len__(self):
        return self.count

    def __contains__(self, item):
        """
        Return a boolean indicateing registry contains the 
        given key
        """
        return self.connection.zscore(self.queue_key, item) is not None

    @property
    def count(self):
        """Returns the number of keys in this rigistry"""
        return self.connection.zcard(self.queue_key)

    def add(self, key, ttl, pipeline=None):
        """Adds a key to a registry with expire time of now + ttl"""
        score = current_timestamp() + ttl

        if pipeline is not None:
            return pipeline.zadd(self.queue_key, {key: score})
        return self.connection.zadd(self.queue_key, {key: score})

    def update_at_ttl(self, key, increment):
        current_score = self.connection.zscore(self.queue_key, key)
        now = current_timestamp()
        if now > current_score:
            return False
        value = (now + increment) - current_score
        self.connection.zincrby(self.queue_key, value, key)
        return True

    def get_expired_keys(self, timestamp=None):
        """Return keys whos score are less than current timestamp"""

        score = timestamp if timestamp is not None else current_timestamp()

        return [
            str(k) for k in
            self.connection.zrangebyscore(self.queue_key, 0, score)
        ]
