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

## Run Demo from Docker Container (Xpra)

Use the Makefile [`run`](Makefile) target, with optional arguments:
- `UI=pyqt|tkinter` to choose a UI toolkit.
- `XPRA_PORT=<port>` to map a local port to container Xpra TCP port `14500`.
- `XPRA_PASSWORD=<password>` to pass Xpra auth password into the container environment.

Run with default settings:

```bash
make run
```

Run with a specific UI:

```bash
make run UI=pyqt
make run UI=tkinter
```

Then connect from your local Xpra client to:

```text
tcp:localhost:14500
```

Or, if using a custom local port:

```bash
make run UI=pyqt XPRA_PORT=16000 XPRA_PASSWORD='change-me-now'
```

```text
tcp:localhost:16000
```

## Server Deployment: Single Container with Direct Xpra TCP

This repository can be deployed as a single container that:
- runs Xpra with TCP bound on `0.0.0.0:14500`
- requires Xpra authentication for native client access
- starts the PyQt UI app through Xpra

Build image:

```bash
docker build -t acsys-xpra .
```

Run on a server:

```bash
docker run -d \
  --name acsys-xpra \
  --restart unless-stopped \
  -p 14500:14500 \
  -e XPRA_PASSWORD='change-me-now' \
  acsys-xpra
```

Connect from native Xpra client:

```text
tcp:<server-ip>:14500
```

Optional environment overrides:
- `APP_CMD` (default: `python /app/main.py --ui pyqt`)
- `XPRA_BIND_HOST` (default: `0.0.0.0`)
- `XPRA_BIND_PORT` (default: `14500`)
- `XPRA_DISPLAY` (default: `:100`)
- `XPRA_HTML` (default: `on`; only needed if using Xpra HTML directly on port `14500`)
- `XPRA_AUTH` (default: `password`)
- `XPRA_PASSWORD` (recommended secret; writes to `XPRA_PASSWORD_FILE` at startup)
- `XPRA_PASSWORD_FILE` (default: `/xpra/password.txt`; use with mounted secret files)

Security note:
- Authentication is now required by default for native Xpra TCP access.
- Use a strong password and do not expose port `14500` publicly without network controls and TLS in front of Xpra.
