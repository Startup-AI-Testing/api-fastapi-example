import pytest
from datetime import datetime, timedelta
import uuid
from src.domain.inventory.entities.stock_reservation import StockReservation

def test_stock_reservation_creation():
    inventory_id = 1
    quantity = 5
    reservation = StockReservation.create(
        inventory_id=inventory_id,
        quantity=quantity,
        reservation_type="cart"
    )
    assert isinstance(reservation.id, uuid.UUID)
    assert reservation.inventory_id == inventory_id
    assert reservation.quantity == quantity
    assert reservation.reservation_type == "cart"
    assert reservation.status == "active"
    assert isinstance(reservation.reserved_at, datetime)
    assert isinstance(reservation.expires_at, datetime)
    assert reservation.expires_at > reservation.reserved_at
    assert reservation.expires_at == reservation.reserved_at + timedelta(minutes=15)

def test_stock_reservation_confirm():
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    order_id = 101
    reservation.confirm(order_id)
    assert reservation.status == "confirmed"
    assert reservation.order_id == order_id

def test_stock_reservation_release():
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    reservation.release()
    assert reservation.status == "released"

def test_stock_reservation_expire():
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    reservation.expire()
    assert reservation.status == "expired"

def test_stock_reservation_is_expired():
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    # Manually set expires_at to the past
    reservation.expires_at = datetime.utcnow() - timedelta(minutes=1)
    assert reservation.is_expired() is True

def test_stock_reservation_is_not_expired():
    reservation = StockReservation.create(inventory_id=1, quantity=5)
    assert reservation.is_expired() is False
