from freezegun import freeze_time
from unittest.mock import patch

from lib import run


@freeze_time("2013-04-08")
def test_run_ok(user_config_loader, recipe_loader, email, postmark_client):

    with patch.object(postmark_client.emails, "send") as send_mock:
        oks, noks = run(user_config_loader, recipe_loader, email)
        assert send_mock.call_count == 2
        assert len(oks) == 2


@freeze_time("2013-04-08")
def test_run_nok(user_config_loader, recipe_loader, email, postmark_client):

    with patch.object(
        postmark_client.emails, "send", side_effect=Exception("Something went wrong.")
    ) as send_mock:
        oks, noks = run(user_config_loader, recipe_loader, email)
        assert send_mock.call_count == 2
        assert len(noks) == 2
