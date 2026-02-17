from app.database import SessionLocal
from app.models import Product, Inventory
from datetime import datetime

def seed_inventory():
    db = SessionLocal()
    try:
        # Check if we have products
        products = db.query(Product).all()
        if not products:
            print("No products found. Creating some...")
            p1 = Product(name="Laptop", description="High-end laptop", price=1500.0)
            p2 = Product(name="Mouse", description="Wireless mouse", price=25.0)
            p3 = Product(name="Keyboard", description="Mechanical keyboard", price=100.0)
            db.add_all([p1, p2, p3])
            db.commit()
            products = [p1, p2, p3]

        for product in products:
            # Check if inventory exists
            inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
            if not inventory:
                print(f"Creating inventory for product {product.name}...")
                inventory = Inventory(
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
        print(f"Error seeding inventory: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_inventory()
