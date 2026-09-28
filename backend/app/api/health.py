from fastapi import APIRouter, status
from app.storage import check_database_connection
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/")
async def health_check() -> dict[str, str]:

    return {
        "status": "ok",
        "service": "recall-and-commit-api",
        "version": "0.1.0",
    }

@router.get("/ready")
async def readiness_check() -> JSONResponse:

    database_ok = check_database_connection()

    if not database_ok:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "checks": {
                    "database": "unavailable",
            },
            }
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ready",
            "checks": {
                "database": "ok",
            },
        },
    )


