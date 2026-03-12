IMAGE_NAME ?= acsys-python-example
SCRIPT ?= demo/main.py

XPRA_PORT ?= 14500
XPRA_BASE_FLAGS := --bind-tcp=0.0.0.0:$(XPRA_PORT) --daemon=no --exit-with-children
XPRA_FEATURE_FLAGS := --speaker=off --webcam=no --printing=no --notifications=no --opengl=no

XPRA_RUN = docker run --rm -p $(XPRA_PORT):$(XPRA_PORT) -v .:/app --entrypoint xpra $(IMAGE_NAME) \
	start-desktop :100 \
	$(XPRA_BASE_FLAGS) --html=$(HTML) $(XPRA_FEATURE_FLAGS) \
	--start-child="python /app/demo/main.py --ui $(UI)"

.PHONY: help build build-no-cache run run-script shell clean demo demo-ui run-pyqt run-tkinter run-pyqt-html run-tkinter-html

help:
	@echo "Available targets:"
	@echo "  make build                 Build Docker image ($(IMAGE_NAME))"
	@echo "  make build-no-cache        Build Docker image ($(IMAGE_NAME)) without cache"
	@echo "  make run                   Run container default command"
	@echo "  make run-script SCRIPT=... Run a specific script in container with repo mounted"
	@echo "  make shell                 Open an interactive shell in container"
	@echo "  make demo                  Run demo script in console mode locally"
	@echo "  make demo-ui               Run demo script with UI locally"
	@echo "  make clean                 Remove Docker image ($(IMAGE_NAME))"
	@echo "  make run-pyqt               Run demo script in Docker with PyQt via native Xpra client (connect to tcp:localhost:14500)"
	@echo "  make run-tkinter            Run demo script in Docker with Tkinter via native Xpra client (connect to tcp:localhost:14500)"
	@echo "  make run-pyqt-html          Run demo script in Docker with PyQt via Xpra HTML5 (open http://localhost:14500)"
	@echo "  make run-tkinter-html       Run demo script in Docker with Tkinter via Xpra HTML5 (open http://localhost:14500)"

build:
	docker build -t $(IMAGE_NAME) .

build-no-cache:
	docker build --no-cache -t $(IMAGE_NAME) .

run:
	docker run --rm $(IMAGE_NAME)

run-script:
	docker run --rm -v .:/app $(IMAGE_NAME) $(SCRIPT)

shell:
	docker run --rm -it -v .:/app --entrypoint /bin/sh $(IMAGE_NAME)

demo:
	python demo/main.py

demo-ui:
	python demo/main.py --ui

clean:
	docker image rm -f $(IMAGE_NAME)

run-pyqt:
	$(MAKE) run-ui UI=pyqt HTML=off

run-tkinter:
	$(MAKE) run-ui UI=tkinter HTML=off

run-pyqt-html:
	$(MAKE) run-ui UI=pyqt HTML=on

run-tkinter-html:
	$(MAKE) run-ui UI=tkinter HTML=on

run-ui:
	$(XPRA_RUN)
