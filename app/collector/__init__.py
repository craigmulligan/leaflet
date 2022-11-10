import re
from typing import Optional
import logging
from pathlib import Path
import os
import json
import requests
import hashlib

from time import sleep
from typing import List
from recipe_scrapers._abstract import AbstractScraper
from .ingredient import Ingredient, parse
from recipe_scrapers import scrape_me


class Recipe:
    def __init__(self, url: str, schema: AbstractScraper) -> None:
        self.url = url
        self.schema = schema

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

    def yields(self) -> Optional[int]:
        txt = self.schema.yields()
        matches = re.findall("[0-9]+", txt)
        if not matches:
            return None

        return int(matches[0])

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.schema.title(),
                "ingredients": self.ingredients(),
                "yields": self.yields(),
                "instructions": self.schema.instructions(),
                "host": self.schema.host(),
                "total_time": self.schema.total_time(),
                "canonical_url": self.schema.canonical_url(),
            },
            indent=4,
            sort_keys=True,
        )


class Persister:
    def __init__(self, dirname="data/recipe") -> None:
        self.dirname = dirname
        Path(dirname).mkdir(parents=True, exist_ok=True)

    def hash(self, url: str) -> str:
        "hash a url this is so it's encoded and fixed length"
        sha_1 = hashlib.sha1()
        sha_1.update(url.encode("utf-8"))
        return sha_1.hexdigest()

    def save(self, url: str, body: str) -> bool:
        id = self.hash(url)
        with open(f"{self.dirname}/{id}", "w+") as f:
            f.write(body)
        return True

    def exists(self, url: str) -> bool:
        id = self.hash(url)
        return os.path.isfile(f"{self.dirname}/{id}")


def collect_recipes(persister, url_file):
    with open(url_file) as f:
        for line in f.readlines():
            url = line.strip()
            if not persister.exists(url):
                recipe = Recipe.from_url(url)
                try:
                    persister.save(url, recipe.to_json())
                    logging.info(f"saved!")
                except Exception:
                    logging.exception("Couldn't save recipe")


def collect_urls(url_filename):
    """
    Handy function to collect all veggie urls on bbcgoodfood
    """
    host = "https://www.bbcgoodfood.com"
    next_url = f"{host}/api/lists/posts/list/healthy-vegetarian-recipes/items?page=1"

    if os.path.isfile(url_filename):
        logging.info("urls already collected.")
        return

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