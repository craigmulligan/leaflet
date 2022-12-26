from celery import Celery, signals, Task


class FlaskCelery(Celery):
    ContextTask: Task

    def __init__(self):
        super().__init__()

    def register(self, app):
        url = app.config["DATABASE_URL"].replace("postgres", "postgresql", 1)
        # Note we use json serializer
        # for safety reasons.
        # https://stackoverflow.com/questions/37376684/how-to-run-celery-workers-by-superuser#37376769
        self.conf.update(
            {
                "broker_url": "sqla+" + url,
                "result_backend": "db+" + url,
                "accept_content": ['json'],
                 "task_serializer": 'json',
                 "result_serializer":'json'
            }
        )

        class ContextTask(Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        if not app.config.get("TESTING"):
            # In the tests we don't want
            # to push a app context
            # this is because the unit
            # tests already have a context pushed
            # which confuses things.
            self.Task = ContextTask

        return self


@signals.setup_logging.connect
def setup_celery_logging(**_):
    """
    This is to override celeries logging hijack.
    see: https://github.com/celery/celery/issues/2509#issuecomment-153936466
    """
    pass


celery = FlaskCelery()
