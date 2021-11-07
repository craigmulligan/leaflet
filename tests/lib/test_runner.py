from freezegun import freeze_time
from unittest.mock import patch


@freeze_time("2013-04-08")
def test_run_ok(postmark_client, runner):
    with patch.object(postmark_client.emails, "send") as send_mock:
        oks, _ = runner.run()
        assert send_mock.call_count == 2
        assert len(oks) == 2


@freeze_time("2013-04-08")
def test_run_nok(postmark_client, runner):

    with patch.object(
        postmark_client.emails, "send", side_effect=Exception("Something went wrong.")
    ) as send_mock:
        _, noks = runner.run()
        assert send_mock.call_count == 2
        assert len(noks) == 2
