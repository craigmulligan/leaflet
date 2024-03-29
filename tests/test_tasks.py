from app.tasks import daily
from datetime import datetime, timedelta
from .conftest import Contains

def test_daily(dummy_user, mail_manager_mock, db, client, signin):
    send_at = datetime.utcnow() - timedelta(days=3)

    users = {}

    for i in range(5):
        user = dummy_user(email=f"{i}@x.com")
        dt = send_at - timedelta(days=5-i)
        users[dt.isoweekday()] = user
        db.user_update_send_at(user.id, dt)
        
    daily.delay()

    weekday = datetime.utcnow().isoweekday()
    user = users[weekday]

    # Should only send to user with 1.
    mail_manager_mock.send.assert_called_once_with(
        user.email,
        f"Leaflet #1",
        Contains("Shopping List"),
    )

    mail_manager_mock.send.reset_mock()

    [entry] = db.leaflet_get_all_by_user(user.id)
    assert entry.created_by == "schedule"
    
    # Try send again.
    # It shouldn't send because we only send max one "scheduled"
    # leaflet per day.
    daily.delay()
    mail_manager_mock.send.assert_not_called()
    mail_manager_mock.send.reset_mock()

    signin(user)

    # # Now manually create one.
    client.post(f"/user/{user.id}/leaflet", follow_redirects=True)

    mail_manager_mock.send.assert_called_once_with(
        user.email,
        f"Leaflet #2",
        Contains("Shopping List"),
    )
