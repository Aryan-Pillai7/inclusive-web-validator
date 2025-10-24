# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="QUEUED", index=True)
    report_path = Column(String(4096), nullable=True)  # path to JSON file (reports_output/...)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def as_dict(self):
        """Lightweight helper to convert model to dict for quick JSON responses."""
        return {
            "scan_id": self.id,
            "url": self.url,
            "status": self.status,
            "report_path": self.report_path,
            "created_at": None if self.created_at is None else self.created_at.isoformat(),
            "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
        }
