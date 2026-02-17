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
