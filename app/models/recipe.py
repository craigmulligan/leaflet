from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Ingredient:
    name: str
    unit: Optional[str]
    quantity: float
    recipe_id: str
    created_at: str


@dataclass
class Recipe:
    id: str
    title: str
    canonical_url: str
    instructions: str
    total_time: int
    created_at: str
    yields: int
    ingredients: List[Ingredient]
