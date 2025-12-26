.PHONY: help venv install run migrate makemigrations test shell createsuperuser collectstatic

PYTHON ?= python3

help:
	@echo "Targets:"
	@echo "  venv             Create a local virtualenv in .venv"
	@echo "  install          Install Python dependencies"
	@echo "  run              Start development server"
	@echo "  migrate          Apply database migrations"
	@echo "  makemigrations   Create new migrations"
	@echo "  test             Run Django tests"
	@echo "  shell            Open Django shell"
	@echo "  createsuperuser  Create an admin user"
	@echo "  collectstatic    Collect static files"

venv:
	$(PYTHON) -m venv .venv
	@echo "Activate with: source .venv/bin/activate"

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) manage.py runserver

migrate:
	$(PYTHON) manage.py migrate

makemigrations:
	$(PYTHON) manage.py makemigrations

test:
	$(PYTHON) manage.py test

shell:
	$(PYTHON) manage.py shell

createsuperuser:
	$(PYTHON) manage.py createsuperuser

collectstatic:
	$(PYTHON) manage.py collectstatic --noinput
