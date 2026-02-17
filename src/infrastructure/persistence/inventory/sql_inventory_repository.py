from typing import Optional
from sqlalchemy.orm import Session
from app.models import Inventory as InventoryModel
from src.domain.inventory.entities.inventory import Inventory
from src.domain.inventory.ports.i_inventory_repository import IInventoryRepository

from src.domain.inventory.errors.inventory_errors import ConcurrencyError

class SqlInventoryRepository(IInventoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_product_id(self, product_id: int) -> Optional[Inventory]:
        db_inventory = self.session.query(InventoryModel).filter_by(product_id=product_id).first()
        if not db_inventory:
            return None
        
        return Inventory(
            product_id=db_inventory.product_id,
            quantity_available=db_inventory.quantity_available,
            quantity_reserved=db_inventory.quantity_reserved,
            quantity_sold=db_inventory.quantity_sold,
            reorder_point=db_inventory.reorder_point,
            version=db_inventory.version,
            last_restocked_at=db_inventory.last_restocked_at
        )

    def save(self, inventory: Inventory) -> None:
        db_inventory = self.session.query(InventoryModel).filter_by(product_id=inventory.product_id).first()
        
        if not db_inventory:
            db_inventory = InventoryModel(
                product_id=inventory.product_id,
                quantity_available=inventory.quantity_available,
                quantity_reserved=inventory.quantity_reserved,
                quantity_sold=inventory.quantity_sold,
                reorder_point=inventory.reorder_point,
                version=inventory.version,
                last_restocked_at=inventory.last_restocked_at
            )
            self.session.add(db_inventory)
        else:
            # Optimistic locking check
            if db_inventory.version != inventory.version:
                raise ConcurrencyError(f"Inventory version mismatch (DB: {db_inventory.version}, Domain: {inventory.version})")
            
            db_inventory.quantity_available = inventory.quantity_available
            db_inventory.quantity_reserved = inventory.quantity_reserved
            db_inventory.quantity_sold = inventory.quantity_sold
            db_inventory.reorder_point = inventory.reorder_point
            db_inventory.version += 1
            db_inventory.last_restocked_at = inventory.last_restocked_at
            
            # Update domain object version
            inventory.version = db_inventory.version
            
        self.session.commit()

    def get_low_stock(self) -> list[Inventory]:
        db_inventories = self.session.query(InventoryModel).filter(
            InventoryModel.quantity_available < InventoryModel.reorder_point
        ).all()
        
        return [
            Inventory(
                product_id=db.product_id,
                quantity_available=db.quantity_available,
                quantity_reserved=db.quantity_reserved,
                quantity_sold=db.quantity_sold,
                reorder_point=db.reorder_point,
                version=db.version,
                last_restocked_at=db.last_restocked_at
            )
            for db in db_inventories
        ]
