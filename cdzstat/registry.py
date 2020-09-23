from cdzstat.utils import current_timestamp


class BaseQueueRegistry:

    registry_template = 'cdzstat:registry:{0}'

    def __init__(self, name='default', connection=None):
        self.connection = connection
        self.name = name

        self.template_key = self.registry_template.format(self.name)

    def __len__(self):
        return self.count

    def __contains__(self, item):
        """
        Return a boolean indicateing registry contains the 
        given key
        """
        return self.connection.zscore(self.template_key, item) is not None

    @property
    def count(self):
        """Returns the number of keys in this rigistry"""
        return self.connection.zcard(self.template_key)

    def add(self, key, ttl):
        """Adds a key to a registry with expire time of now + ttl"""
        score = current_timestamp() + ttl
        return self.connection.zadd(self.template_key, {key: score})

    def update_at_ttl(self, key, increment) -> bool:
        current_score = self.connection.zscore(self.template_key, key)
        now = current_timestamp()
        if now > current_score:
            return False
        value = (now + increment) - current_score
        self.connection.zincrby(self.template_key, value, key)
        return True

    def get_expired_keys(self, timestamp=None):
        """Return keys whos score are less than current timestamp"""

        score = timestamp if timestamp is not None else current_timestamp()

        return [
            str(k) for k in
            self.connection.zrangebyscore(self.template_key, 0, score)
        ]

    def remove(self, key, pipline=None) -> None:
        if pipline is not None:
            pipline.zrem(self.template_key, key)
        self.connection.zrem(self.template_key, key)
