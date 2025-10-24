# backend/app/routers/scan.py
import asyncio
import traceback
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..models import Scan
from ..schemas import ScanCreate, ScanResponse, ScanStatusResponse
from ..services.report_service import run_full_scan

router = APIRouter(prefix="/scan", tags=["scan"])


async def _run_scan_background(scan_id: int, url: str, max_pages: int, max_depth: int) -> None:
    """
    Background coroutine to run the scan and update DB.
    Uses its own DB session (SessionLocal) to avoid reusing request session.
    """
    db: Session = SessionLocal()
    try:
        scan_obj: Optional[Scan] = db.get(Scan, scan_id)
        if not scan_obj:
            return

        # Mark RUNNING
        scan_obj.status = "RUNNING"
        db.add(scan_obj)
        db.commit()
        db.refresh(scan_obj)

        # Run the external scan (Person 2)
        try:
            result = await run_full_scan(url, max_pages=max_pages, max_depth=max_depth)
            report_path = None
            if isinstance(result, dict):
                report_path = result.get("report_path")

            scan_obj.report_path = report_path
            scan_obj.status = "COMPLETED"
            db.add(scan_obj)
            db.commit()
            db.refresh(scan_obj)
        except Exception as exc:
            # Change status to FAILED and record a small error file if possible
            scan_obj.status = "FAILED"
            try:
                err_text = "".join(traceback.format_exception_only(type(exc), exc))
                err_file = f"reports_output/scan_{scan_id}_error.txt"
                os_path = "reports_output"
                # ensure directory exists
                import os as _os

                _os.makedirs(os_path, exist_ok=True)
                with open(err_file, "w", encoding="utf-8") as fh:
                    fh.write(err_text)
                scan_obj.report_path = err_file
            except Exception:
                # ignore file write errors
                pass
            db.add(scan_obj)
            db.commit()
    finally:
        db.close()


@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(payload: ScanCreate, db: Session = Depends(get_db)):
    """
    Queue a new scan and return scan metadata immediately.
    """
    scan_obj = Scan(url=str(payload.url), status="QUEUED", report_path=None)
    db.add(scan_obj)
    db.commit()
    db.refresh(scan_obj)

    # schedule background task
    asyncio.create_task(_run_scan_background(scan_obj.id, str(payload.url), payload.max_pages, payload.max_depth))

    return ScanResponse(
        scan_id=scan_obj.id,
        url=scan_obj.url,
        status=scan_obj.status,
        report_path=scan_obj.report_path,
        created_at=scan_obj.created_at,
        updated_at=scan_obj.updated_at,
    )


@router.get("/{scan_id}/status", response_model=ScanStatusResponse)
def get_scan_status(scan_id: int, db: Session = Depends(get_db)):
    """
    Return the current status for a scan.
    """
    scan_obj = db.get(Scan, scan_id)
    if not scan_obj:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanStatusResponse(
        scan_id=scan_obj.id,
        url=scan_obj.url,
        status=scan_obj.status,
        created_at=scan_obj.created_at,
    )
