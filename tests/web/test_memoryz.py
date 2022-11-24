"""Tests memoryz page can be accessed."""


def test_memoryz(client):
    assert client.get('/memoryz').status_code == 200
