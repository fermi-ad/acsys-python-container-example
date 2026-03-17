IMAGE_NAME ?= acsys-python-example
SCRIPT ?= main.py

XPRA_PORT ?= 14500
HTTP_PORT ?= 80
CONTAINER_NAME ?= acsys-xpra
UI ?= pyqt

DEPLOY_RUN = docker run --rm \
	--name $(CONTAINER_NAME) \
	-p $(HTTP_PORT):80 \
	$(if $(APP_CMD),-e APP_CMD="$(APP_CMD)") \
	$(if $(XPRA_BIND_HOST),-e XPRA_BIND_HOST="$(XPRA_BIND_HOST)") \
	$(if $(XPRA_BIND_PORT),-e XPRA_BIND_PORT="$(XPRA_BIND_PORT)") \
	$(if $(XPRA_DISPLAY),-e XPRA_DISPLAY="$(XPRA_DISPLAY)") \
	$(IMAGE_NAME)

.PHONY: help build build-no-cache run stop shell clean

help:
	@echo "Available targets:"
	@echo "  make build                                  Build Docker image ($(IMAGE_NAME))"
	@echo "  make build-no-cache                         Build Docker image ($(IMAGE_NAME)) without cache"
	@echo "  make run [UI=pyqt|tkinter] [HTTP_PORT=80]   Run deployment container (Nginx -> Xpra HTML)"
	@echo "  make stop [CONTAINER_NAME=acsys-xpra]       Stop deployed container"
	@echo "  make shell                                  Open an interactive shell in container"
	@echo "  make clean                                  Remove Docker image ($(IMAGE_NAME))"

build:
	docker build -t $(IMAGE_NAME) .

build-no-cache:
	docker build --no-cache -t $(IMAGE_NAME) .

run:
	@if [ "$(UI)" != "pyqt" ] && [ "$(UI)" != "tkinter" ]; then \
		echo "Usage: make run [UI=pyqt|tkinter] [HTTP_PORT=80]"; \
		exit 1; \
	fi
	$(MAKE) _run APP_CMD="python /app/$(SCRIPT) --ui $(UI)"

_run:
	$(DEPLOY_RUN)
	@echo "Run started (attached): http://localhost:$(HTTP_PORT)/"

stop:
	-docker stop $(CONTAINER_NAME)

shell:
	docker run --rm -it -v .:/app --entrypoint /bin/sh $(IMAGE_NAME)

clean:
	docker image rm -f $(IMAGE_NAME)
