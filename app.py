"""Web interface for a SANE-compatible Brother scanner."""

from __future__ import annotations

import os
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

import img2pdf
from flask import Flask, Response, jsonify, render_template, request, send_file

app = Flask(__name__)

ALLOWED_FORMATS = {"png", "pdf"}
ALLOWED_SOURCES = {"flatbed", "adf"}
DEFAULT_DPI = 300
MAX_DPI = 600
MIN_DPI = 75


def _log_scan_event(event: str, **fields: object) -> None:
    values = {"event": event, **fields}
    rendered_values = []
    for key, value in values.items():
        rendered_value = str(value).replace(chr(92), chr(92) + chr(92))
        rendered_value = rendered_value.replace(chr(34), chr(92) + chr(34))
        rendered_values.append(f'{key}="{rendered_value}"')
    app.logger.info(" ".join(rendered_values))


def _scan(image_format: str, dpi: int, source: str, job_id: str) -> Path:
    """Run scanimage and return a temporary output file."""
    started_at = time.monotonic()
    _log_scan_event("scan_started", job_id=job_id, format=image_format, dpi=dpi, source=source)
    status = "failed"
    suffix = ".png" if image_format == "png" else ".pdf"
    output = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    output.close()
    png_path = Path(output.name) if image_format == "png" else Path(output.name).with_suffix(".png")

    command = ["scanimage", "--format=png", f"--resolution={dpi}"]
    if source == "adf":
        command.append("--source=ADF")
    device = os.getenv("SANE_DEVICE")
    if device:
        command.extend(["--device-name", device])
    timeout = int(os.getenv("SCAN_TIMEOUT", "120"))

    try:
        with png_path.open("wb") as image_file:
            subprocess.run(
                command, stdout=image_file, stderr=subprocess.PIPE, check=True, timeout=timeout
            )
        if image_format == "pdf":
            Path(output.name).write_bytes(img2pdf.convert(str(png_path)))
            png_path.unlink(missing_ok=True)
        status = "completed"
        return Path(output.name)
    except Exception:
        Path(output.name).unlink(missing_ok=True)
        png_path.unlink(missing_ok=True)
        raise
    finally:
        _log_scan_event(
            "scan_ended",
            job_id=job_id,
            status=status,
            duration_seconds=f"{time.monotonic() - started_at:.3f}",
        )


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.post("/scan")
def scan() -> Response:
    image_format = request.form.get("format", "pdf").lower()
    source = request.form.get("source", "flatbed").lower()
    try:
        dpi = int(request.form.get("dpi", DEFAULT_DPI))
    except ValueError:
        return jsonify(error="dpi must be an integer"), 400
    if image_format not in ALLOWED_FORMATS:
        return jsonify(error="format must be png or pdf"), 400
    if source not in ALLOWED_SOURCES:
        return jsonify(error="source must be flatbed or adf"), 400
    if not MIN_DPI <= dpi <= MAX_DPI:
        return jsonify(error=f"dpi must be between {MIN_DPI} and {MAX_DPI}"), 400

    job_id = uuid.uuid4().hex[:12]
    _log_scan_event(
        "scan_submitted",
        job_id=job_id,
        format=image_format,
        dpi=dpi,
        source=source,
    )

    try:
        output = _scan(image_format, dpi, source, job_id)
    except subprocess.TimeoutExpired:
        return jsonify(error="scanner timed out"), 504
    except subprocess.CalledProcessError as error:
        detail = error.stderr.decode(errors="replace").strip() or "scanner command failed"
        return jsonify(error=detail), 502
    except (OSError, ValueError) as error:
        return jsonify(error=str(error)), 502

    response = send_file(output, as_attachment=True, download_name=f"scan.{image_format}")
    response.call_on_close(lambda: output.unlink(missing_ok=True))
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
