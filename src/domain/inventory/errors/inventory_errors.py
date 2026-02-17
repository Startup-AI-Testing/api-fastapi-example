class InventoryError(Exception):
    """Base class for inventory errors"""
    pass

class InsufficientStockError(InventoryError):
    """Raised when there is not enough stock available"""
    pass

class ConcurrencyError(InventoryError):
    """Raised when a concurrency conflict is detected"""
    pass

class ReservationError(InventoryError):
    """Raised when there is an error with a reservation"""
    pass

class InventoryNotFoundError(InventoryError):
    """Raised when inventory for a product is not found"""
    pass

class ReservationNotFoundError(ReservationError):
    """Raised when a reservation is not found"""
    pass

class ReservationExpiredError(ReservationError):
    """Raised when a reservation has expired"""
    pass
