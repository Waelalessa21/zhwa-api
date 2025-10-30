from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.core.database import engine
import logging
from app.models import Base
from app.api import auth, stores, offers, upload, dashboard, subscriptions
from app.schemas import ErrorResponse
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Zhwaweb Admin API",
    description="FastAPI backend for Zhwaweb admin system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("uploads"):
    os.makedirs("uploads")

app.mount("/static", StaticFiles(directory="uploads"), name="static")

app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(offers.router)
app.include_router(upload.router)
app.include_router(dashboard.router)
app.include_router(subscriptions.router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP Error",
            message=exc.detail
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logging.exception("Unhandled exception while processing request")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred"
        ).dict()
    )

@app.middleware("http")
async def convert_auth_errors(request: Request, call_next):
    """Convert 403 Forbidden to 401 Unauthorized for missing credentials"""
    try:
        response = await call_next(request)
        
        if response.status_code == 403:
            if not request.headers.get("authorization"):
                return JSONResponse(
                    status_code=401,
                    content=ErrorResponse(
                        error="HTTP Error",
                        message="Could not validate credentials"
                    ).dict()
                )
        
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise

@app.get("/")
def read_root():
    return {"message": "Zhwaweb Admin API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
