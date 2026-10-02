from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.api.imports import router as import_router
from app.api.conversations import router as conversations_router
from app.api.recall import router as recall_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Recall & Commit API is starting.")
    yield
    print("Recall & Commit API is shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Recall & Commit API",
        description=(
            "Local-first backend for evidence-backed recall and "
            "user-approved commitment tracking."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request.state.request_id = request.headers.get(
            "X-Request-ID",
            str(uuid4()),
        )

        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "The request contains invalid data.",
                    "request_id": request_id,
                    "details": exc.errors(),
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected server error occurred.",
                    "request_id": request_id,
                }
            },
        )

    @app.get("/", tags=["System"])
    async def root() -> dict[str, str]:
        return {
            "message": "Recall & Commit API is running.",
            "docs": "/docs",
            "health": "/api/health",
        }

    app.include_router(health_router)
    app.include_router(import_router)
    app.include_router(conversations_router)
    app.include_router(recall_router)


    return app


app = create_app()