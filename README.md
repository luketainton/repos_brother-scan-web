# Brother Scan Web

A small Flask web application for scanning documents from a Brother printer/scanner on the local network.

The container includes the SANE command-line tools and the generic sane-airscan backend for network scanners. The scanner must be reachable from the container and visible to SANE.

## Run with Docker

For network scanner discovery, use host networking:

```sh
docker build -t brother-scan-web .
docker run --rm --network host brother-scan-web
```

Open <http://localhost:8080>.

Check which scanner names SANE can see:

```sh
docker run --rm --network host --entrypoint scanimage brother-scan-web -L
```

Set SANE_DEVICE to the exact device name reported by scanimage -L. Do not set it to a raw IP address; an IP address is not a complete SANE device name. Leave it empty to let SANE use its default/discovered device.

## Run with Compose

The example Compose file uses host networking so network scanner discovery works on a typical Linux host:

```sh
docker compose up --build
```

Set SANE_DEVICE in the environment if more than one scanner is available.

If the scanner does not appear in scanimage -L, the model may require Brother's proprietary brscan/brscan4 backend and configuration. The backend must be installed in the image; sane-utils alone does not provide every Brother network backend.

## Run locally

```sh
uv sync --dev
uv run flask --app app run --debug
```

The scan endpoint accepts POST /scan with optional form fields format (png or pdf), dpi (75600), and source (flatbed or adf).
