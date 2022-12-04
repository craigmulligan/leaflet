# Fetch the LiteFS binary using a multi-stage build.
FROM flyio/litefs:0.3.0-beta7 AS litefs

# Final python app
FROM python:3.10-alpine

COPY --from=litefs /usr/local/bin/litefs /usr/local/bin/litefs

RUN apk add build-base

RUN apk add bash curl fuse sqlite

EXPOSE 8080

# RUN useradd -rm -d /home/user -s /bin/bash -g root -G sudo -u 1001 user 
# USER user

WORKDIR /home/user/app

RUN pip install --quiet --progress-bar off poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

COPY etc/litefs-worker.yml /etc/
COPY etc/litefs-web.yml /etc/

RUN mkdir -p /data /mnt/data
