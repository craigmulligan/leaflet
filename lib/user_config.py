from typing import Dict
from datetime import datetime
from dataclasses import dataclass
import calendar
import csv


@dataclass
class UserConfig:
    """Config supplied for a user"""

    email: str
    timestamp: datetime
    meal_count: int = 1
    person_count: int = 1
    contact_day: int = 0


class UserConfigLoader:
    def __init__(self, user_configs_path: str):
        self.user_configs_path = user_configs_path

    def load_todays_user_configs(self) -> Dict[str, UserConfig]:
        """
        Returns a list of user_configs that should be contacted
        today.
        """
        weekday = datetime.today().weekday()
        return self.load_user_configs_by_weekday(weekday)

    def load_user_configs_by_weekday(self, weekday: int) -> Dict[str, UserConfig]:
        """
        Returns a list of user_configs that should be contacted
        on weekday.
        """
        user_configs = self.load_user_configs()
        selected_configs = {}

        for email, config in user_configs.items():
            if config.contact_day == weekday:
                selected_configs[email] = config

        return selected_configs

    def load_user_configs(self) -> Dict[str, UserConfig]:
        # TODO add some caching.
        with open(f"{self.user_configs_path}.csv", mode="r") as csv_file:
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
