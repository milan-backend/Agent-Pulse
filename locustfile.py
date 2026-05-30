from locust import HttpUser, task, between
import uuid

API_KEY = "d2b3f5fe.UoomLcUJ-ExwaMi-2NkyBViZ7mPUem32J6HyQ1Nbdfg"


class StepUser(HttpUser):

    host = "https://api.agentpulseai.dev"

    wait_time = between(2, 5)

    @task
    def execute_step(self):

        payload = {
            "task_name": "ping",
            "input_data": {
                "prompt": "hi"
            },
            "idempotency_key": str(uuid.uuid4())
        }

        with self.client.post(
            "/steps/execute",
            json=payload,
            headers={
                "X-API-Key": API_KEY
            },
            catch_response=True
        ) as response:

            print("\n========================")
            print("STATUS:", response.status_code)
            print("BODY:", response.text)
            print("========================\n")

            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"{response.status_code}: {response.text}"
                )