# Inventory Reservation System

## Overview
The Inventory Reservation System manages product stock with support for temporary reservations, preventing overselling through optimistic locking and transactional integrity.

## Architecture
The system follows Domain-Driven Design (DDD) and Hexagonal Architecture principles:

- **Domain Layer**: Pure business logic, entities (`Inventory`, `StockReservation`, `StockMovement`), and domain services.
- **Application Layer**: Use case handlers that coordinate domain objects and infrastructure.
- **Infrastructure Layer**: Persistence implementations (SQLAlchemy repositories) and external adapters.
- **Interface Layer**: HTTP endpoints (FastAPI routers).

## Key Features
- **Optimistic Locking**: Uses a `version` field to prevent race conditions during concurrent stock updates.
- **Temporary Reservations**: Stock can be reserved for 15 minutes (configurable).
- **Audit Log**: Every stock change is recorded in `stock_movements`.
- **Background Jobs**: Automatic release of expired reservations and low stock detection.

## API Endpoints

### Inventory Management
- `GET /inventory/product/{id}`: Get current availability.
- `POST /inventory/restock`: Add stock to a product.
- `POST /inventory/adjust`: Manually adjust stock levels.
- `GET /inventory/movements`: View stock movement history.
- `GET /inventory/low-stock`: List products below reorder point.

### Reservations
- `POST /inventory/reserve`: Create a temporary reservation.
- `POST /inventory/reserve/{id}/confirm`: Confirm a reservation (usually during order creation).
- `DELETE /inventory/reserve/{id}`: Manually release a reservation.

## Flow Diagrams

### Stock Reservation Flow
1. User adds item to cart.
2. `POST /inventory/reserve` is called.
3. System checks `quantity_available`.
4. If available, `quantity_available` decreases, `quantity_reserved` increases.
5. `StockReservation` record created with expiration time.
6. `StockMovement` (type: `reserve`) recorded.

### Order Confirmation Flow
1. User completes checkout.
2. `POST /orders` is called with `reservation_id`.
3. `ConfirmReservationHandler` is executed.
4. `StockReservation` status becomes `confirmed`.
5. `Inventory` updates: `quantity_reserved` decreases, `quantity_sold` increases.
6. `StockMovement` (type: `sale`) recorded.

## Concurrency Control
We use optimistic locking on the `Inventory` entity. If two processes try to update the same inventory simultaneously, one will fail with a `ConcurrencyError`. The application layer is designed to retry these operations or return a meaningful error to the user.
