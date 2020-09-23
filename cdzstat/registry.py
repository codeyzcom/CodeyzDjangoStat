from cdzstat import (
    ACTIVE_SESSIONS,
    utils,
)


class SessionRegistry:

    template_key = ACTIVE_SESSIONS

    def __init__(self, connection=None):
        self.connection = connection

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
        score = utils.current_timestamp() + ttl
        return self.connection.zadd(self.template_key, {key: score})

    def update_at_ttl(self, key, increment) -> bool:
        current_score = self.connection.zscore(self.template_key, key)
        now = utils.current_timestamp()
        if now > current_score:
            return False
        value = (now + increment) - current_score
        self.connection.zincrby(self.template_key, value, key)
        return True

    def get_expired_keys(self, timestamp=None):
        """Return keys whos score are less than current timestamp"""

        score = timestamp if timestamp is not None else utils.current_timestamp()

        return [
            str(k) for k in
            self.connection.zrangebyscore(self.template_key, 0, score)
        ]

    def remove(self, key, pipline=None) -> None:
        if pipline is not None:
            pipline.zrem(self.template_key, key)
        self.connection.zrem(self.template_key, key)
