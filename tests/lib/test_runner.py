from freezegun import freeze_time
from unittest.mock import patch


@freeze_time("2013-04-08")
def test_run_ok(email_client, runner):
    oks, _ = runner.run()
    assert email_client.send.call_count == 2
    assert len(oks) == 2


@freeze_time("2013-04-08")
def test_run_nok(email_client, runner):
    email_client.send.side_effect = Exception("Something went wrong.")
    _, noks = runner.run()
    assert email_client.send.call_count == 2
    assert len(noks) == 2
