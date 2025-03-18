
.DEFAULT_GOAL := run

NUM_NODES ?= 2
OS_ARCH ?= linux/$(shell uname -m)
# Supports rocky95, ubuntu2204
OS_FLAVOR ?= rocky95
REPO ?= http://repo:8000/download

BUILD_OS_ARCH ?= linux/$(shell uname -m)
# Supports rocky95, rocky810
BUILD_OS_FLAVOR ?= rocky95

COMPOSE_ARGS := NUM_NODES=$(NUM_NODES) OS_ARCH=$(OS_ARCH) OS_FLAVOR=$(OS_FLAVOR) BUILD_OS_ARCH=$(BUILD_OS_ARCH) BUILD_OS_FLAVOR=$(BUILD_OS_FLAVOR) REPO=$(REPO)

.PHONY: compose-up
compose-up:
	$(COMPOSE_ARGS) docker compose build && $(COMPOSE_ARGS) docker compose up -d

.PHONY: compose-down
compose-down:
	docker compose down

.PHONY: exec-build
exec-build:
	@docker exec -it pgedge-build-1 bash

define EXEC_NODE
.PHONY: exec-n$(1)
exec-n$(1):
	@docker exec -u pgedge -it pgedge-node-$(1) bash
endef

.PHONY: node-ips
node-ips:
	@docker compose ps -q node | xargs docker inspect -f '{{.Name}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'

$(foreach n,1 2 3 4 5 6 7 8 9 10,$(eval $(call EXEC_NODE,$n)))
