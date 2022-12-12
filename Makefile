SHELL := /bin/sh
DIR := ${CURDIR}

lint_ci :
	black . --exclude "(migrations|venv)" --check
	isort . --check-only
	flake8 --ignore=E203,E128,E231,E302,E402,E501,W503,W605,E722 --exclude=venv
	mypy ofcors web --pretty

lint :
	black . --exclude "(migrations|venv)"
	isort .
	flake8 --ignore=E203,E128,E231,E302,E402,E501,W503,W605,E722 --exclude=venv
	mypy ofcors web --pretty

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
	rm -rf terraform/package.tar.gz
	tar -czvf package.tar.gz ofcors tests vendor web Makefile manage.py Procfile requirements.txt release-tasks.sh
	mv package.tar.gz terraform

deploy_infrastructure : package_to_zip
	echo "Deploying infrastructure based on contents of '$(CONFIG_FILE)' configuration file..."
	$(eval HEROKU_APP_NAME := $(shell python manage.py get_terraform_arg -f $(CONFIG_FILE) -a heroku_app_name_var))
	$(eval CLOUDFLARE_API_TOKEN := $(shell python manage.py get_terraform_arg -f $(CONFIG_FILE) -a cloudflare_api_token))
	$(eval HOST_DOMAINS := $(shell python manage.py get_terraform_arg -f $(CONFIG_FILE) -a host_domains))
	cd terraform && terraform apply -var $(HEROKU_APP_NAME) -var $(CLOUDFLARE_API_TOKEN) -var $(HOST_DOMAINS) -auto-approve

configure_heroku :
	echo "Configuring Heroku deployment based on contents of '$(CONFIG_FILE)' configuration file..."
	$(eval HEROKU_APP_NAME := $(shell python manage.py get_terraform_arg -f $(CONFIG_FILE) -a heroku_app_name))
	$(eval YAML_CONTENT := $(shell cat $(CONFIG_FILE) | base64))
	heroku run -a $(HEROKU_APP_NAME) "python manage.py configure_from_yaml -s $(YAML_CONTENT)"

open_heroku_console :
	echo "Opening a browser to the results viewing page for the remote deployment on Heroku (config file at '$(CONFIG_FILE)')..."
	$(eval HEROKU_APP_NAME := $(shell python manage.py get_terraform_arg -f $(CONFIG_FILE) -a heroku_app_name))
	$(eval TICKET_URL := $(shell heroku run -a $(HEROKU_APP_NAME) "python manage.py view_results --url-only"))
	open $(TICKET_URL)

deploy_and_configure : deploy_infrastructure configure_heroku
