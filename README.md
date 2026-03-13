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
- `ui=pyqt|tkinter` to choose a UI toolkit.
- `html=on|off` to enable/disable Xpra HTML5 mode (`off` by default).

Run with default settings (no UI, HTML off):

```bash
make run
```

Run with a UI (native Xpra client mode, HTML off):

```bash
make run ui=pyqt
make run ui=tkinter
```

Then connect from your local Xpra client to:

```text
tcp:localhost:14500
```

Run with HTML5 mode enabled (browser):

```bash
make run ui=pyqt html=on
make run ui=tkinter html=on
```

Then open:

```text
http://localhost:14500
```

## Server Deployment: Single Container with Nginx Reverse Proxy

This repository can be deployed as a single container that:
- runs Xpra in HTML mode bound on internal `127.0.0.1:14500`
- starts the PyQt UI app through Xpra
- exposes Nginx on external port `80` at path `/`, proxying traffic to Xpra

Build image:

```bash
docker build -t acsys-xpra-nginx .
```

Run on a server:

```bash
docker run -d \
  --name acsys-xpra \
  --restart unless-stopped \
  -p 80:80 \
  acsys-xpra-nginx
```

Open in browser:

```text
http://<server-ip>/
```

Optional environment overrides:
- `APP_CMD` (default: `python /app/main.py --ui pyqt`)
- `XPRA_BIND_HOST` (default: `127.0.0.1`)
- `XPRA_BIND_PORT` (default: `14500`)
- `XPRA_DISPLAY` (default: `:100`)

Security note:
- This setup is suitable for internal or trusted networks.
- For internet-facing use, add TLS termination and Xpra authentication before public exposure.
