from typing import TypedDict, Optional, cast
import logging
import json

from pint import UnitRegistry, UndefinedUnitError
from ingredient_parser import parse_ingredient
import nltk


pint = UnitRegistry()

# arbitrary units
pint.define("cloves = 1")
pint.define("bunches = 1")
pint.define("sprigs = 1")
pint.define("packs = 1")
pint.define("pinches = 1")
pint.define("stalks = 1")

def renamer(name):
    map = {
            "tomatoes": "tomato",
            "ripe tomatoes": "tomato",
            "onions": "onion",
            "red onions": "red onion",
            "eggs": "egg",
    }
    
    name = map.get(name, name)

    if "chillies" in name:
        return name.replace("chillies", "chilli")

    return name

def unit_renamer(unit):
    if unit == "g cans":
        return "g"

    return unit

def unit_to_str(units):
    return "" if str(units) == "dimensionless" else pint.get_symbol(str(units))


class Ingredient(TypedDict):
    name: str
    quantity: float
    unit: Optional[str]
    input: str
    comment: Optional[str]
    category: Optional[str]


def parse(description) -> Ingredient:
    nltk.download("averaged_perceptron_tagger")
    d = parse_ingredient(description)
    name = renamer(d["name"])
    unit = unit_renamer(d["unit"])

    return {
        "name": name,
        "quantity": float(d["quantity"] or 1),
        "unit": unit,
        "input": description,
        "comment": d["comment"],
    }  # type: ignore


def get_category(name: str) -> str:
    try:
        with open("data/categories.json", "r+") as f:
            categories = json.loads(f.read())
            for key, values in categories.items():
                if name in values:
                    return key

            choices = "\n".join(
                [f"({i}) {key}" for i, key in enumerate(categories.keys())]
            )
            choice = input(f"What is the category of: {name}\n{choices}\n")

            output = list(categories.keys())[int(choice)]

            # Now let's auto update the categories list.
            if output in categories:
                categories[output].append(name)
            else:
                categories[output] = [name]

            data = json.dumps(categories, indent=4, sort_keys=True)
            f.truncate()
            f.seek(0)
            f.write(data)

        return output
    except Exception:
        logging.exception("Error getting category")
        return ""


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
    keys = ["name", "quantity", "unit", "comment", "category"]

    if result is None:
        result = {}

    for key in keys:
        if key not in result:
            if key == "category":
                output = get_category(result["name"])
            else:
                output = input(f"What is the {key} of: {description}\n")

            result[key] = output

    result["input"] = description

    cast(Ingredient, result)
    return result  # type: ignore


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


def fixup(ingredient):
    keys = list(ingredient.keys())
    choices = "\n".join([f"({i}) {choice}" for i, choice in enumerate(keys)])
    result = "\n".join([f"{key}: {value}" for key, value in ingredient.items()])

    answer = input(f"Happy?\n{result}\n{choices}\n")

    if answer:
        key = keys[int(answer)]
        ingredient.pop(key)
        ingredient = ask(ingredient["input"], ingredient)
        return fixup(ingredient)

    return ingredient
