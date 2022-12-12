import os
import subprocess
import logging
import shlex
import click
from flask.cli import AppGroup
from flask import current_app
from app import database
from app.collector import collect_recipes, collect_urls, Persister

logging.basicConfig(level=logging.INFO)

dev = AppGroup("dev", short_help="All development commands")
db = AppGroup("db", short_help="All database commands")
prod = AppGroup("prod", short_help="All production commands")
recipes = AppGroup("recipes", short_help="All recipe commands")


def run_sh(cmd: str, env=None, popen=False):
    copied_env = os.environ.copy()

    if env:
        copied_env.update(env)

    args = shlex.split(cmd)

    if popen:
        return subprocess.Popen(args, env=copied_env)

    ret = subprocess.call(args, env=copied_env)
    exit(ret)

def db_init():
    logging.info("Initializing db")

    try:
        run_sh(f"yoyo apply --database {current_app.config['DATABASE_URL']} --batch", popen=True)
    except Exception as e:
        print(e) 
    db = database.get()
    db.recipe_load("data/recipe")

@db.command("new")
def db_migration_new():
    run_sh("yoyo new --sql ./migrations")

@db.command("init")
def run_db_init():
    db_init()

@recipes.command("collect")
def recipes_collect():
    """
    This fetchs recipes and saves them
    to data/*

    From there we can manually correct them if needed
    and then load into the db.

    NOTE: If any of the files exist, we don't overwrite them.
    This is so we can maintain manual fixes. If you want a file
    to be regenerated you must delete it from /data
    """

    url_file = "data/test.txt"
    persister = Persister()
    collect_urls(url_file)
    collect_recipes(persister, url_file)


@prod.command("server")
def prod_server():
    db_init()
    return run_sh(
        "gunicorn 'run_app:app' -b 0.0.0.0:8080",
    )


@prod.command("worker")
def prod_worker():
    db_init()
    # Note we are using the solo pool class
    # because we only run 2 tasks and need to keep memory usage down. 
    return run_sh("celery --app 'run_app:celery' worker --without-gossip -B -c 1 --pool solo")


@dev.command("test")
@click.option("--watch", default=False, is_flag=True, help="watch mode")
@click.argument("pytest_options", nargs=-1, type=click.UNPROCESSED)
def test(watch: bool, pytest_options):
    pytest_flags = " ".join(pytest_options)

    if watch:
        run_sh(f"ptw -- --testmon {pytest_flags}")

    run_sh(f"pytest {pytest_flags}")


def run_server(popen=False):
    db_init()
    return run_sh(
        "flask run --host 0.0.0.0 --port 8080",
        env={"FLASK_DEBUG": "1"},
        popen=popen,
    )


def run_worker(popen=False):
    db_init()
    return run_sh(
        "watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery --app run_app:celery worker --without-gossip -B",
        env={"FLASK_DEBUG": "development"},
        popen=popen,
    )


@dev.command("server")
def run_server_command():
    return run_server()


@dev.command("worker")
def run_worker_command():
    return run_worker()


@dev.command("run")
def run_all():
    """Run both the worker and dev server"""
    procs = [run_worker(popen=True), run_server(popen=True)]
    for p in procs:
        p.wait()


@dev.command("fmt")
@click.argument("black_options", nargs=-1, type=click.UNPROCESSED)
def run_fmt(black_options):
    black_flags = " ".join(black_options)
    run_sh(f"black . {black_flags}")


@dev.command("mypy")
def run_mypy():
    run_sh("pyright .")


def register(app):
    app.cli.add_command(dev)
    app.cli.add_command(db)
    app.cli.add_command(prod)
    app.cli.add_command(recipes)
