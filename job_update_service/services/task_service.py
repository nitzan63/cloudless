from services.base_service import BaseService
import requests

class TaskService(BaseService):
    def create_task(self, payload: dict):
        response = requests.post(f"{self.base_url}/tasks/", json=payload)
        return self._handle_response(response)

    def get_task(self, task_id: str):
        response = requests.get(f"{self.base_url}/tasks/{task_id}")
        return self._handle_response(response)

    def list_tasks(self):
        response = requests.get(f"{self.base_url}/tasks")
        return self._handle_response(response)

    def update_task(self, task_id: str, updates: dict):
        response = requests.patch(f"{self.base_url}/tasks/{task_id}", json=updates)
        return self._handle_response(response)

    def delete_task(self, task_id: str):
        response = requests.delete(f"{self.base_url}/tasks/{task_id}")
        return self._handle_response(response)

    def get_unfinished_tasks(self):
        response = requests.get(f"{self.base_url}/tasks/not-finished/all")
        return self._handle_response(response)
