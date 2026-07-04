from app.models.audit_log import AuditLog

def create_audit_log(
    db,
    workspace_id: str,
    action: str,
    user: object = None,  # 🟢 Accepts current_user safely from endpoint dependencies
    agent_id=None,
    step_id=None,
    input_data=None,
    output_data=None,
    error_message=None
):
    log = AuditLog(
        workspace_id=workspace_id,
        action=action,
        agent_id=agent_id,
        step_id=step_id,
        input_data=input_data,
        output_data=output_data,
        error_message=error_message
    )

    # 🟢 If user context is provided, pull and save their profile state snapshots
    if user:
        log.user_id = getattr(user, "id", None)
        log.user_name = getattr(user, "name", None)
        log.user_email = getattr(user, "email", None)
        log.user_role = getattr(user, "role", None)

    db.add(log)
    
    # ⚡ THE CURE: Change flush to commit so it saves permanently to disk!
    db.commit()  
    
    # Refresh to make sure the returned log object has its auto-generated fields populated
    db.refresh(log) 
    return log