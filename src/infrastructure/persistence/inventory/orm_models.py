from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UUID, text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class InventoryORM(Base):
    __tablename__ = "inventory"

    product_id = Column(Integer, primary_key=True, index=True)
    quantity_available = Column(Integer, default=0, nullable=False)
    quantity_reserved = Column(Integer, default=0, nullable=False)
    quantity_sold = Column(Integer, default=0, nullable=False)
    reorder_point = Column(Integer, default=0, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    last_restocked_at = Column(DateTime, default=datetime.utcnow)

    __mapper_args__ = {
        "version_id_col": version
    }

class StockReservationORM(Base):
    __tablename__ = "stock_reservations"

    id = Column(String(36), primary_key=True) # UUID as string for SQLite compatibility
    inventory_id = Column(Integer, ForeignKey("inventory.product_id"), nullable=False)
    order_id = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=False)
    reserved_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False) # active, confirmed, released, expired
    reservation_type = Column(String(20), nullable=False) # order, cart

class StockMovementORM(Base):
    __tablename__ = "stock_movements"

    id = Column(String(36), primary_key=True)
    inventory_id = Column(Integer, ForeignKey("inventory.product_id"), nullable=False)
    movement_type = Column(String(20), nullable=False) # restock, reserve, release, sale, adjustment
    quantity = Column(Integer, nullable=False)
    reference_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
