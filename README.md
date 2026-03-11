# ACSys-Python Container Example

This project builds a container with acsys-python dependencies and a small script to demonstrate its functionality.

## Development Container

This project also includes a VSCode `.devcontainer`` that allows acsys-python developers and users to quickly and easily develop scripts.

<https://code.visualstudio.com/docs/devcontainers/tutorial>

## Docker Deployment

The `.devcontainer` is not meant for production, so we build a `Dockerfile` as well. This file is somewhat optimized for deployment without development tools installed.

## Build & Run

- To build: 
```bash
    cd root-of-this-repo/
    docker build -t <image-name> .
```

- To run 
```bash
    docker run --rm <image-name>
```
- To run your script directly without rebuilding the image:

```bash
    docker run --rm -v .:/app <image-name> <your-script>
```

## Demo Script Usage

Run in console mode (default):

```bash
python demo/main.py
```

Run with a simple PyQt window:

```bash
python demo/main.py --ui
```
