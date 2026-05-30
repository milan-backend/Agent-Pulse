from locust import HttpUser, task, between
import uuid

API_KEY = "d2b3f5fe.UoomLcUJ-ExwaMi-2NkyBViZ7mPUem32J6HyQ1Nbdfg"

class StepUser(HttpUser):

    host = "https://api.agentpulseai.dev"

    wait_time = between(2, 5)

    @task
    def execute_step(self):

        self.client.post(
            "/steps/execute",
            json={
                "task_name": "ping",
                "input_data": {
                    "prompt": "hi"
                },
                "idempotency_key": str(uuid.uuid4())
            },
            headers={
                "X-API-Key": API_KEY
            }
        )