from locust import HttpUser, task, between
import uuid
import random

API_KEY = "e5b93c6e.x94g1WzMPp7kVNLhoRt2lIAPr9fPzXEwEvzUzvNZ1bU"

TASKS = [
    "ping",
    "health_check",
    "test",
    "status"
]

class StepUser(HttpUser):

    host = "https://api.agentpulseai.dev"

    wait_time = between(2, 5)

    @task
    def execute_step(self):

        payload = {
            "task_name": random.choice(TASKS),
            "input_data": {
                "prompt": "hi"
            },
            "idempotency_key": str(uuid.uuid4())
        }

        response = self.client.post(
            "/steps/execute",
            json=payload,
            headers={
                "X-API-Key": API_KEY
            }
        )

        print(response.status_code)
        print(response.text)