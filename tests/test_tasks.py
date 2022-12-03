from freezegun import freeze_time
from app.tasks import daily
from datetime import datetime, timedelta
from unittest.mock import ANY
from .conftest import Contains

@freeze_time("2022-10-01")
def test_daily(dummy_user, mail_manager_mock, db):
    sent = 0
    send_at = datetime.utcnow() - timedelta(days=3)
    # weekday = send_at.isoweekday()

    for i in range(5):
        user = dummy_user(email=f"{i}@x.com")
        dt = send_at - timedelta(days=i)
        db.user_update_send_at(user.id, dt)
        
    sent += 1
    daily.delay()

    # Should only send to user with 1.
    mail_manager_mock.send.assert_called_once_with(
        "4@x.com",
        f"Leaflet #{sent}",
        Contains("Shopping List"),
    )

    mail_manager_mock.send.reset_mock()

    sent += 1
    daily.delay()

    mail_manager_mock.send.assert_called_once_with(
        "4@x.com",
        f"Leaflet #{sent}",
        Contains("Shopping List"),
    )
