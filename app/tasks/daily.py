import logging
from app.celery import celery
from app import database
from app import leaflet_manager
from datetime import datetime
from celery.schedules import crontab

@celery.task
def daily(*args, **kwargs):
    """
    Looks up all users that need to be 
    sent leaflets today. 
    For each it will generate a new leaflet
    """
    db = database.get()
    lm = leaflet_manager.get()
    now = datetime.utcnow()
    weekday = now.isoweekday()

    with db.lock(weekday):
        for user in db.user_get_candidates(weekday):
            leaflet = lm.generate(user)
            leaflet_id = lm.save(leaflet)
            logging.info(f"Sending user {user.id} leaflet: {leaflet_id}")
            lm.send(leaflet)


@celery.on_after_configure.connect # type: ignore
def setup_periodic_tasks(sender, **kwargs):
    """
    Called every day
    """
    # Executes every Day at 8 a.m.
    logging.info("setting up periodic task.")
    sender.add_periodic_task(crontab(hour="3", minute="0"), daily.s(), name='daily')
