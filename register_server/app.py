from flask import Flask, request, jsonify
import subprocess
import server_config
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
from services.provider_service import ProviderService

provider_service = ProviderService()

def add_peer(public_key, client_ip):
    subprocess.run([
        "wg", "set", server_config.WG_INTERFACE,
        "peer", public_key,
        "allowed-ips", f"{client_ip}/32"
    ], check=True)
    peer_block = f"\n[Peer]\nPublicKey = {public_key}\nAllowedIPs = {client_ip}/32\n"
    with open(server_config.WG_CONF_PATH, "a") as conf:
        conf.write(peer_block)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    public_key = data.get("public_key")
    if not public_key:
        return jsonify({"error": "Missing public_key"}), 400

    try:
        # # Get token from Authorization header
        # auth_header = request.headers.get('Authorization')
        # if not auth_header or not auth_header.startswith('Bearer '):
        #     return jsonify({"error": "Missing or invalid authorization token"}), 401
        # user_id = auth_header.split(' ')[1]

        # Create provider and get network IP
        client_ip = provider_service.create_provider_with_ip("admin", public_key)
        add_peer(public_key, client_ip)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "server_public_key": server_config.SERVER_PUBLIC_KEY,
        "server_endpoint": server_config.SERVER_ENDPOINT,
        "allowed_ips": server_config.ALLOWED_IPS,
        "client_ip": client_ip
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 