pre-commit.install:
	pipenv run pre-commit install

compose.deps.dev.down:
	docker-compose -f compose.deps.dev.yml down

compose.deps.dev:
	docker-compose -f compose.deps.dev.yml up -d

makemigrations:
	pipenv run python src/manage.py makemigrations

migrate:
	pipenv run python src/manage.py migrate

createsuperuser:
	pipenv run python src/manage.py createsuperuser

run:
	pipenv run python src/manage.py runserver

lint:
	pipenv run ruff format src/
	pipenv run ruff check src/ --fix
	pipenv run mypy src/

test:
	pipenv run pytest src/
