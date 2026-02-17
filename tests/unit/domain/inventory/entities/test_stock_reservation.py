from datetime import datetime, timedelta
import uuid
import pytest
from src.domain.inventory.entities.stock_reservation import StockReservation

def test_stock_reservation_creation():
    reservation_id = uuid.uuid4()
    reservation = StockReservation.create(
        id=reservation_id,
        inventory_id=1,
        quantity=5,
        reservation_type="cart"
    )
    assert reservation.id == reservation_id
    assert reservation.inventory_id == 1
    assert reservation.quantity == 5
    assert reservation.status == "active"
    assert reservation.reservation_type == "cart"
    assert reservation.expires_at > reservation.reserved_at
    assert reservation.expires_at == reservation.reserved_at + timedelta(minutes=15)

def test_stock_reservation_is_expired():
    reservation = StockReservation.create(
        id=uuid.uuid4(),
        inventory_id=1,
        quantity=5
    )
    # Manually set expires_at to the past
    reservation.expires_at = datetime.utcnow() - timedelta(minutes=1)
    assert reservation.is_expired() is True

def test_stock_reservation_confirm():
    reservation = StockReservation.create(
        id=uuid.uuid4(),
        inventory_id=1,
        quantity=5
    )
    order_id = 100
    reservation.confirm(order_id)
    assert reservation.status == "confirmed"
    assert reservation.order_id == order_id

def test_stock_reservation_release():
    reservation = StockReservation.create(
        id=uuid.uuid4(),
        inventory_id=1,
        quantity=5
    )
    reservation.release()
    assert reservation.status == "released"
