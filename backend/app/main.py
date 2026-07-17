from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.api import (
    auth, accounts, contacts, opportunities, custom_objects, workflows, reports,
    products, territories, events,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Husky CRM API",
    description="Salesforce Platform Simplified - CRM API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(contacts.router)
app.include_router(opportunities.router)
app.include_router(custom_objects.router)
app.include_router(workflows.router)
app.include_router(reports.router)
app.include_router(reports.dashboard_router)
app.include_router(products.router)
app.include_router(territories.router)
app.include_router(events.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
