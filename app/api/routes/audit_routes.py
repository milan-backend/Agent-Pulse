from fastapi import APIRouter, Depends, Query, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from typing import Optional
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.api.deps_user import get_current_user  # Adjust path to match your auth setup

router = APIRouter(prefix="/api/v1/audit-logs", tags=["Audit Logs"])

@router.get("")
def get_workspace_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    status: Optional[str] = Query(None), # "SUCCESS" or "FAILURE"
    start_date: Optional[str] = Query(None), # Format: YYYY-MM-DD
    end_date: Optional[str] = Query(None),   # Format: YYYY-MM-DD
    # ⚡ PERMANENT FIX: Automatically read the header sent by your frontend api.ts
    workspace_id: Optional[str] = Header(None, alias="workspace-id"), 
    db: Session = Depends(get_db),
    current_user: object = Depends(get_current_user)
):
    # 1. Multi-Tenancy Guard: Check the current user object first, fall back to the HTTP Header
    active_wksp = getattr(current_user, "active_workspace_id", None) or workspace_id
    
    if not active_wksp:
        raise HTTPException(
            status_code=400, 
            detail="Multi-tenancy isolation failure: No active workspace identifier provided."
        )

    # 2. Hard filter by the active workspace to secure company data isolation
    query = db.query(AuditLog).filter(AuditLog.workspace_id == active_wksp)

    # 3. Apply Text Search Filter (Name / Email / User ID)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                AuditLog.user_name.ilike(search_filter),
                AuditLog.user_email.ilike(search_filter),
                AuditLog.user_id.ilike(search_filter)
            )
        )

    # 4. Apply Action Dropdown Filter
    if action:
        query = query.filter(AuditLog.action == action.upper())

    # 5. Apply Status Filters
    if status:
        if status.upper() == "SUCCESS":
            query = query.filter(AuditLog.error_message == None)
        elif status.upper() == "FAILURE":
            query = query.filter(AuditLog.error_message != None)

    # 6. Apply Date Range Filters
    try:
        if start_date:
            parsed_start = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(AuditLog.timestamp >= parsed_start)
        if end_date:
            parsed_end = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            query = query.filter(AuditLog.timestamp <= parsed_end)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format criteria. Use YYYY-MM-DD.")

    # 7. Execute Server-Side Pagination
    total_logs = query.count()
    offset = (page - 1) * limit
    logs = query.order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    # 8. Return paginated response structure for the frontend table
    return {
        "total": total_logs,
        "page": page,
        "limit": limit,
        "results": [
            {
                "id": log.id,
                "user_id": log.user_id,
                "user_name": log.user_name,
                "user_email": log.user_email,
                "user_role": log.user_role,
                "action": log.action,
                "agent_id": log.agent_id,
                "step_id": log.step_id,
                "input_data": log.input_data,
                "output_data": log.output_data,
                "error_message": log.error_message,
                "status": "FAILURE" if log.error_message else "SUCCESS",
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]
    }