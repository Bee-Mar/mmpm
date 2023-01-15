#!/usr/bin/env python3
import os
import pytest
import socket
import shutil
from mmpm import utils, consts, core, colors

HOME_DIR: str = os.path.expanduser('~')

def test_internet_connection():
    try:
        assert socket.create_connection(('www.google.com', 80))  # HTTP
        assert socket.create_connection(('www.google.com', 443))  # HTTPS
        print('Internet connection up')
        return True
    except OSError:
        print('Internet connection down')
        return False


def test_nodejs_installation():
    assert shutil.which('nodejs') or shutil.which('node')


def test_module_file_exists():
    assert os.path.exists(consts.MMPM_LOG_FILE)


def test_module_dir_exists():
    assert os.path.exists(os.path.join(consts.MAGICMIRROR_ROOT, 'modules'))


def test_magic_mirror_installation_found():
    assert os.path.exists(consts.MAGICMIRROR_ROOT)


def test_retrieve_modules():
    assert core.load_modules()


def test_search_modules_with_empty_query():
    assert core.search_modules(core.load_modules(), '')


def test_search_modules_with_valid_query():
    assert core.search_modules(core.load_modules(), 'face')
