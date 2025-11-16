from django_mongodb_backend.routers import MongoRouter as BaseMongoRouter


class MongoRouter(BaseMongoRouter):
    """
    Routes database operations for apps that use MongoDB.
    """

    app_labels = {"conversations"}
    mongo_db = "mongodb"

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.app_labels:
            return self.mongo_db
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.app_labels:
            return self.mongo_db
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
                obj1._meta.app_label in self.app_labels
                or obj2._meta.app_label in self.app_labels
        ):
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # MongoDB allowed only for listed apps
        if db == self.mongo_db:
            if app_label not in self.app_labels:
                return False

            base = super().allow_migrate(db, app_label, model_name, **hints)
            if base is not None:
                return base
            return True

        # default db disallowed for listed apps
        if app_label in self.app_labels:
            return False

        return None
