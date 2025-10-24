# backend/app/schemas.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime


# ---------
# Request models
# ---------
class ScanCreate(BaseModel):
    url: HttpUrl = Field(..., description="The URL to scan (must be a valid URL)")
    max_pages: Optional[int] = Field(10, ge=1, le=100, description="Maximum pages to crawl")
    max_depth: Optional[int] = Field(1, ge=0, le=5, description="Link depth to follow")


# ---------
# Shared models for report content (kept generic to accept Axe output)
# ---------
class ViolationNode(BaseModel):
    html: Optional[str] = None
    target: Optional[List[str]] = None
    any: Optional[List[Any]] = None
    all: Optional[List[Any]] = None


class Violation(BaseModel):
    id: Optional[str] = None
    impact: Optional[str] = None
    description: Optional[str] = None
    helpUrl: Optional[str] = None
    nodes: Optional[List[ViolationNode]] = None


class PageReport(BaseModel):
    url: str
    axe: Optional[Dict[str, Any]] = None   # raw axe JSON for the page
    screenshot: Optional[str] = None
    error: Optional[str] = None


class ReportSummary(BaseModel):
    total_violations: int = 0
    by_impact: Dict[str, int] = {}
    pages_scanned: int = 0


class FullReport(BaseModel):
    start_url: str
    scanned_at: str
    pages: List[PageReport] = []
    summary: Optional[ReportSummary] = None


# ---------
# Response models for DB-backed Scan records
# ---------
class ScanResponse(BaseModel):
    scan_id: int
    url: str
    status: str
    report_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ScanStatusResponse(BaseModel):
    scan_id: int
    url: str
    status: str
    created_at: Optional[datetime] = None


# ---------
# Response wrapper for listing reports
# ---------
class ReportsListItem(BaseModel):
    scan_id: int
    url: str
    status: str
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
