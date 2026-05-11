from app.models.audit_log import AuditLog


def log_event(
    db,
    agent_id,
    step_id,
    action,
    input_data=None,
    output_data=None,
    error_message=None
):
    log = AuditLog(
        agent_id=agent_id,
        step_id=step_id,
        action=action,
        input_data=input_data,
        output_data=output_data,
        error_message=error_message
    )

    db.add(log)
    db.commit()