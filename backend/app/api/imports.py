# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.storage import get_db
# from app.services.sample_loader import load_sample_payload
# from app.services.ingestion import import_sample_payload
# from app.schemas.imports import ImportSummaryResponse
# from app.services.recall import rebuild_recall_index

# # In the endpoint, after the import succeeds:

# router = APIRouter(prefix="/api/imports", tags=["Imports"])


# @router.post("/sample", response_model=ImportSummaryResponse)
# async def import_sample(db: Session = Depends(get_db)) -> ImportSummaryResponse:
#     try:
#         payload = load_sample_payload()
#     except FileNotFoundError as exc:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

#     summary = import_sample_payload(db, payload)
#     rebuild_recall_index(db)
#     return summary

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.imports import ImportSummaryResponse
from app.services.ingestion import import_sample_payload
from app.services.recall import rebuild_recall_index
from app.services.sample_loader import load_sample_payload
from app.storage import get_db

router = APIRouter(prefix="/api/imports", tags=["Imports"])


@router.post("/sample", response_model=ImportSummaryResponse)
def import_sample(db: Session = Depends(get_db)) -> ImportSummaryResponse:
    try:
        payload = load_sample_payload()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    summary = import_sample_payload(db, payload)
    rebuild_recall_index(db)
    return summary