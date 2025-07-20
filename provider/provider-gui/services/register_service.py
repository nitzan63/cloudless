from services.base_service import BaseService
import requests

class RegisterService(BaseService):
    def __init__(self, base_url):
        super().__init__(base_url)

    def register(self):
        url = f"{self.base_url}/register"
        response = requests.get(url)
        return self._handle_response(response)

    def get_details(self):
        url = f"{self.base_url}/details"
        response = requests.get(url)
        return self._handle_response(response)

    def trigger(self):
        url = f"{self.base_url}/trigger"
        response = requests.get(url)
        return self._handle_response(response)
