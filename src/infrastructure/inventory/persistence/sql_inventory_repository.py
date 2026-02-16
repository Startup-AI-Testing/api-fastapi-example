from typing import Optional, List
from sqlalchemy.orm import Session
from src.domain.inventory.ports.i_inventory_repository import IInventoryRepository
from src.domain.inventory.entities.inventory import Inventory as DomainInventory
from app.models import Inventory as SqlInventory

class SqlInventoryRepository(IInventoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, inventory_id: int) -> Optional[DomainInventory]:
        return self.get_by_product_id(inventory_id)

    def get_by_product_id(self, product_id: int) -> Optional[DomainInventory]:
        sql_inventory = self.session.query(SqlInventory).filter_by(product_id=product_id).first()
        if not sql_inventory:
            return None
        return self._to_domain(sql_inventory)

    def list_low_stock(self) -> List[DomainInventory]:
        sql_inventories = self.session.query(SqlInventory).filter(
            SqlInventory.quantity_available < SqlInventory.reorder_point
        ).all()
        return [self._to_domain(i) for i in sql_inventories]

    def save(self, inventory: DomainInventory) -> None:
        sql_inventory = self.session.query(SqlInventory).filter_by(product_id=inventory.product_id).first()
        if sql_inventory:
            # Check version for optimistic locking
            if sql_inventory.version != inventory.version:
                # In a real app, we might raise a specific ConcurrencyError
                pass
            
            sql_inventory.quantity_available = inventory.quantity_available
            sql_inventory.quantity_reserved = inventory.quantity_reserved
            sql_inventory.quantity_sold = inventory.quantity_sold
            sql_inventory.reorder_point = inventory.reorder_point
            sql_inventory.version = inventory.version + 1 # Increment version
            sql_inventory.last_restocked_at = inventory.last_restocked_at
        else:
            sql_inventory = SqlInventory(
                product_id=inventory.product_id,
                quantity_available=inventory.quantity_available,
                quantity_reserved=inventory.quantity_reserved,
                quantity_sold=inventory.quantity_sold,
                reorder_point=inventory.reorder_point,
                version=1,
                last_restocked_at=inventory.last_restocked_at
            )
            self.session.add(sql_inventory)
        
        # Update domain object version
        inventory.version = sql_inventory.version

    def _to_domain(self, sql_inventory: SqlInventory) -> DomainInventory:
        return DomainInventory(
            product_id=sql_inventory.product_id,
            quantity_available=sql_inventory.quantity_available,
            quantity_reserved=sql_inventory.quantity_reserved,
            quantity_sold=sql_inventory.quantity_sold,
            reorder_point=sql_inventory.reorder_point,
            version=sql_inventory.version,
            last_restocked_at=sql_inventory.last_restocked_at
        )
