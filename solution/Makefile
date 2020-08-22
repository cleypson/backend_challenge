migrate:
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate

build:
	docker-compose build db
	docker-compose build web

up:
	docker-compose up -d db
	sleep 5
	docker-compose up web

stop:
	docker-compose stop web
	docker-compose stop db

test:
	docker-compose exec web python manage.py test

shell:
	docker-compose exec web python manage.py shell