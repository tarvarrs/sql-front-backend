.PHONY: help build up up-v down restart clean logs shell ps migrate migrate-create migrate-down test

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Docker targets
build: ## Build or rebuild services
	docker-compose build

up: ## Start containers (detached mode)
	docker-compose up -d

up-v: ## Start containers with fresh anonymous volumes (ignore cached data)
	docker-compose up -V -d

up-build: ## Build and start containers
	docker-compose up -d --build

down: ## Stop and remove containers
	docker-compose down

down-v: ## Stop and remove containers with volumes (full cleanup)
	docker-compose down -v

restart: down up ## Restart all containers

clean: down-v ## Full cleanup: stop containers and remove volumes
	@echo "Containers and volumes removed"

# Utility targets
logs: ## Show logs from all containers
	docker-compose logs -f

logs-api: ## Show logs from API container only
	docker-compose logs -f backend

ps: ## Show running containers status
	docker-compose ps

# Maintenance
prune: ## Remove all unused containers, networks, and images
	docker system prune -f
