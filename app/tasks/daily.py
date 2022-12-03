import logging
from app.celery import celery
from app import database
from datetime import datetime
from .email import email_send

@celery.task
def daily(*args, **kwargs):
    now = datetime.utcnow()
    weekday = now.isoweekday() 
    db = database.get()

    for user in db.user_get_by_weekday(weekday):
        pass

    return

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    """
    Called every day
    """
    logging.info("setting up periodic task.")
    sender.add_periodic_task(10.0, daily.s(), name='daily')
