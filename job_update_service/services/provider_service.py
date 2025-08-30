from services.base_service import BaseService
import requests


class ProviderService(BaseService):
    def add_credits(self, network_ips, amount: int):
        payload = {
            "network_ips": network_ips,
            "amount": amount,
        }
        response = requests.post(f"{self.base_url}/providers/credits/add", json=payload)
        return self._handle_response(response)


