# Fetch the LiteFS binary using a multi-stage build.
# Final python app
FROM python:3.10-alpine

EXPOSE 8080

WORKDIR /home/user/app

RUN pip install --quiet --progress-bar off poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .
