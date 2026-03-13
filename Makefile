IMAGE_NAME ?= acsys-python-example
SCRIPT ?= demo/main.py

XPRA_PORT ?= 14500
XPRA_BASE_FLAGS := --bind-tcp=0.0.0.0:$(XPRA_PORT) --daemon=no --exit-with-children
XPRA_FEATURE_FLAGS := --speaker=off --webcam=no --printing=no --notifications=no --opengl=no

RUN_ARGS :=
ifneq ($(strip $(ui)),)
	RUN_ARGS := --ui $(ui)
endif

XPRA_RUN = docker run --rm -p $(XPRA_PORT):$(XPRA_PORT) -v .:/app --entrypoint xpra $(IMAGE_NAME) \
	start-desktop :100 \
	$(XPRA_BASE_FLAGS) --html=$(HTML) $(XPRA_FEATURE_FLAGS) \
	--start-child="python /app/demo/main.py $(RUN_ARGS)"

CLI_RUN = docker run --rm -v .:/app $(IMAGE_NAME) /app/demo/main.py

.PHONY: help build build-no-cache run shell clean

help:
	@echo "Available targets:"
	@echo "  make build                       Build Docker image ($(IMAGE_NAME))"
	@echo "  make build-no-cache              Build Docker image ($(IMAGE_NAME)) without cache"
	@echo "  make run [ui=...] [html=on|off]  Run demo in Docker (default no UI; else ui=pyqt|tkinter)"
	@echo "  make shell                       Open an interactive shell in container"
	@echo "  make clean                       Remove Docker image ($(IMAGE_NAME))"

build:
	docker build -t $(IMAGE_NAME) .

build-no-cache:
	docker build --no-cache -t $(IMAGE_NAME) .

run:
	@if [ -n "$(ui)" ] && [ "$(ui)" != "pyqt" ] && [ "$(ui)" != "tkinter" ]; then \
		echo "Usage: make run [ui=pyqt|tkinter] [html=on|off]"; \
		exit 1; \
	fi
	@if [ -z "$(ui)" ] && [ -n "$(html)" ]; then \
		echo "Usage: html requires ui (make run ui=pyqt html=on|off)"; \
		exit 1; \
	fi
	@if [ -n "$(html)" ] && [ "$(html)" != "on" ] && [ "$(html)" != "off" ]; then \
		echo "Usage: make run [ui=pyqt|tkinter] [html=on|off]"; \
		exit 1; \
	fi
	$(MAKE) _run HTML=$(if $(html),$(html),off) ui=$(ui)

_run:
	@if [ -n "$(ui)" ]; then \
		$(XPRA_RUN); \
	else \
		$(CLI_RUN); \
	fi

shell:
	docker run --rm -it -v .:/app --entrypoint /bin/sh $(IMAGE_NAME)

clean:
	docker image rm -f $(IMAGE_NAME)
