from typing import TypedDict
import logging
from pint import UnitRegistry, UndefinedUnitError
from ingredient_parser import parse_ingredient
import nltk

nltk.download("averaged_perceptron_tagger")
pint = UnitRegistry()


class Ingredient(TypedDict):
    name: str
    quantity: float
    unit: str


def parse(description) -> Ingredient:
    d = parse_ingredient(description)
    quantity, unit = normalize_units(float(d["quantity"]), d["unit"])
    return {"name": d["name"], "quantity": quantity, "unit": unit}  # type: ignore


def normalize_units(quantity: float, unit: str):
    try:
        value = pint.Quantity(quantity, unit)
    except UndefinedUnitError:
        logging.warning(f"couldn't get normalize unit:{unit}")
        return quantity, unit
    except ValueError:
        logging.warning(f"couldn't get normalize quantity:{quantity}")
        return quantity, unit

    base_units = get_base_units(value) or value.units
    value = value.to(base_units)
    magnitude = round(value.magnitude, 2)
    units = None if value.dimensionless else pint.get_symbol(str(value.units))
    return magnitude, units


def get_base_units(quantity):
    dimensionalities = {
        None: pint.Quantity(1),
        "energy": pint.Quantity(1, "cal"),
        "length": pint.Quantity(1, "cm"),
        "volume": pint.Quantity(1, "ml"),
        "weight": pint.Quantity(1, "g"),
    }
    dimensionalities = {
        v.dimensionality: pint.get_symbol(str(v.units)) if k else None
        for k, v in dimensionalities.items()
    }
    return dimensionalities.get(quantity.dimensionality)
