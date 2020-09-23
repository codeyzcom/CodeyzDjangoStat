from cdzstat import (
    REDIS_CONN,
    registry,
)


class SessionGarbageCollectorService:

    def __init__(self):
        pass
    
    def execute(self):
        reg = registry.SessionRegistry(REDIS_CONN)
        expired_keys = reg.get_expired_keys()

        if expired_keys:
            with REDIS_CONN.pipeline() as p:
                for key in expired_keys:
                    print(f'Notify about removing key {key}')
                    reg.remove(key, p)
                    p.delete(f'session:{key}')
                p.execute()
