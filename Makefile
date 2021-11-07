init_db:
	wget --output-file="logs.csv" "${GSHEET_URL}" -O "data/db/users.csv"

init_cli:
	curl -L https://github.com/cooklang/CookCLI/releases/download/v0.0.10/CookCLI_0.0.10_linux_amd64.zip > /tmp/cooklang.zip && unzip -d ./bin /tmp/cooklang.zip

test_watch:
	poetry run ptw -- --testmon -vv

test:
	poetry run pytest

shell:
	poetry shell

install: 
	poetry install

run:
	python run_job.py

ci: init_cli install test 

cron: init_cli install run
