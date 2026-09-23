from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models.meta_db import init_db
from app.routers import connect_db, query


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize metadata database tables on startup
    init_db()
    # Pre-warm demo schema cache for instant connection
    connect_db.preload_demo_cache()
    yield



app = FastAPI(
    title="NL2SQL Assistant Backend",
    description="Natural Language to SQL Assistant Backend API",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Phase 2 Routers
app.include_router(connect_db.router, prefix="/api", tags=["Database Connection"])
app.include_router(query.router, prefix="/api", tags=["Query"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
