import os
from dotenv import load_dotenv
from invoke.tasks import task

# do ENV=production command to run with production envars.
env_file = ".production.env" if os.getenv("ENV") == "production" else ".env"

load_dotenv(env_file)


@task()
def tailwind_init(ctx):
    if not os.path.exists("tailwindcss"):
        ctx.run(
            "curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64"
        )
        ctx.run("chmod +x tailwindcss-macos-arm64")
        ctx.run("mv tailwindcss-macos-arm64 tailwindcss")


@task(tailwind_init)
def tailwind_watch(ctx):
    print("running tailwind_watch!!!")
    ctx.run(
        "./tailwindcss -i ./static/input.css -o ./static/output.css --watch",
        pty=True,
        disown=True,
    )


@task()
def test(ctx, k=None):
    """
    Run pytest with optional arguments.
    """

    flags = f"-k {k}" if k else ""
    # Build the pytest command
    command = "pytest " + flags
    # Run the command
    ctx.run(command, pty=True)


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


@task(tailwind_watch)
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
    ctx.run("uvicorn app.main:app --host 0.0.0.0 --port 8080 --forwarded-allow-ips=*")


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
