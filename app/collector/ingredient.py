from typing import TypedDict, Optional, cast
import logging
from pint import UnitRegistry, UndefinedUnitError
from ingredient_parser import parse_ingredient
import nltk

nltk.download("averaged_perceptron_tagger")
pint = UnitRegistry()

# arbitrary units
pint.define("cloves = 1")
pint.define("bunches = 1")
pint.define("sprigs = 1")
pint.define("packs = 1")


def unit_to_str(units):
    return "" if str(units) == "dimensionless" else pint.get_symbol(str(units))


class Ingredient(TypedDict):
    name: str
    quantity: float
    unit: Optional[str]
    input: str
    comment: Optional[str]


def parse(description) -> Ingredient:
    d = parse_ingredient(description)

    return {
        "name": d["name"],
        "quantity": float(d["quantity"]),
        "unit": d["unit"],
        "input": description,
        "comment": d["comment"],
    }  # type: ignore


def yield_factor(ingredient: Ingredient, yields: int):
    """
    Based on the recipe yield. Calculate the value of quantity of 1 serving.

    For instance:

        input: {"name": "butter", quantity: 200.0, unit: "g"}, yield: 4
        output: {"name": "butter", quantity: 50.0, unit: "g"}
    """
    ingredient["quantity"] = ingredient["quantity"] / yields
    return ingredient


def normalize(ingredient: Ingredient) -> Ingredient:
    try:
        quantity, unit = normalize_units(
            float(ingredient["quantity"]), ingredient["unit"]
        )
    except UndefinedUnitError:
        logging.warning(f"couldn't normalize unit:{ingredient['unit']}")
        return normalize(ask(ingredient["input"], {"name": ingredient["name"]}))
    except ValueError:
        logging.warning(f"couldn't normalize quantity:{ingredient['quantity']}")
        return normalize(ask(ingredient["input"], {"name": ingredient["name"]}))

    ingredient["quantity"] = quantity
    ingredient["unit"] = unit
    return ingredient


def ask(description, result=None) -> Ingredient:
    keys = ["name", "quantity", "unit", "comment"]
    if result is None:
        result = {}

    for key in keys:
        if key not in result:
            output = input(f"What is the {key} of: {description}\n")
            result[key] = output

    result["input"] = description

    cast(Ingredient, result)
    return result


def normalize_units(quantity: float, unit: Optional[str]):
    value = pint.Quantity(quantity, unit)
    base_units = get_base_units(value) or value.units
    value = value.to(base_units)
    magnitude = round(value.magnitude, 2)
    units = unit_to_str(value.units)
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
