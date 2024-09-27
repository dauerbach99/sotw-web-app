WHOAMI = $(shell whoami)

# DB parameters
DB_NAME := sotw
DB_TEST_NAME := sotw_test
DB_DEV_USER := clarice
DB_DEV_PASS := clarice
ENV := dev

# docker-compose automation
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build: docker-build-nginx docker-build-backend docker-build-frontend

docker-build-prod: 
	ENV := prod
	docker-build-prod-nginx docker-build-backend docker-build-frontend

# docker-build-backend:
# 	. venv/bin/activate && ./venv/bin/pip freeze > ./app/requirements.txt
# 	cd app && docker build --no-cache -t sotw-api .
docker-build-backend:
	cp alembic.ini app/
	cd app && docker build --no-cache --build-arg BUILD_ENV=$(ENV) -t sotw-api .
	rm app/alembic.ini

docker-build-nginx:
	cd nginx && docker build -f Dockerfile.dev --no-cache -t sotw-nginx .

docker-build-prod-nginx:
	cd nginx && docker build --no-cache -t sotw-nginx .

docker-build-frontend:
	cd frontend && docker build --no-cache -t sotw-frontend .


# development automation
dev-backend-up:
	@echo "Starting up backend"
	. venv/bin/activate && ./venv/bin/python run_dev.py

dev-backend-full-up: db-up
	@echo "Starting up backend"
	. venv/bin/activate && ./venv/bin/python run_dev.py

dev-frontend-up:
	@echo "Starting up frontend"
	cd frontend && npm install && npm run serve

# postgres automation
db-up: build-db build-db-data

build-db:
	@echo "Building database '$(DB_NAME)'"
	echo "CREATE USER $(DB_DEV_USER) WITH PASSWORD '$(DB_DEV_PASS)'" | psql -d postgres
	echo "CREATE DATABASE $(DB_NAME) WITH OWNER $(DB_DEV_USER) ENCODING 'UTF8'" | psql -d postgres
	echo "CREATE DATABASE $(DB_TEST_NAME) WITH OWNER $(DB_DEV_USER) ENCODING 'UTF8'" | psql -d postgres
	
build-db-data:
	. venv/bin/activate && ./venv/bin/alembic upgrade head
	@echo "Initializing database data"
	. venv/bin/activate && ./venv/bin/python run_seed.py

db-down: clean-db-data clean-db

clean-db-data:
	@echo "Cleaning database data"
	echo "DROP SCHEMA public CASCADE" | psql -d $(DB_NAME)
	echo "CREATE SCHEMA public" | psql -d $(DB_NAME)
	echo "GRANT ALL ON SCHEMA public TO public" | psql -d $(DB_NAME)
	echo "GRANT ALL ON SCHEMA public TO $(WHOAMI)" | psql -d $(DB_NAME)

clean-db:
	@echo "Deleting database $(DB_NAME)"
	echo "DROP DATABASE IF EXISTS $(DB_NAME)" | psql -d postgres
	echo "DROP DATABASE IF EXISTS $(DB_TEST_NAME)" | psql -d postgres