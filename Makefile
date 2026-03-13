IMAGE_NAME ?= acsys-python-example
SCRIPT ?= demo/main.py

XPRA_PORT ?= 14500
HTTP_PORT ?= 80
CONTAINER_NAME ?= acsys-xpra
UI ?= pyqt

RUN_ARGS :=
ifneq ($(strip $(ui)),)
	RUN_ARGS := --ui $(ui)
endif

CLI_RUN = docker run --rm -v .:/app $(IMAGE_NAME) /app/demo/main.py

DEPLOY_RUN = docker run -d --rm \
	--name $(CONTAINER_NAME) \
	--restart unless-stopped \
	-p $(HTTP_PORT):80 \
	$(if $(APP_CMD),-e APP_CMD="$(APP_CMD)") \
	$(if $(XPRA_BIND_HOST),-e XPRA_BIND_HOST="$(XPRA_BIND_HOST)") \
	$(if $(XPRA_BIND_PORT),-e XPRA_BIND_PORT="$(XPRA_BIND_PORT)") \
	$(if $(XPRA_DISPLAY),-e XPRA_DISPLAY="$(XPRA_DISPLAY)") \
	$(IMAGE_NAME)

.PHONY: help build build-no-cache run deploy stop shell clean

help:
	@echo "Available targets:"
	@echo "  make build                                  Build Docker image ($(IMAGE_NAME))"
	@echo "  make build-no-cache                         Build Docker image ($(IMAGE_NAME)) without cache"
	@echo "  make run [ui=pyqt|tkinter]                  Run demo directly in container for local testing"
	@echo "  make deploy [ui=pyqt|tkinter] [HTTP_PORT=80] Start server deployment (Nginx -> Xpra HTML)"
	@echo "  make stop [CONTAINER_NAME=acsys-xpra]       Stop deployed container"
	@echo "  make shell                                  Open an interactive shell in container"
	@echo "  make clean                                  Remove Docker image ($(IMAGE_NAME))"

build:
	docker build -t $(IMAGE_NAME) .

build-no-cache:
	docker build --no-cache -t $(IMAGE_NAME) .

run:
	@if [ -n "$(ui)" ] && [ "$(ui)" != "pyqt" ] && [ "$(ui)" != "tkinter" ]; then \
		echo "Usage: make run [ui=pyqt|tkinter]"; \
		exit 1; \
	fi
	@if [ -n "$(ui)" ]; then \
		docker run --rm -v .:/app $(IMAGE_NAME) /app/demo/main.py --ui $(ui); \
	else \
		$(CLI_RUN); \
	fi

deploy:
	@if [ -n "$(ui)" ] && [ "$(ui)" != "pyqt" ] && [ "$(ui)" != "tkinter" ]; then \
		echo "Usage: make deploy [ui=pyqt|tkinter] [HTTP_PORT=80]"; \
		exit 1; \
	fi
	$(MAKE) _deploy APP_CMD="python /app/main.py --ui $(if $(ui),$(ui),$(UI))"

_deploy:
	$(DEPLOY_RUN)
	@echo "Deployment started: http://localhost:$(HTTP_PORT)/"

stop:
	-docker stop $(CONTAINER_NAME)

shell:
	docker run --rm -it -v .:/app --entrypoint /bin/sh $(IMAGE_NAME)

clean:
	docker image rm -f $(IMAGE_NAME)
