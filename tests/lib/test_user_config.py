from freezegun import freeze_time
from datetime import datetime


def test_load_users(user_config_loader):
    """
    Asserts we load the users.csv correctly

    1. If there are dupes we select the most recent entry.
    2. We load the values correctly into a UserConfig.
    """
    dupe_email = "hey@x.com"
    user_configs = user_config_loader._all_user_configs()
    assert len(user_configs.keys()) == 3

    config = [config for email, config in user_configs.items() if email == "hey@x.com"][
        0
    ]

    # Check it's the more recent entry.
    assert config.meal_count == 2
    assert config.person_count == 1
    assert config.email == dupe_email
    # sunday == 6
    assert config.contact_day == 6


def test_filter_weekdays_user_configs(user_config_loader):
    """
    Checks that we can load users by weekday.
    """
    assert len(user_config_loader._user_configs_by_weekday(1)) == 0
    assert len(user_config_loader._user_configs_by_weekday(6)) == 1
    assert len(user_config_loader._user_configs_by_weekday(0)) == 2


@freeze_time("2013-04-08")
def test_filter_todays_user_configs(user_config_loader):
    """
    Checks that we only select users whose contact_day
    is today.
    """
    weekday = datetime.today().weekday()
    assert weekday == 0
    assert len(user_config_loader.todays_user_configs()) == 2
