from uuid import uuid4


def generate_task_id() -> str:
    return str(uuid4())
