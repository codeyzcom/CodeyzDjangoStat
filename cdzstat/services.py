from cdzstat import (
    REDIS_CONN,
    settings,
    registry,
)


class SessionGarbageCollectorService:

    def __init__(self):
        pass
    
    def execute(self):
        reg = registry.SessionRegistry(REDIS_CONN)
        expired_keys = reg.get_expired_keys()

        if expired_keys:
            if settings.CDZSTAT_PERSISTENCE_MODE:
                for key in expired_keys:
                    print(f'Save data before delete {key}') # ToDo

            with REDIS_CONN.pipeline() as p:
                for key in expired_keys:
                    reg.remove(key, p)
                    p.delete(f'session:{key}')
                p.execute()
