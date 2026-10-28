"""These probes do not use the OCR predictor or torch."""
import pytest
import socket
import urllib.request


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError('probe attempted live network')
    monkeypatch.setattr(socket.socket, 'connect', blocked)
    monkeypatch.setattr(socket.socket, 'connect_ex', blocked)
    monkeypatch.setattr(urllib.request, 'urlopen', blocked)


@pytest.fixture(scope='session', autouse=True)
def predictor_path():
    yield


@pytest.fixture(scope='session', autouse=True)
def cpu_threads():
    yield
