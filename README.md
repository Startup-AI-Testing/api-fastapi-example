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

## Ejemplo de uso

### Crear un producto

```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "description": "Laptop gaming", "price": 999.99, "stock": 10}'
```

### Crear una orden

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_name": "Juan", "customer_email": "juan@example.com", "items": [{"product_id": 1, "quantity": 2}]}'
```
