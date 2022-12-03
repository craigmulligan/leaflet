import logging
from app.celery import celery
from flask import render_template
from app import database
from app import leaflet_manager
from datetime import datetime
from .email import email_send

@celery.task
def daily(*args, **kwargs):
    now = datetime.utcnow()
    weekday = now.isoweekday() 
    db = database.get()
    lm = leaflet_manager.get()

    for user in db.user_get_all_by_weekday(weekday):
        leaflet = lm.generate(user)
        leaflet_id = lm.save(leaflet)
        count = db.leaflet_count_by_user(user.id) 
        logging.info(f"Sending user leaflet: {leaflet_id}")
        
        body = render_template("leaflet.html", leaflet=leaflet)
        email_send(user.email, f"Leaflet #{count}",  body)
        logging.info(f"Sent user leaflet: {leaflet_id}")


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    """
    Called every day
    """
    logging.info("setting up periodic task.")
    sender.add_periodic_task(10.0, daily.s(), name='daily')
