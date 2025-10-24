# backend/app/routers/reports.py
import json
import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Scan
from ..schemas import ReportsListItem, FullReport

router = APIRouter(tags=["reports"])


def _resolve_report_file(report_path: str) -> str:
    if not report_path:
        return ""

    candidates = [
        report_path,
        os.path.join(os.getcwd(), report_path),
        os.path.join(os.path.dirname(__file__), "..", report_path),
        os.path.join(os.path.dirname(__file__), "..", "..", report_path),
    ]

    for c in candidates:
        p = os.path.normpath(c)
        if os.path.exists(p):
            return p
    return ""


@router.get("/reports", response_model=List[ReportsListItem])
def list_reports(db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc()).all()

    items = [
        ReportsListItem(
            scan_id=s.id,         # ✅ FIXED
            url=s.url,
            status=s.status,
            created_at=s.created_at,
        )
        for s in scans
    ]
    return items


@router.get("/report/{scan_id}", response_model=FullReport)
def get_report(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()  # ✅ FIXED
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if not scan.report_path:
        raise HTTPException(status_code=404, detail="Report not ready for this scan")

    report_file = _resolve_report_file(scan.report_path)
    if not report_file:
        raise HTTPException(
            status_code=500,
            detail=f"Report file not found on disk (expected: {scan.report_path})",
        )

    try:
        with open(report_file, "r", encoding="utf-8") as fh:
            report_json = json.load(fh)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Report file is not valid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read report file: {e}")

    return FullReport(**report_json)
