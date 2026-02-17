from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order_items = relationship("OrderItem", back_populates="product")
    inventory = relationship("Inventory", back_populates="product", uselist=False)


class Inventory(Base):
    __tablename__ = "inventory"

    product_id = Column(Integer, ForeignKey("products.id"), primary_key=True)
    quantity_available = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    quantity_sold = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    version = Column(Integer, default=1, nullable=False)
    last_restocked_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="inventory")
    reservations = relationship("StockReservation", back_populates="inventory")
    movements = relationship("StockMovement", back_populates="inventory")


class StockReservation(Base):
    __tablename__ = "stock_reservations"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    inventory_id = Column(Integer, ForeignKey("inventory.product_id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    reserved_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    status = Column(String(20), default="active") # active, confirmed, released, expired
    reservation_type = Column(String(20), default="order") # order, cart

    inventory = relationship("Inventory", back_populates="reservations")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    inventory_id = Column(Integer, ForeignKey("inventory.product_id"), nullable=False)
    movement_type = Column(String(20), nullable=False) # restock, reserve, release, sale, adjustment
    quantity = Column(Integer, nullable=False)
    reference_id = Column(Uuid, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), default="system")

    inventory = relationship("Inventory", back_populates="movements")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)
    total = Column(Float, default=0.0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
