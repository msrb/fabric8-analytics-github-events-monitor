"""Tests for backend module."""

import pytest
from unittest import mock
from ghmonitor.backend import (
    get_backend_by_name, LoggerBackend, SelinonBackend, InvalidBackendClass
)


@mock.patch('ghmonitor.backend.init_celery')
@mock.patch('ghmonitor.backend.init_selinon')
def test_get_backend_by_name(init_celery_mock, init_selinon_mock):
    """Test get_backend_by_name() function."""
    backend = get_backend_by_name('LoggerBackend')
    assert isinstance(backend, LoggerBackend)

    backend = get_backend_by_name('SelinonBackend')
    assert isinstance(backend, SelinonBackend)


def test_get_backend_by_name_invalid():
    """Test get_backend_by_name() with invalid backend class name."""
    with pytest.raises(InvalidBackendClass):
        get_backend_by_name('InvalidBackendName')
