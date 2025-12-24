.PHONY: help install run migrate makemigrations test shell createsuperuser collectstatic

help:
	@echo "Targets:"
	@echo "  install          Install Python dependencies"
	@echo "  run              Start development server"
	@echo "  migrate          Apply database migrations"
	@echo "  makemigrations   Create new migrations"
	@echo "  test             Run Django tests"
	@echo "  shell            Open Django shell"
	@echo "  createsuperuser  Create an admin user"
	@echo "  collectstatic    Collect static files"

install:
	pip install -r requirements.txt

run:
	python manage.py runserver

migrate:
	python manage.py migrate

makemigrations:
	python manage.py makemigrations

test:
	python manage.py test

shell:
	python manage.py shell

createsuperuser:
	python manage.py createsuperuser

collectstatic:
	python manage.py collectstatic --noinput
