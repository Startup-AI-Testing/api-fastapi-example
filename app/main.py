from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import products, orders
from src.interfaces.http.inventory import router as inventory_router
from src.infrastructure.jobs.scheduler import start_scheduler

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler = start_scheduler()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(
    title="FastAPI Example",
    description="API de ejemplo con ABM de Productos y Ordenes",
    version="1.0.0",
    lifespan=lifespan
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
app.include_router(inventory_router)
