from app.models.usage import Usage


def log_usage(db, agent_id, step_id, action,cost=0, prompt_tokens=0, completion_tokens=0):
    usage = Usage(
        agent_id=agent_id,
        step_id=step_id,
        action=action,
        cost=cost,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens
    )

    db.add(usage)
    db.commit()