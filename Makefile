# these will speed up builds, for docker-compose >= 1.25
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

all: down build up test

build:
	docker-compose build

up:
	docker-compose up 

create:
	docker-compose up --no-start

down:
	docker-compose down

restart: 
	docker-compose restart

start:
	docker-compose start
	
migrate:
	docker-compose run django sh -c 'aerich migrate'


logs:
	docker-compose logs django | tail -100


flake8:
	docker-compose run django sh -c 'flake8'

report:
	docker-compose run django sh -c 'coverage report'

test:
	docker-compose run django sh -c 'python manage.py test'