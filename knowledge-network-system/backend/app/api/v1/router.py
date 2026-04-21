from fastapi import APIRouter

from app.api.v1.endpoints.graph import router as graph_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.parse import router as parse_router
from app.api.v1.endpoints.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
api_router.include_router(parse_router, prefix="/parse", tags=["parse"])
api_router.include_router(graph_router, prefix="/graph", tags=["graph"])
