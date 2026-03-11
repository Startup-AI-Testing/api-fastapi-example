import sys
import os
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, engine, Base
from app import models

def seed():
    # Create tables if they don't exist (though we should use alembic)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have products
        if db.query(models.Product).count() > 0:
            print("Database already seeded.")
            return

        # Create products
        products = [
            models.Product(name="Laptop Pro", description="High performance laptop", price=1500.0, stock=10),
            models.Product(name="Wireless Mouse", description="Ergonomic mouse", price=25.0, stock=50),
            models.Product(name="Mechanical Keyboard", description="RGB keyboard", price=100.0, stock=20),
            models.Product(name="Monitor 4K", description="27 inch monitor", price=400.0, stock=5),
        ]
        db.add_all(products)
        db.commit()

        # Create inventory for each product
        for product in products:
            inventory = models.Inventory(
                product_id=product.id,
                quantity_available=product.stock,
                quantity_reserved=0,
                quantity_sold=0,
                reorder_point=5 if product.stock > 10 else 2,
                version=1,
                last_restocked_at=datetime.utcnow()
            )
            db.add(inventory)
            
            # Add a restock movement
            movement = models.StockMovement(
                inventory_id=product.id,
                movement_type="restock",
                quantity=product.stock,
                reference_id="initial_seed",
                created_by="admin"
            )
            db.add(movement)
            
        db.commit()
        print("Database seeded successfully.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed()
