#!/usr/bin/env python3
import pytest
import socket


@pytest.fixture
def internet_connection():
    try:
        socket.create_connection(('www.google.com', 80))  # HTTP
        socket.create_connection(('www.google.com', 443))  # HTTPS
        return True
    except OSError:
        return False


@pytest.fixture
def nodejs_installation():
    pass


def module_file_exists():
    pass


@pytest.fixture
def module_dir_exists():
    pass


def magic_mirror_installation_found():
    pass
