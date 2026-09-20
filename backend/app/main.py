from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.invoices import router as invoices_router
from app.api.suppliers import router as suppliers_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    yield
    print("Shutting down application...")


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(invoices_router)
app.include_router(suppliers_router)


@app.get("/health")
def health():
    return {"status": "ok"}