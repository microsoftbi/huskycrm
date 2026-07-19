from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.api import (
    auth, accounts, contacts, opportunities, custom_objects, workflows, reports,
    products, territories, events, profiles, audit_logs,
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


@app.middleware("http")
async def set_audit_user(request, call_next):
    """Set current user ID in audit contextvar for automatic audit logging."""
    from app.services.audit_service import current_user_id
    token = current_user_id.set("system")
    try:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            from app.core.security import decode_token
            token_str = auth_header.split(" ")[1]
            payload = decode_token(token_str)
            if payload and payload.get("sub"):
                current_user_id.set(payload["sub"])
        response = await call_next(request)
        return response
    finally:
        current_user_id.reset(token)

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
app.include_router(profiles.router)
app.include_router(audit_logs.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
