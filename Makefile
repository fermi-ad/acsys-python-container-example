IMAGE_NAME ?= acsys-python-example
SCRIPT ?= demo/main.py

.PHONY: help build build-no-cache run run-script shell clean demo demo-ui ui-pyqt ui-tkinter

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

	@echo "  make ui-pyqt                Run demo script in Docker with PyQt via Xpra (open http://localhost:14500)"
	@echo "  make ui-tkinter             Run demo script in Docker with Tkinter via Xpra (open http://localhost:14500)"

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

ui-pyqt:
	docker run --rm -p 14500:14500 -v .:/app --entrypoint xpra $(IMAGE_NAME) \
		start-desktop :100 \
		--bind-tcp=0.0.0.0:14500 --html=on --daemon=no --exit-with-children \
		--start-child="python /app/demo/main.py --ui pyqt"

ui-tkinter:
	docker run --rm -p 14500:14500 -v .:/app --entrypoint xpra $(IMAGE_NAME) \
		start-desktop :100 \
		--bind-tcp=0.0.0.0:14500 --html=on --daemon=no --exit-with-children \
		--start-child="python /app/demo/main.py --ui tkinter"
