import os
import subprocess
import requests
from typing import List, Dict
import shutil
import time

from services.base_service import BaseService
from services.provider_service import ProviderService

class WireguardService(BaseService):
    def __init__(self):
        super().__init__()
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
        # TODO: Fix the provider generation
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
        
        if len(providers) == 0:
            content = interface_config.strip()
        else:
            content = '\n\n'.join(conf)
        
        self.write_to_wg_config(content)
    
    def write_to_wg_config(self, content):
        # Write content using sudo tee
        process = subprocess.Popen(['sudo', 'tee', self.config_path], 
                                stdin=subprocess.PIPE, text=True)
        process.communicate(input=content)

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
ListenPort = {self.server_port}
DNS = 1.1.1.1

[Peer]
PublicKey = {self.server_public_key}
Endpoint = {self.server_endpoint}:{self.server_port}
AllowedIPs = {self.server_network_ip}/24
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
        """
        Adds a single provider (peer) to wg0.conf
        """
        # TODO: Understand how to add specific endpoints without downtime
        cmd = [
            "sudo", "wg", "set", "wg0",
            "peer", public_key,
            "allowed-ips", f"{network_ip}/32",
            "endpoint", self.server_endpoint,
            "persistent-keepalive", "25"
        ]

        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True)


    def remove_provider_from_conf(self, public_key: str, conf_path: str = "/etc/wireguard/wg0.conf"):
        """
        Removes a provider (peer) from wg0.conf by public key
        """
        if not os.path.exists(conf_path):
            return
        with open(conf_path, 'r') as f:
            lines = f.readlines()
        new_lines = []
        skip = False
        for line in lines:
            if line.strip().startswith('[Peer]'):
                skip = False
                peer_block = []
            if skip:
                continue
            peer_block.append(line)
            if line.strip().startswith('PublicKey =') and public_key in line:
                skip = True
                peer_block = []
                continue
            if not skip:
                new_lines.extend(peer_block)
                peer_block = []
        with open(conf_path, 'w') as f:
            f.writelines(new_lines)

    def apply_wg_changes(self):
        subprocess.run(['sudo', 'wg', 'syncconf', 'wg0', self.config_path])
    
    def start_wg_server(self):
        print("Stopping...")
        subprocess.run(['sudo', 'systemctl', 'stop', 'wg-quick@wg0'])
        time.sleep(5)
        print("Starting...")
        subprocess.run(['sudo', 'systemctl', 'start', 'wg-quick@wg0'])

    def generate_keypair(self):
        """
        Generates a WireGuard public/private key pair.
        Returns:
            Tuple[str, str]: (private_key, public_key)
        """
        private_key = subprocess.check_output(["wg", "genkey"]).decode().strip()
        public_key = subprocess.check_output(
            ["wg", "pubkey"], input=private_key.encode()
        ).decode().strip()
        return private_key, public_key

    import subprocess

    def get_wg_keys(self):
        # This might work without sudo depending on your setup
        private = subprocess.run(['sudo', 'wg', 'show', 'wg0', 'private-key'], 
                            capture_output=True, text=True)
        public = subprocess.run(['sudo', 'wg', 'show', 'wg0', 'public-key'], 
                            capture_output=True, text=True)
        
        if private.returncode != 0:
            private = os.environ.get('PRIVATE_KEY', "")
        else:
            private = private.stdout.strip()
        if public.returncode != 0:
            public = os.environ.get('PUBLIC_KEY', "")
        else:
            public = public.stdout.strip()
        
        return private, public


    def get_device_public_ip(self):
        result = subprocess.run(['curl', '-s', 'ifconfig.me'], 
                                capture_output=True, text=True)
        return result.stdout.strip()