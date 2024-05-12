import os
import logging

from openai import OpenAI
from jinja2 import Template
from openai.types import Embedding
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

    def generate(self, user_prompt: str) -> Response:
        with open(os.path.join(script_dir, "system_prompt.jinja")) as file:
            system_prompt = Template(file.read())
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt.render({"recipe_count": 3}),
                    },
                    {
                        "role": "user",
                        "content": user_prompt or "",
                    },
                ],
                model="gpt-3.5-turbo-0125",
                response_format={"type": "json_object"},
            )

            content = chat_completion.choices[0].message.content

            if content is None:
                raise Exception("No content")

            logging.info(f"llm response {content}")
            return Response.model_validate_json(content)

    def generate_image(self, recipe: Recipe) -> str | None:
        with open(os.path.join(script_dir, "image_user_prompt.jinja")) as file:
            user_prompt = Template(file.read())
            images = self.client.images.generate(
                model="dall-e-2",
                size="512x512",
                prompt=user_prompt.render({"recipe": recipe}),
                response_format="b64_json",
            )

            return images.data[0].b64_json

    def generate_embeddings(self, text: str) -> List[float]:
        embeddings = self.client.embeddings.create(
            input=text, model="text-embedding-3-small"
        )
        return embeddings.data[0].embedding


def get_llm():
    llm = LLM()
    yield llm
