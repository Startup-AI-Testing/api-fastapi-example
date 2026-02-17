import pytest
from unittest.mock import MagicMock
from src.infrastructure.jobs.inventory_jobs import release_expired_reservations_job

def test_release_expired_reservations_job():
    handler_mock = MagicMock()
    
    release_expired_reservations_job(handler_mock)
    
    handler_mock.execute.assert_called_once()
