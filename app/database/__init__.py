import os
import json
from typing import Iterable, Optional, Union, Any, List
import logging

from contextlib import contextmanager
from flask import g, current_app, has_request_context
from datetime import datetime
from app.models import User, Recipe, Ingredient, LeafletEntry, DATETIME_FORMAT
import psycopg2
import psycopg2.extras
from psycopg2 import pool as pgpool

pool_key = "db_pool"

class Db:
    context_key = "_db_connection"

    def __init__(self, pool) -> None:
        self.conn = pool.getconn()

    @staticmethod
    def tear_down(_):
        """
        When app context is torn down
        close the db connection.
        """
        logging.info("closing db connection")
        db = getattr(g, Db.context_key, None)
        pool = current_app.config[pool_key]
        if db is not None:
            db.conn.close()
            pool.putconn(db.conn)

    def user_create(self, email) -> User:
        User.validate_email(email)
        user = self.query(
            """
            INSERT INTO "user" (email) VALUES (%s) RETURNING *
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
            UPDATE "user" set recipes_per_week = %s, serving = %s where id = %s RETURNING *;
            """,
            [recipes_per_week, serving, user_id],
            one=True,
        )

        self.conn.commit()
        assert user
        return User(**user)

    def user_update_send_at(self, user_id: int, send_at: datetime):
        user = self.query(
            """
            UPDATE "user" set send_at = %s where id = %s RETURNING *;
            """,
            [send_at.strftime(DATETIME_FORMAT), user_id],
            one=True,
        )

        self.conn.commit()
        assert user
        return User(**user)


    def user_get_all_by_weekday(self, weekday: int) -> Iterable[User]:
        """
        Returns all users who should be emailed this weekday 
        """
        cur = self.query('select * from "user" where extract(isodow from send_at::timestamp)  = %s', [weekday])

        if cur:
            for row in cur:
                yield User(**row)


    def user_get_candidates(self, weekday: int) -> Iterable[User]:
        """
        Returns all users who should be emailed this weekday 
        """
        cur = self.query('''
             with non_candidates as (
                select user_id from leaflet_entry
                where date(created_at) = date(now())
                and created_by = 'schedule' 
                group by user_id
             )
             select "user".* from "user"
             left join non_candidates on non_candidates.user_id = "user".id
             where extract(isodow from send_at::timestamp) = %s
             and non_candidates.user_id is NULL;
        ''', [weekday])

        if cur:
            for row in cur:
                yield User(**row)

    def user_get_by_email(self, email: str):
        user = self.query(
            'select * from "user" where email = %s limit 1', [email], one=True
        )

        if user:
            return User(**user)

    def user_get_by_id(self, user_id: int):
        user = self.query(
            'select * from "user" where id = %s limit 1', [user_id], one=True
        )
        if user:
            return User(**user)

    def ingredient_insert(self, recipe_id, name, quantity, unit, category):
        self.query(
            """
            INSERT INTO ingredient (recipe_id, name, quantity, unit, category) VALUES (%s, %s, %s, %s, %s) ON CONFLICT(recipe_id, name)
            DO UPDATE SET name = EXCLUDED.name, quantity = EXCLUDED.quantity, unit = EXCLUDED.unit, category = EXCLUDED.category;
            """,
            [recipe_id, name, quantity, unit, category],
            one=True,
        )

        self.conn.commit()

    def leaflet_entry_insert(self, leaflet_id, recipe_id, user_id):
        created_by = "schedule"

        if has_request_context():
            created_by = "user"

        self.query(
            """
            INSERT INTO leaflet_entry (leaflet_id, recipe_id, user_id, created_by) VALUES (%s, %s, %s, %s)
            """,
            [leaflet_id, recipe_id, user_id, created_by],
        )

        self.conn.commit()

    def leaflet_get_all_by_user(self, user_id: int, limit=100):
        rows = self.query(
            """
            SELECT * FROM (
              SELECT DISTINCT ON (leaflet_id) *
              FROM leaflet_entry 
              WHERE user_id = %s 
              ORDER BY leaflet_id, created_at DESC
            ) t
            ORDER BY created_at DESC
            LIMIT %s
            """,
            [user_id, limit],
        )

        if not rows:
            return [] 

        return [LeafletEntry(**r) for r in rows] 

    def leaflet_count_by_user(self, user_id: int) -> int:
        res = self.query(
            """
            select count(DISTINCT leaflet_id) as count from leaflet_entry where user_id = %s
            """,
            [user_id],
            one=True
        )

        if not res:
            return 0 

        return res["count"] 

    def recipe_get_all_by_leaflet_id(self, leaflet_id: int):
        rows = self.query(
            """
            SELECT recipe_id
            FROM leaflet_entry
            where leaflet_id = %s
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
            where id = %s
            limit 1
            """,
            [recipe_id],
            one=True,
        )

        ingredients = self.query(
            """
            SELECT *
            FROM ingredient
            where recipe_id = %s
            order by name
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
                where user_id = %s
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
            where recipe_id = %s
            """,
            [recipe_id],
        )

        if not ingredients:
            raise Exception("Recipe not found")

        names = [ingredient["name"] for ingredient in ingredients]
        seq = ",".join(["%s"] * len(names))

        res = self.query(
            f"""
            with recipe_relevance as (
                select recipe_id, count(recipe_id) as count
                from ingredient
                where ingredient.name in ({seq})
                group by recipe_id
            )

            SELECT id FROM recipe
            LEFT JOIN recipe_relevance on recipe.id = recipe_relevance.recipe_id
            where recipe_id <> %s
            ORDER BY recipe_relevance.count DESC
            limit %s;
            """,
            [*names, recipe_id, limit],
        )

        if res is None:
            raise Exception("Recipe not found")

        recipe_ids = [r["id"] for r in res]

        return recipe_ids

    def recipe_insert(
        self, recipe_id, title, canonical_url, yields, total_time, instructions
    ):
        self.query(
            """
            INSERT INTO recipe (id, title, canonical_url, yields, total_time, instructions) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
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
                            ingredient["category"],
                        )

    def recipe_count(self):
        row = self.query("select count(*) as count from recipe;", one=True)
        assert row
        return row["count"]

    def query(self, query, query_args=(), one=False) -> Union[Optional[Any], Any]:
        cur = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cur.execute(query, query_args)

        if not cur.description:
            cur.close()
            return None
            
        if one:
           rv = cur.fetchone()
        else: 
           rv = cur.fetchall()

        cur.close()
        return rv

    @contextmanager
    def lock(self, id: int):
        acquired = False
        try:
            logging.info(f"acquiring lock:{id}")
            row = self.query("select pg_try_advisory_lock(%s)", [id], one=True)
            assert row
            acquired = row["pg_try_advisory_lock"]
            if acquired:
                logging.info(f"acquired lock:{id}")
            else:
                logging.info(f"could not acquired lock:{id}")
            yield acquired
        finally:
            if acquired:
               self.query("select pg_advisory_unlock(%s)", [id], one=True)
               logging.info(f"unlocking lock:{id}")


def register(app):
    app.config[pool_key] = pgpool.SimpleConnectionPool(1, 20, dsn=app.config["DATABASE_URL"])
    app.teardown_appcontext(Db.tear_down)

def create():
    pool = current_app.config[pool_key] 
    return Db(pool)

def get() -> Db:
    db = getattr(g, Db.context_key, None)
    if db is None:
        db = create()
        setattr(g, Db.context_key, db)

    return db
