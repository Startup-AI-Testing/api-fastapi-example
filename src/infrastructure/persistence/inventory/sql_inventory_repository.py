from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from src.domain.inventory.ports.i_inventory_repository import IInventoryRepository
from src.domain.inventory.entities.inventory import Inventory
from src.infrastructure.persistence.inventory.orm_models import InventoryORM
from src.infrastructure.persistence.inventory.mappers import InventoryMapper

class SqlInventoryRepository(IInventoryRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, inventory_id: int) -> Optional[Inventory]:
        orm = self.session.query(InventoryORM).get(inventory_id)
        if not orm:
            return None
        return InventoryMapper.to_domain(orm)

    def get_by_product_id(self, product_id: int) -> Optional[Inventory]:
        orm = self.session.query(InventoryORM).filter(InventoryORM.product_id == product_id).first()
        if not orm:
            return None
        return InventoryMapper.to_domain(orm)

    def save(self, inventory: Inventory) -> None:
        orm = self.session.query(InventoryORM).filter_by(product_id=inventory.product_id).first()
        if orm:
            # Use a filter to ensure we only update if the version matches
            # This is more robust for optimistic locking with domain objects
            updated = self.session.query(InventoryORM).filter(
                InventoryORM.product_id == inventory.product_id,
                InventoryORM.version == inventory.version
            ).update({
                "quantity_available": inventory.quantity_available,
                "quantity_reserved": inventory.quantity_reserved,
                "quantity_sold": inventory.quantity_sold,
                "reorder_point": inventory.reorder_point,
                "last_restocked_at": inventory.last_restocked_at,
                "version": InventoryORM.version + 1
            }, synchronize_session='fetch')
            
            if not updated:
                raise Exception("Concurrency conflict: Inventory was modified by another process")
            
            # Update the domain object version
            inventory.version += 1
        else:
            orm = InventoryMapper.to_orm(inventory)
            self.session.add(orm)
            self.session.flush()
            inventory.version = orm.version

    def list_low_stock(self) -> List[Inventory]:
        orms = self.session.query(InventoryORM).filter(InventoryORM.quantity_available < InventoryORM.reorder_point).all()
        return [InventoryMapper.to_domain(orm) for orm in orms]
