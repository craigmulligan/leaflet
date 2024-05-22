from dotenv import load_dotenv
from invoke.tasks import task

load_dotenv(".env.production")


@task
def db_rev(ctx, message):
    """
    Generate a new Alembic migration script with the specified message.
    """
    ctx.run(f"alembic revision --autogenerate -m '{message}'")


@task
def db_up(ctx):
    """
    Apply Alembic migrations to the database.
    """
    ctx.run("alembic upgrade head")


@task
def db_down(ctx):
    """
    Apply Alembic migrations to the database.
    """
    ctx.run("alembic downgrade cb0dd456e4cc")


@task
def server(ctx):
    """
    Start the FastAPI server in development mode on port 8080.
    """
    ctx.run("uvicorn app.main:app --reload --port 8080")


@task
def server_prod(ctx):
    """
    Start the FastAPI server in on port 8080.
    """
    ctx.run("uvicorn app.main:app --port 8080")


@task
def worker_prod(ctx):
    """
    Run the worker
    """
    ctx.run("python3 worker.py")


@task
def worker(ctx):
    """
    Run the worker
    """
    ctx.run("python3 worker_dev.py")


@task
def lint(ctx):
    """
    lint code
    """
    ctx.run("ruff check")
