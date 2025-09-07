import os
import requests
import json
from dotenv import load_dotenv
from services.base_service import BaseService
load_dotenv()

class LivyService(BaseService):
    def _pretty_print(self, resp):
        """Nicely print JSON response."""
        print(json.dumps(resp.json(), indent=2))

    def list_batches(self, verbose=True):
        """List all batch jobs."""
        resp = requests.get(f"{self.base_url}/batches")
        if verbose:
            print("=== List Batches ===")
            self._pretty_print(resp)
        return resp

    def submit_batch(self, file_path, name="ExampleBatchJob", verbose=True):
        """
        Submit a batch job (PySpark script).
        file_path: path inside Livy container, e.g. local:/scripts/your_script.py
        Returns the batch job ID.
        """
        data = {
            "file": file_path,
            "name": name
        }
        resp = requests.post(f"{self.base_url}/batches", json=data)
        if verbose:
            print("=== Submit Batch Job ===")
            self._pretty_print(resp)
        return resp.json().get("id")

    def get_batch_status(self, batch_id, verbose=False):
        """Get the status of a batch job."""
        resp = requests.get(f"{self.base_url}/batches/{batch_id}")
        if verbose:
            print(f"=== Status of Batch {batch_id} ===")
            self._pretty_print(resp)
        return resp

    def get_batch_logs(self, batch_id, verbose=False):
        """Get the logs of a batch job."""
        resp = requests.get(f"{self.base_url}/batches/{batch_id}/log?from=0&size=1")
        total = resp.json()['total']
        resp = requests.get(f"{self.base_url}/batches/{batch_id}/log?from=0&size={total}")
        log = resp.json()['log']
        if verbose:
            print(f"=== Logs of Batch {batch_id} ===")
            self._pretty_print(resp)
        return '\n'.join(log)

    def kill_batch(self, batch_id, verbose=True):
        """Kill a batch job."""
        resp = requests.delete(f"{self.base_url}/batches/{batch_id}")
        if verbose:
            print(f"=== Kill Batch {batch_id} ===")
            print(f"Status Code: {resp.status_code}")
        return resp
