import os
import subprocess
import requests
from typing import List, Dict

from services.base_service import BaseService
from services.provider_service import ProviderService

class WireguardService(BaseService):
    def __init__(self):
        super().__init__()
        self.provider_service = ProviderService(os.environ.get('DATA_SERVICE_URL', "http://localhost:8002"))

    def generate_wg_conf(self, providers: List[Dict], conf_path: str = "/etc/wireguard/wg0.conf"):
        """
        Generates wg0.conf with all connected peers.
        providers: list of dicts with keys: public_key, allowed_ip, endpoint
        """
        interface_config = f"""[Interface]\nPrivateKey = {os.environ.get('SERVER_PRIVATE_KEY')}\nAddress = 10.0.0.1/24\nListenPort = 51820\n"""
        conf = [interface_config.strip()]
        for p in providers:
            peer = f"""
[Peer]
PublicKey = {p['public_key']}
AllowedIPs = 0.0.0.0/0
Endpoint = {p.get('network_ip', '')}/32
PersistentKeepalive = 25
"""
            conf.append(peer.strip())
        with open(conf_path, 'w') as f:
            f.write('\n\n'.join(conf))

    def generate_client_wg_conf(self, client_private_key: str, client_ip: str):
        """
        Generates a WireGuard client configuration file.

        Args:
            client_private_key (str): The client's private key.
            client_ip (str): The IP address assigned to the client (e.g., "10.0.0.2/32").
        """
        conf = f"""[Interface]
PrivateKey = {client_private_key}
Address = {client_ip}/24
DNS = 1.1.1.1

[Peer]
PublicKey = {os.environ.get('SERVER_PUBLIC_KEY')}
Endpoint = {os.environ.get('SERVER_ENDPOINT')}
AllowedIPs = 10.10.0.0/24
PersistentKeepalive = 25
"""
        
        return conf


    def fetch_providers_and_generate_conf(self, conf_path: str = "/etc/wireguard/wg0.conf"):
        """
        Fetches all providers from API and generates wg0.conf
        """
        providers = self.provider_service.get_all_providers()
        print(providers, type(providers))
        self.generate_wg_conf(providers, conf_path)

    def add_provider_to_conf(self, provider: Dict, conf_path: str = "/etc/wireguard/wg0.conf"):
        """
        Adds a single provider (peer) to wg0.conf
        """
        peer = f"""
[Peer]
PublicKey = {provider['public_key']}
AllowedIPs = {provider['allowed_ip']}
Endpoint = {provider.get('endpoint', '')}
PersistentKeepalive = 25
"""
        with open(conf_path, 'a') as f:
            f.write('\n' + peer.strip() + '\n')

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

    def apply_wg_changes(self, interface: str = "wg0"):
        """
        Applies changes to the local WireGuard interface
        """
        subprocess.run(["wg-quick", "down", interface], check=False)
        subprocess.run(["wg-quick", "up", interface], check=True)

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
