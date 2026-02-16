class InventoryError(Exception):
    pass

class InsufficientStockError(InventoryError):
    def __init__(self, product_id: int, requested: int, available: int):
        super().__init__(f"Insufficient stock for product {product_id}: requested {requested}, available {available}")

class ReservationNotFoundError(InventoryError):
    def __init__(self, reservation_id):
        super().__init__(f"Reservation {reservation_id} not found")

class InventoryNotFoundError(InventoryError):
    def __init__(self, product_id: int):
        super().__init__(f"Inventory for product {product_id} not found")

class ConcurrentUpdateError(InventoryError):
    def __init__(self, product_id: int):
        super().__init__(f"Concurrent update detected for product {product_id}")
