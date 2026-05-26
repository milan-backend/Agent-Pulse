import hashlib
import json


def generate_cache_key(
    task_name: str,
    input_data: dict[str, object]
) -> str:

    data_string = json.dumps(
        input_data,
        sort_keys=True
    )

    raw_key = f"{task_name}:{data_string}"

    return hashlib.sha256(
        raw_key.encode()
    ).hexdigest()