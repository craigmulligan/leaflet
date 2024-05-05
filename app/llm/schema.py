from pydantic import BaseModel
from typing import List

class Ingredient(BaseModel):
    description: str
    unit: str
    amount: float

class Step(BaseModel):
    description: str

class Recipe(BaseModel):
    title: str
    servings: int
    estimated_time: int
    description: str
    steps: List[Step]
    ingredients: List[Ingredient]

class Response(BaseModel):
    recipes: List[Recipe]
    shopping_list: List[Ingredient]

