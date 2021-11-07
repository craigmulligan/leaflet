from dataclasses import dataclass


@dataclass
class Result:
    """Single Ingredient spec"""

    email: str
    # currently 0 for success 1 for failure.
    int: bool
    message: str = ""
