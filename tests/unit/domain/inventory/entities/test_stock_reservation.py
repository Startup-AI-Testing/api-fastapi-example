import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from src.domain.inventory.entities.stock_reservation import StockReservation

def test_create_stock_reservation():
    inventory_id = 1
    quantity = 5
    reservation = StockReservation.create(
        inventory_id=inventory_id,
        quantity=quantity,
        reservation_type="cart"
    )
    
    assert reservation.inventory_id == inventory_id
    assert reservation.quantity == quantity
    assert reservation.reservation_type == "cart"
    assert reservation.status == "active"
    assert isinstance(reservation.reserved_at, datetime)
    assert isinstance(reservation.expires_at, datetime)
    assert reservation.expires_at > reservation.reserved_at
    assert reservation.order_id is None

def test_confirm_reservation():
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    order_id = 101
    reservation.confirm(order_id)
    
    assert reservation.status == "confirmed"
    assert reservation.order_id == order_id

def test_release_reservation():
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    reservation.release()
    
    assert reservation.status == "released"

def test_is_expired():
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    assert reservation.is_expired() is False
    
    # Mock expiration
    reservation.expires_at = datetime.utcnow() - timedelta(minutes=1)
    assert reservation.is_expired() is True
