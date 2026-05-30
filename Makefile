DC   = docker compose
EXEC = docker exec -it

APP_CONTAINER = payment-service-api


.PHONY: run
run: stop
	$(DC) up -d

.PHONY: services-run
services-run:
	$(DC) up -d --scale api=0 --scale consumer=0

.PHONY: stop
stop:
	$(DC) down

.PHONY: build
build:
	$(DC) build

.PHONY: logs
logs:
	$(DC) logs -n 1000



