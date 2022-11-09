import json
import requests
from time import sleep
from typing import Protocol, List
from recipe_scrapers._abstract import AbstractScraper
from .ingredient import Ingredient, parse
from recipe_scrapers import scrape_me


class Recipe:
    def __init__(self, url: str, schema: AbstractScraper) -> None:
        self.schema = schema
        self.url = url

    @staticmethod
    def from_url(url):
        schema = scrape_me(
            url,
        )
        return Recipe(url, schema)

    def ingredients(self) -> List[Ingredient]:
        data = []
        for i in self.schema.ingredients():
            data.append(parse(i))

        return data

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.schema.title(),
                "ingredients": self.ingredients(),
                "yields": self.schema.yields(),
                "instructions": self.schema.instructions(),
                "host": self.schema.host(),
                "total_time": self.schema.total_time(),
                "prep_time": self.schema.prep_time(),
                "cook_time": self.schema.cook_time(),
                "canonical_url": self.schema.canonical_url(),
            }
        )


class Persister:
    def save(self, url: str, body: str) -> bool:
        print(url, body)
        return True

    def exists(self, url: str) -> bool:
        print(url)
        return True


class RecipeCollector:
    def __init__(self, persister: Persister) -> None:
        self.persister = persister

    def run(self, urls: List[str]):
        for url in urls:
            if not self.persister.exists(url):
                try:
                    recipe = Recipe.from_url(url)
                    self.persister.save(url, recipe.to_json())
                except Exception as e:
                    print(e)


def collect_urls(url_filename):
    """
    Handy function to collect all veggie urls on bbcgoodfood
    """
    host = "https://www.bbcgoodfood.com"
    next_url = f"{host}/api/lists/posts/list/healthy-vegetarian-recipes/items?page=1"

    with open(url_filename, "a") as f:
        while True:
            res = requests.get(next_url)
            res.raise_for_status()
            data = res.json()
            next_url = data["nextUrl"]

            for item in data["items"]:
                try:
                    f.write(host + item["url"] + "\n")
                except Exception as e:
                    print(e)

            if next_url is None:
                break

            sleep(3)
