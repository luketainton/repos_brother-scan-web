# Brother Scan Web

A small Flask web application for scanning documents from a Brother printer/scanner on the local network.

The container uses the Linux SANE command-line tools. The Brother device must be reachable from the container and available to SANE (for example, through a configured `net` backend).

## Run with Docker

```sh
docker build -t brother-scan-web .
docker run --rm -p 8080:8080 --network host brother-scan-web
```

Open <http://localhost:8080>. Set `SANE_DEVICE` if more than one scanner is available. Use `SCAN_TIMEOUT` to change the scan timeout in seconds.

## Run with Compose

```sh
docker compose up --build
```

Set `SANE_DEVICE` in the environment when the scanner is not the default SANE device.

## Run locally

```sh
uv sync --dev
uv run flask --app app run --debug
```

The scan endpoint accepts `POST /scan` with optional form fields `format` (`png` or `pdf`), `dpi` (75–600), and `source` (`flatbed` or `adf`).

## Important deployment note

SANE device discovery and network backend configuration are environment-specific. For a Brother network scanner, install/configure the matching SANE backend in the image or mount a site-specific `dll.conf`/`net.conf` configuration as appropriate for the model.
