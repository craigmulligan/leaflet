import os
import json
from typing import Optional, Union, Any, List

# from datetime import datetime
import sqlite3
from flask import g, current_app
from app.models import User, Recipe, Ingredient

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Db:
    context_key = "_db_connection"

    def __init__(self, app) -> None:
        db_url = app.config["DB_URL"]
        connection = sqlite3.connect(db_url)
        connection.row_factory = self.make_dicts
        self.conn = connection

    @staticmethod
    def tear_down(_):
        """
        When app context is torn down
        close the db connection.
        """
        db = getattr(g, Db.context_key, None)
        if db is not None:
            db.conn.close()

    @staticmethod
    def make_dicts(cursor, row):
        return dict(
            (cursor.description[idx][0], value) for idx, value in enumerate(row)
        )

    def setup(self):

        """
        initializes schema
        """
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL, 
                created_at TEXT DEFAULT (datetime('now')) NOT NULL,
                recipes_per_week INTEGER DEFAULT 1,
                serving INTEGER DEFAULT 1,
                send_at TEXT DEFAULT (datetime('now')) 
            );
        """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recipe (
                id TEXT PRIMARY KEY, 
                canonical_url TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now')) NOT NULL,
                instructions TEXT NOT NULL, 
                title TEXT NOT NULL,
                total_time INTEGER NOT NULL,
                yields INTEGER
            );
        """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingredient (
                recipe_id TEXT,
                created_at TEXT DEFAULT (datetime('now')) NOT NULL,
                unit TEXT,
                quantity INTEGER NOT NULL,
                name TEXT NOT NULL,
                PRIMARY KEY (recipe_id, name),
                FOREIGN KEY(recipe_id) REFERENCES recipe(id)
            );
        """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leaflet_entry (
                id INTEGER PRIMARY KEY, 
                leaflet_id TEXT,
                created_at TEXT DEFAULT (datetime('now')) NOT NULL,
                recipe_id TEXT,
                user_id INTEGER,
                FOREIGN KEY(recipe_id) REFERENCES recipe(id),
                FOREIGN KEY(user_id) REFERENCES user(id)
            );
        """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS user_email_idx ON user(email);
        """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS user_created_at_idx ON user(created_at);
        """
        )

    def user_create(self, email) -> User:
        User.validate_email(email)
        user = self.query(
            """
            INSERT INTO user (email) VALUES (?) RETURNING *
            """,
            [email],
            one=True,
        )

        self.conn.commit()
        assert user
        return User(**user)

    def user_update(self, user_id: int, recipes_per_week: int, serving: int):
        user = self.query(
            """
            UPDATE user set recipes_per_week = ?, serving = ? where id = ? RETURNING *;
            """,
            [recipes_per_week, serving, user_id],
            one=True,
        )

        self.conn.commit()
        assert user
        return User(**user)

    def user_get_by_email(self, email: str):
        user = self.query(
            "select * from user where email = ? limit 1", [email], one=True
        )
        if user:
            return User(**user)

    def user_get_by_id(self, user_id: int):
        user = self.query(
            "select * from user where id = ? limit 1", [user_id], one=True
        )
        if user:
            return User(**user)

    def ingredient_insert(self, recipe_id, name, quantity, unit):
        self.query(
            """
            INSERT OR IGNORE INTO ingredient (recipe_id, name, quantity, unit) VALUES (?, ?, ?, ?)
            """,
            [recipe_id, name, quantity, unit],
            one=True,
        )

        self.conn.commit()

    def leaflet_entry_insert(self, leaflet_id, recipe_id, user_id):
        self.query(
            """
            INSERT INTO leaflet_entry (leaflet_id, recipe_id, user_id) VALUES (?, ?, ?)
            """,
            [leaflet_id, recipe_id, user_id],
        )

        self.conn.commit()

    def leaflet_get_all_by_user(self, user_id: int, limit=100):
        res = self.query(
            """
            select leaflet_id from leaflet_entry where user_id = ? group by leaflet_id order by created_at desc limit ?
            """,
            [user_id, limit],
        )

        if not res:
            return res

        return [r["leaflet_id"] for r in res]

    def recipe_get_all_by_leaflet_id(self, leaflet_id: int):
        rows = self.query(
            """
            SELECT recipe_id
            FROM leaflet_entry
            where leaflet_id = ?
            """,
            [leaflet_id],
        )

        assert rows
        return [row["recipe_id"] for row in rows]

    def recipe_get(self, recipe_id) -> Optional[Recipe]:
        recipe = self.query(
            """
            SELECT *
            FROM recipe 
            where id = ?
            limit 1
            """,
            [recipe_id],
            one=True,
        )

        ingredients = self.query(
            """
            SELECT *
            FROM ingredient
            where recipe_id = ?
            """,
            [recipe_id],
        )

        if not ingredients:
            raise Exception(f"Could not find ingredients for {recipe_id}")

        return Recipe(
            **recipe, ingredients=[Ingredient(**i) for i in ingredients]  # type: ignore
        )  # type:ignore

    def recipe_random(self, user_id: int) -> Optional[str]:
        """
        This will randomly select a recipe ordered by the number
        of times the user has recieved it.
        """
        res = self.query(
            """
            with recipe_count as (
                select recipe_id, count(recipe_id) as c from leaflet_entry
                where user_id = ?
                group by recipe_id
            )
            select id, c from recipe
            LEFT JOIN recipe_count on recipe_id = id
            ORDER BY c, random() LIMIT 1
            """,
            [user_id],
            one=True,
        )

        if res:
            return res["id"]

        return None

    def recipe_similar(self, recipe_id, limit) -> List[str]:
        """
        Gets recipe that have common ingredients
        """
        ingredients = self.query(
            """
            SELECT name
            FROM ingredient
            where recipe_id = ?
            """,
            [recipe_id],
        )

        if not ingredients:
            raise Exception("Recipe not found")

        names = [ingredient["name"] for ingredient in ingredients]
        seq = ",".join(["?"] * len(names))

        res = self.query(
            f"""
            select recipe_id, count(recipe_id) as count
            from ingredient
            where recipe_id is not ?
            and ingredient.name in ({seq})
            group by recipe_id
            order by count desc
            limit ?   
            """,
            [recipe_id, *names, limit],
        )

        if res is None:
            raise Exception("Recipe not found")

        recipe_ids = [r["recipe_id"] for r in res]

        return recipe_ids

    def recipe_insert(
        self, recipe_id, title, canonical_url, yields, total_time, instructions
    ):
        self.query(
            """
            INSERT OR IGNORE INTO recipe (id, title, canonical_url, yields, total_time, instructions) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [recipe_id, title, canonical_url, yields, total_time, instructions],
            one=True,
        )

        self.conn.commit()

    def recipe_load(self, directory, recipe_ids=None):
        for recipe_id in os.listdir(directory):
            # checking if it is a file
            with open(os.path.join(directory, recipe_id), "r") as f:
                data = json.load(f)
                if recipe_ids is None or data["id"] in recipe_ids:
                    self.recipe_insert(
                        data["id"],
                        data["title"],
                        data["canonical_url"],
                        data["yields"],
                        data["total_time"],
                        data["instructions"],
                    )

                    for ingredient in data["ingredients"]:
                        self.ingredient_insert(
                            data["id"],
                            ingredient["name"],
                            ingredient["quantity"],
                            ingredient["unit"],
                        )

    def query(self, query, query_args=(), one=False) -> Union[Optional[Any], Any]:
        cur = self.conn.execute(query, query_args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


def register(app):
    app.teardown_appcontext(Db.tear_down)


def get() -> Db:
    db = getattr(g, Db.context_key, None)
    if db is None:
        db = Db(current_app)
        setattr(g, Db.context_key, db)

    return db
