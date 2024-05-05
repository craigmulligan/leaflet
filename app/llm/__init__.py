import os
import logging

from openai import OpenAI
from jinja2 import Template
from pydantic import BaseModel
from typing import List

from app import config

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


script_dir = os.path.dirname(os.path.abspath(__file__))

class LLM:
    def __init__(self):
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=config.LLM_KEY,
            base_url=config.LLM_HOST,
        )

    def generate(self):
        with open(os.path.join(script_dir, 'system_prompt.jinja')) as file:
            system_prompt = Template(file.read())
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        'role': 'system',
                        "content": system_prompt.render({ "recipe_count": 2 }),
                    },
                    {
                        'role': 'user',
                        "content": "I usually cook for 2 people, I'd like my recipes in the metric system. I'm allergic to ginger.",
                    }
                ],
                model='llama3',
                response_format={"type": "json_object"},
            )

            content = chat_completion.choices[0].message.content 

            if content is None:
                raise Exception("No content")

            logging.info(f"llm response {content}")
            return Response.model_validate_json(content)

    def generate_image(self, response: Response):
        return "/static/placeholder.webp" 
