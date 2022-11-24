SHELL := /bin/sh
DIR := ${CURDIR}

lint_ci :
	black . --exclude "(migrations|venv)" --check
	isort . --check-only
	flake8 --ignore=E203,E128,E231,E302,E402,E501,W503,W605,E722 --exclude=venv
	mypy corshunter web --pretty

lint :
	black . --exclude "(migrations|venv)"
	isort .
	flake8 --ignore=E203,E128,E231,E302,E402,E501,W503,W605,E722 --exclude=venv
	mypy corshunter web --pretty

test :
	pytest --cov=web --cov-report html tests/

update_requirements :
	pip freeze > requirements.txt

make_migrations :
	python manage.py makemigrations web

migrate : make_migrations
	python manage.py migrate

run_server :
	python manage.py runserver 127.0.0.1:8080

package_to_zip :
	rm -rf package.tar.gz
	tar -czvf package.tar.gz corshunter tests vendor web Makefile manage.py Procfile requirements.txt release-tasks.sh