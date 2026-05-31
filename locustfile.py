from locust import HttpUser, task, between
import uuid
import random

API_KEY = "28d2d833.6itnFfSdACCU0UxejWYtnbJHK3g8hQj_dzkYqEEEltY"

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
            "additionalProp1": {}
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