import pytest
from flask import Flask
from unittest.mock import MagicMock, mock_open, patch

from mmpm.api.endpoints.ep_ui import Ui

FAKE_INDEX = '<html><head><base href="/" /></head><body><app-root></app-root></body></html>'


@pytest.fixture
def client():
    app = Flask(__name__)
    endpoint = Ui()
    app.register_blueprint(endpoint.blueprint)
    app.config["TESTING"] = True
    return app.test_client()


def _mock_env(base_url=""):
    m = MagicMock()
    m.MMPM_UI_BASE_URL.get.return_value = base_url
    return m


def test_serves_html_content_type(client):
    with patch("mmpm.api.endpoints.ep_ui.MMPMEnv", return_value=_mock_env()), \
         patch("builtins.open", mock_open(read_data=FAKE_INDEX)):
        response = client.get("/")
    assert "text/html" in response.content_type


def test_base_href_replaced_when_base_url_set(client):
    with patch("mmpm.api.endpoints.ep_ui.MMPMEnv", return_value=_mock_env("http://host/mmpm")), \
         patch("builtins.open", mock_open(read_data=FAKE_INDEX)):
        response = client.get("/")
    assert b'<base href="/mmpm/">' in response.data


def test_base_href_unchanged_when_base_url_empty(client):
    with patch("mmpm.api.endpoints.ep_ui.MMPMEnv", return_value=_mock_env()), \
         patch("builtins.open", mock_open(read_data=FAKE_INDEX)):
        response = client.get("/")
    assert b'<base href="/" />' in response.data


def test_mmpm_config_not_injected(client):
    with patch("mmpm.api.endpoints.ep_ui.MMPMEnv", return_value=_mock_env()), \
         patch("builtins.open", mock_open(read_data=FAKE_INDEX)):
        response = client.get("/")
    assert b"MMPM_CONFIG" not in response.data


def test_base_href_extracted_from_full_url(client):
    with patch("mmpm.api.endpoints.ep_ui.MMPMEnv", return_value=_mock_env("http://192.168.1.100/mmpm")), \
         patch("builtins.open", mock_open(read_data=FAKE_INDEX)):
        response = client.get("/")
    assert b'<base href="/mmpm/">' in response.data


def test_trailing_slash_normalised(client):
    with patch("mmpm.api.endpoints.ep_ui.MMPMEnv", return_value=_mock_env("http://host/mmpm/")), \
         patch("builtins.open", mock_open(read_data=FAKE_INDEX)):
        response = client.get("/")
    assert b'<base href="/mmpm/">' in response.data
