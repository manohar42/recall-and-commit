from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("")
async def health_check() -> dict[str, str]:

    return {
        "status": "ok",
        "service": "recall-and-commit-api",
        "version": "0.1.0",
    }

