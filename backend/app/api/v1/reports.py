from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid
import csv
import io
from datetime import datetime

from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.core.deps import require_role

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/mis")
async def generate_mis_report(
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    format: str = "csv",
    current_user: User = Depends(require_role(["super_admin", "state_authority"])),
    db: AsyncSession = Depends(get_db),
):
    query = select(Project).where(Project.is_deleted == False)
    if state_id:
        query = query.where(Project.state_id == state_id)
    if district_id:
        query = query.where(Project.district_id == district_id)
    if status_filter:
        query = query.where(Project.status == status_filter)

    query = query.options(
        selectinload(Project.state),
        selectinload(Project.district),
    )
    result = await db.execute(query.order_by(Project.created_at.desc()))
    projects = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Project Name", "Status", "Priority", "Current Stage",
        "Estimated Budget (₹)", "State", "District",
        "Created At", "Target Completion"
    ])

    for p in projects:
        writer.writerow([
            p.name,
            p.status.value if hasattr(p.status, 'value') else str(p.status),
            p.priority.value if hasattr(p.priority, 'value') else str(p.priority),
            p.current_stage,
            float(p.estimated_budget) if p.estimated_budget else "",
            p.state.name if p.state else "",
            p.district.name if p.district else "",
            p.created_at.strftime("%Y-%m-%d") if p.created_at else "",
            p.target_completion_date.strftime("%Y-%m-%d") if p.target_completion_date else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=MIS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )
