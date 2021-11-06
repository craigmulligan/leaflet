from lib import load_user_configs, filter_user_configs


def test_load_users():
    """
    Asserts we load the users.csv correctly

    1. If there are dupes we select the most recent entry.
    2. We load the values correctly into a UserConfig.
    """
    dupe_email = "hey@x.com"
    user_configs = load_user_configs("tests/data/db/users")
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


def test_filter_users():
    """
    Checks that we only select users whose contact_day
    is today.
    """
    user_configs = load_user_configs("tests/data/db/users")
    assert len(filter_user_configs(user_configs, 1)) == 0
    assert len(filter_user_configs(user_configs, 6)) == 1
    assert len(filter_user_configs(user_configs, 0)) == 2
