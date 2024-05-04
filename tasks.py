from invoke.tasks import task 

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
def server_dev(ctx):
    """
    Start the FastAPI server in development mode on port 8080.
    """
    ctx.run("uvicorn app.main:app --reload --port 8080")