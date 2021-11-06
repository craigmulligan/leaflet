from typing import Dict
from datetime import datetime
import calendar
import csv

from dataclasses import dataclass


@dataclass
class UserConfig:
    """Config supplied for a user"""

    email: str
    timestamp: datetime
    meal_count: int = 1
    person_count: int = 1
    contact_day: int = 0


def load_user_configs(path: str) -> Dict[str, UserConfig]:
    with open(f"{path}.csv", mode="r") as csv_file:
        user_configs = {}
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            line_count = +1
            if line_count > 0:
                # Ensure we always get the most recent entry.
                user_configs[row["Email"]] = UserConfig(
                    row["Email"],
                    datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S"),
                    int(row["Number of meals"]),
                    int(row["Number of persons"]),
                    list(calendar.day_name).index(row["Day to send shopping list"]),
                )
        return user_configs


def filter_user_configs(
    user_configs: Dict[str, UserConfig], day_number: int
) -> Dict[str, UserConfig]:
    """
    Only returns users whose contact_day is today.
    """
    selected_configs = {}

    for email, config in user_configs.items():
        if config.contact_day == day_number:
            selected_configs[email] = config

    return selected_configs
