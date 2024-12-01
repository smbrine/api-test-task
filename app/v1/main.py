"""
V1's main module
"""

from fastapi import APIRouter

from app.v1.insurance import router as insurance_router

router = APIRouter(prefix="/v1")
router.include_router(insurance_router)
