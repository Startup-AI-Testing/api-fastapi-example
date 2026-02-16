import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Product
from src.infrastructure.persistence.inventory.orm_models import InventoryORM
from datetime import datetime

def seed():
    # Ensure tables are created (though migrations should handle this)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have products
        products = db.query(Product).all()
        if not products:
            print("Creating sample products...")
            p1 = Product(name="Laptop", description="High-end laptop", price=1200.0)
            p2 = Product(name="Mouse", description="Wireless mouse", price=25.0)
            p3 = Product(name="Keyboard", description="Mechanical keyboard", price=75.0)
            db.add_all([p1, p2, p3])
            db.commit()
            products = [p1, p2, p3]
        
        print(f"Found {len(products)} products. Initializing inventory...")
        
        for product in products:
            # Check if inventory exists
            inventory = db.query(InventoryORM).filter(InventoryORM.product_id == product.id).first()
            if not inventory:
                print(f"Creating inventory for product {product.name} (ID: {product.id})")
                inventory = InventoryORM(
                    product_id=product.id,
                    quantity_available=100,
                    quantity_reserved=0,
                    quantity_sold=0,
                    reorder_point=10,
                    version=1,
                    last_restocked_at=datetime.utcnow()
                )
                db.add(inventory)
        
        db.commit()
        print("Seed completed successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
