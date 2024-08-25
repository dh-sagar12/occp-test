DOCKER_COMPOSE_DEV = docker/docker-compose.yml


start:
	docker compose -f $(DOCKER_COMPOSE_DEV) up app && docker attach occp-backend-1

build:
	docker compose -f $(DOCKER_COMPOSE_DEV) build

migrate-db:
	docker compose -f $(DOCKER_COMPOSE_DEV) exec app alembic -c alembic.dev.ini upgrade head

autogenerate:
	docker compose -f $(DOCKER_COMPOSE_DEV) exec app alembic -c alembic.dev.ini revision --autogenerate -m "revision"

stop:
	docker compose -p appointment-app -f $(DOCKER_COMPOSE_DEV) down
