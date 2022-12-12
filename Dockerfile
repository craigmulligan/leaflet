# Fetch the LiteFS binary using a multi-stage build.
# Final python app
FROM python:3.10-alpine

EXPOSE 8080

# RUN useradd -rm -d /home/user -s /bin/bash -g root -G sudo -u 1001 user 
# USER user

WORKDIR /home/user/app

RUN pip install --quiet --progress-bar off poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .
