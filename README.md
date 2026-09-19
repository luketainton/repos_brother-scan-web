# Brother Scan Web

A small Flask web application for scanning documents from a Brother printer/scanner on the local network.

The container includes SANE, the generic sane-airscan backend, and Brother's brscan4 backend for the DCP-J785DW on amd64 images. The scanner must be reachable from the container and visible to SANE.

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

For the DCP-J785DW, the expected Brother SANE device is usually:

```text
brother4:net1;dev0
```

The Compose example uses that device by default. Override SANE_DEVICE if the device name differs or if you have more than one scanner. Do not set SANE_DEVICE to a raw IP address; an IP address is not a complete SANE device name.

The proprietary Brother brscan4 package is amd64-only, so the DCP-J785DW backend is included in amd64 images. arm64 images retain sane-airscan for scanners supporting eSCL/WSD.

## Run with Compose

The example Compose file uses host networking so network scanner discovery works on a typical Linux host:

```sh
docker compose up --build
```

## Run locally

```sh
uv sync --dev
uv run flask --app app run --debug
```

The scan endpoint accepts POST /scan with optional form fields format (png or pdf), dpi (75600), and source (flatbed or adf).
