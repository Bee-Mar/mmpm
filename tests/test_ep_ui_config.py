import json
import pytest
from flask import Flask
from unittest.mock import MagicMock, patch

from mmpm.api.endpoints.ep_ui_config import UiConfig


@pytest.fixture
def client():
    app = Flask(__name__)
    endpoint = UiConfig()
    app.register_blueprint(endpoint.blueprint)
    app.config["TESTING"] = True
    return app.test_client()


def _mock_env(api_base="", socket_url="", base_url=""):
    m = MagicMock()
    m.MMPM_UI_API_BASE_URL.get.return_value = api_base
    m.MMPM_UI_SOCKET_URL.get.return_value = socket_url
    m.MMPM_UI_BASE_URL.get.return_value = base_url
    return m


def test_returns_200(client):
    with patch("mmpm.api.endpoints.ep_ui_config.MMPMEnv", return_value=_mock_env()):
        response = client.get("/api/ui-config")
    assert response.status_code == 200


def test_content_type_is_javascript(client):
    with patch("mmpm.api.endpoints.ep_ui_config.MMPMEnv", return_value=_mock_env()):
        response = client.get("/api/ui-config")
    assert "javascript" in response.content_type


def test_response_assigns_mmpm_config(client):
    with patch("mmpm.api.endpoints.ep_ui_config.MMPMEnv", return_value=_mock_env()):
        response = client.get("/api/ui-config")
    assert response.data.decode().startswith("window.MMPM_CONFIG=")


def test_config_values_from_env(client):
    env = _mock_env(
        api_base="http://host/mmpm",
        socket_url="http://host/mmpm/repeater",
        base_url="http://host/mmpm",
    )
    with patch("mmpm.api.endpoints.ep_ui_config.MMPMEnv", return_value=env):
        response = client.get("/api/ui-config")
    raw = response.data.decode()
    config = json.loads(raw.removeprefix("window.MMPM_CONFIG=").removesuffix(";"))
    assert config["apiBase"] == "http://host/mmpm"
    assert config["socketUrl"] == "http://host/mmpm/repeater"
    assert config["baseUrl"] == "http://host/mmpm"


def test_empty_env_values(client):
    with patch("mmpm.api.endpoints.ep_ui_config.MMPMEnv", return_value=_mock_env()):
        response = client.get("/api/ui-config")
    raw = response.data.decode()
    config = json.loads(raw.removeprefix("window.MMPM_CONFIG=").removesuffix(";"))
    assert config["apiBase"] == ""
    assert config["socketUrl"] == ""
    assert config["baseUrl"] == ""
