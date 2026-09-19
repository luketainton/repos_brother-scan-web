from unittest.mock import patch

from app import app


def test_index():
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert b"Brother Scan" in response.data


def test_scan_rejects_invalid_dpi():
    response = app.test_client().post("/scan", data={"dpi": "bad"})
    assert response.status_code == 400
    assert response.json["error"] == "dpi must be an integer"


def test_scan_rejects_invalid_format():
    response = app.test_client().post("/scan", data={"format": "jpeg"})
    assert response.status_code == 400


@patch("app._scan")
def test_scan_returns_file(mock_scan, tmp_path):
    output = tmp_path / "scan.png"
    output.write_bytes(b"png")
    mock_scan.return_value = output
    response = app.test_client().post("/scan", data={"format": "png", "dpi": "300"})
    assert response.status_code == 200
    assert response.data == b"png"
