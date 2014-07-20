class StaphopiaRouter(object):
    """A router to control all database operations on models in
    the database application"""
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'database':
            return 'staphopia'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'database':
            return 'staphopia'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'database' or obj2._meta.app_label == 'database':
            return True
        return None

    def allow_syncdb(self, db, model):
        if db == 'staphopia':
            return model._meta.app_label == 'database'
        elif model._meta.app_label == 'database':
            return False
        return None