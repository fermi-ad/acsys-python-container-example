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
python demo/main.py --ui pyqt
```

Run with a simple Tkinter window:

```bash
python demo/main.py --ui tkinter
```

## Run UIs from Docker Container (Xpra)

Use the Makefile targets that start `xpra` inside the container.

### Native Xpra client mode (default)

Run PyQt UI in Docker with HTML disabled:

```bash
make run-pyqt
```

Run Tkinter UI in Docker with HTML disabled:

```bash
make run-tkinter
```

Then connect from your local Xpra client to:

```text
tcp:localhost:14500
```

### HTML5 client mode (browser)

Run PyQt UI in Docker:

```bash
make run-pyqt-html
```

Run Tkinter UI in Docker:

```bash
make run-tkinter-html
```

Then open:

```text
http://localhost:14500
```
