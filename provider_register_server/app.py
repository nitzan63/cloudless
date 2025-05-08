from flask import Flask, request, jsonify
import subprocess
import server_config
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
    client_ip = data.get("client_ip")
    if not public_key or not client_ip:
        return jsonify({"error": "Missing public_key or client_ip"}), 400

    try:
        add_peer(public_key, client_ip)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "server_public_key": server_config.SERVER_PUBLIC_KEY,
        "server_endpoint": server_config.SERVER_ENDPOINT,
        "allowed_ips": server_config.ALLOWED_IPS
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 