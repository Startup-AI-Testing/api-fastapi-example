from fastapi import FastAPI

from .database import engine, Base
from .routers import products, orders, customers

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Example",
    description="API de ejemplo con ABM de Productos y Ordenes",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "name": "FastAPI Example API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# Include routers
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(customers.router)
