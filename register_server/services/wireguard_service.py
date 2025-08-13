import os
import subprocess
import requests
from typing import List, Dict
import shutil
import time

from services.base_service import BaseService
from services.provider_service import ProviderService

class WireguardService(BaseService):
    def __init__(self, wireguard_server_url: str):
        super().__init__(wireguard_server_url)
        self.config_path = os.environ.get('CONFIG_PATH', "/etc/wireguard/wg0.conf")
        self.server_network_ip = os.environ.get('SERVER_NETWORK_IP', "10.10.0.0")
        self.server_port = os.environ.get('SERVER_PORT', 51820)
        self.provider_service = ProviderService(os.environ.get('DATA_SERVICE_URL', "http://localhost:8002"))
        # server public ip
        self.server_endpoint = self.get_device_public_ip()
        # fetch keys
        self.server_private_key, self.server_public_key = self.get_wg_keys()


    def generate_wg_conf(self, providers: List[Dict]):
        """
        Generates wg0.conf with all connected peers.
        providers: list of dicts with keys: public_key, allowed_ip, endpoint
        """
        interface_config = "\n".join([
            "[Interface]",
            f"PrivateKey = {self.server_private_key}",
            f"Address = {self.server_network_ip}/24",
            f"ListenPort = {self.server_port}"
        ])
        
        conf = [interface_config.strip()]
        for p in providers:
            peer = f"""
[Peer]
PublicKey = {p['public_key']}
AllowedIPs = {p['network_ip']}/32
"""
            conf.append(peer.strip())
        
        print("Final config:", conf)        


    def generate_client_wg_conf(self, client_private_key: str, client_ip: str):
        """
        Generates a WireGuard client configuration file.

        Args:
            client_private_key (str): The client's private key.
            client_ip (str): The IP address assigned to the client (e.g., "10.0.0.2/32").
        """
        conf = f"""[Interface]
PrivateKey = {client_private_key}
Address = {client_ip}/32
DNS = 1.1.1.1

[Peer]
PublicKey = {self.server_public_key}
AllowedIPs = {self.server_network_ip}/24
Endpoint = {self.server_endpoint}:{self.server_port}
PersistentKeepalive = 25
"""
        return conf


    def fetch_providers_and_generate_conf(self):
        """
        Fetches all providers from API and generates wg0.conf
        """
        providers = self.provider_service.get_all_providers()
        self.generate_wg_conf(providers)


    def add_provider(self, public_key: str, network_ip: str):
        response = requests.post(f"{self.base_url}/add-peer", json={"peer_public_key": public_key, "allowed_ips": network_ip})
        return response.json()

    def reload_wg(self):
        response = requests.get(f"{self.base_url}/reload")
        return response.json()

    def restart_wg(self):
        response = requests.get(f"{self.base_url}/restart")
        return response.json()

    def get_wg_keys(self):
        response = requests.get(f"{self.base_url}/keys")
        res_json = response.json()  
        return res_json["private_key"], res_json["public_key"]

    def generate_keypair(self):
        response = requests.get(f"{self.base_url}/generate-keys")
        res_json = response.json()  
        return res_json["private_key"], res_json["public_key"]

    def get_device_public_ip(self):
        return "127.0.0.1"
