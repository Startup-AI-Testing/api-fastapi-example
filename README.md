# FastAPI Example API

API de ejemplo con CRUD de Productos y Ordenes usando SQLite.

## Requisitos

- Python 3.10+

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn app.main:app --reload
```

La API estará disponible en http://localhost:8000

## Documentación

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Productos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /products | Listar productos |
| GET | /products/{id} | Obtener producto |
| POST | /products | Crear producto |
| PUT | /products/{id} | Actualizar producto |
| DELETE | /products/{id} | Eliminar producto |

### Ordenes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /orders | Listar ordenes |
| GET | /orders/{id} | Obtener orden |
| POST | /orders | Crear orden |
| PUT | /orders/{id} | Actualizar orden |
| DELETE | /orders/{id} | Eliminar orden |

## Sistema de Inventario y Reservas

Este proyecto implementa un sistema robusto de gestión de inventario con soporte para reservas temporales, control transaccional y prevención de sobreventa (overselling).

### Arquitectura

Se sigue una arquitectura hexagonal con Domain-Driven Design (DDD):

- **Dominio**: Entidades (`Inventory`, `StockReservation`), Value Objects y Servicios de Dominio.
- **Aplicación**: Handlers de casos de uso (`ReserveStockHandler`, `ConfirmReservationHandler`, etc.).
- **Infraestructura**: Repositorios SQL con bloqueo optimista y adaptadores externos.
- **Interfaces**: Endpoints HTTP de FastAPI.

### Flujo de Reserva y Venta

1. **Reserva (Carrito)**: El usuario reserva stock temporalmente (15 min).
   - `POST /inventory/reserve`
2. **Checkout**: Al crear la orden, se confirma la reserva.
   - `POST /orders` (incluyendo `reservation_id`)
3. **Expiración**: Un job en segundo plano libera automáticamente las reservas expiradas.

### Endpoints de Inventario

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /inventory/reserve | Reservar stock para un producto |
| POST | /inventory/reserve/{id}/confirm | Confirmar una reserva manualmente |
| DELETE | /inventory/reserve/{id} | Liberar una reserva |
| GET | /inventory/product/{id} | Consultar disponibilidad de un producto |
| POST | /inventory/restock | Reponer stock (Admin) |
| POST | /inventory/adjust | Ajuste manual de stock (Admin) |
| GET | /inventory/movements | Historial de movimientos |
| GET | /inventory/low-stock | Productos con stock bajo |

### Ejemplos de API

#### Reservar Stock
```bash
curl -X POST http://localhost:8000/inventory/reserve \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2, "reservation_type": "cart"}'
```

#### Crear Orden con Reserva
```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Juan",
    "customer_email": "juan@example.com",
    "reservation_id": "uuid-de-la-reserva",
    "items": [{"product_id": 1, "quantity": 2}]
  }'
```

### Bloqueo Optimista

El sistema utiliza un campo `version` en la tabla de inventario para manejar la concurrencia. Si dos procesos intentan actualizar el mismo registro simultáneamente, uno fallará y el sistema reintentará la operación automáticamente hasta 3 veces.

### Jobs en Segundo Plano

- **Liberación de Reservas**: Cada 5 minutos se liberan las reservas que han superado su tiempo de expiración.
- **Detección de Stock Bajo**: Cada hora se verifica si hay productos por debajo de su punto de reorden.
