from app.database import SessionLocal
from app.models import Product, Inventory
from datetime import datetime

def seed():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        for product in products:
            inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
            if not inventory:
                inventory = Inventory(
                    product_id=product.id,
                    quantity_available=product.stock,
                    quantity_reserved=0,
                    quantity_sold=0,
                    reorder_point=5,
                    version=1,
                    last_restocked_at=datetime.utcnow()
                )
                db.add(inventory)
        db.commit()
        print(f"Seeded inventory for {len(products)} products")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
