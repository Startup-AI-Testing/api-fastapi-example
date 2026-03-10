from datetime import datetime, timedelta
import uuid
import pytest
from src.domain.inventory.entities.stock_reservation import StockReservation

def test_stock_reservation_creation():
    reservation = StockReservation.create(
        inventory_id=1,
        quantity=2,
        reservation_type="cart"
    )
    assert isinstance(reservation.id, str)
    assert reservation.inventory_id == 1
    assert reservation.quantity == 2
    assert reservation.status == "active"
    assert reservation.reservation_type == "cart"
    assert isinstance(reservation.reserved_at, datetime)
    assert reservation.expires_at > reservation.reserved_at
    assert reservation.expires_at == reservation.reserved_at + timedelta(minutes=15)

def test_stock_reservation_confirm():
    reservation = StockReservation.create(inventory_id=1, quantity=2)
    order_id = str(uuid.uuid4())
    reservation.confirm(order_id=order_id)
    assert reservation.status == "confirmed"
    assert reservation.order_id == order_id

def test_stock_reservation_release():
    reservation = StockReservation.create(inventory_id=1, quantity=2)
    reservation.release()
    assert reservation.status == "released"

def test_stock_reservation_expire():
    reservation = StockReservation.create(inventory_id=1, quantity=2)
    reservation.expire()
    assert reservation.status == "expired"

def test_stock_reservation_is_expired():
    reservation = StockReservation.create(inventory_id=1, quantity=2)
    assert not reservation.is_expired()
    
    reservation.expires_at = datetime.utcnow() - timedelta(minutes=1)
    assert reservation.is_expired()
