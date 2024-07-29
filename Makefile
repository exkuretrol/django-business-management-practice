.PHONY: run

run:
	@python manage.py runserver_plus

test:
	@python manage.py test

makemigrations:
	@python manage.py makemigrations core
	@python manage.py makemigrations branch
	@python manage.py makemigrations announcement
	@python manage.py makemigrations checklist
	@python manage.py makemigrations member

migrate:
	@python manage.py migrate

collectstatic:
	@python manage.py collectstatic

shell:
	@python manage.py shell_plus

clean:
	@find . -type f -name ".DS_Store" -execdir rm -rf {} \;
	@find . -type d -name "migrations" -execdir rm -rf {} \;
	@find . -type d -name "__pycache__" -execdir rm -rf {} \;
	@find . -type f -name "db.sqlite3" -execdir rm -rf {} \;
	@find ./media -type f -execdir rm -rf {} \;

