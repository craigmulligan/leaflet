init_db: init_db_dir
	wget "${GSHEET_URL}" -O "data/db/users.csv"

init_cli:
	curl -L https://github.com/cooklang/CookCLI/releases/download/v0.0.10/CookCLI_0.0.10_linux_amd64.zip > /tmp/cooklang.zip && unzip -d ./bin /tmp/cooklang.zip

init_db_dir:
	mkdir -p data/db

test_watch:
	poetry run ptw -- --testmon -vv

test:
	poetry run pytest

shell:
	poetry shell

install: 
	poetry install

run:
	poetry run python run.py

mypy:
	poetry run mypy . 

ci_test: init_cli install mypy test

ci_cron: init_cli init_db install run
