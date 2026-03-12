IMAGE_NAME ?= acsys-python-example
SCRIPT ?= demo/main.py

.PHONY: help build run run-script shell clean demo demo-ui

help:
	@echo "Available targets:"
	@echo "  make build                 Build Docker image ($(IMAGE_NAME))"
	@echo "  make run                   Run container default command"
	@echo "  make run-script SCRIPT=... Run a specific script in container with repo mounted"
	@echo "  make shell                 Open an interactive shell in container"
	@echo "  make demo                  Run demo script in console mode locally"
	@echo "  make demo-ui               Run demo script with UI locally"
	@echo "  make clean                 Remove Docker image ($(IMAGE_NAME))"

build:
	docker build -t $(IMAGE_NAME) .

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
