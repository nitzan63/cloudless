from flask import Flask, request, jsonify
import subprocess
import server_config
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
from services.provider_service import ProviderService
from services.wireguard_service import WireguardService


provider_service = ProviderService(os.environ.get('DATA_SERVICE_URL', "http://localhost:8002"))
wireguard_service = WireguardService()


@app.route("/register", methods=["GET"])
def register():
    try:
        # # Get token from Authorization header
        # auth_header = request.headers.get('Authorization')
        # if not auth_header or not auth_header.startswith('Bearer '):
        #     return jsonify({"error": "Missing or invalid authorization token"}), 401
        # user_id = auth_header.split(' ')[1]
        user_id = "admin"

        # check if user exists
        try:
            user = provider_service.get_provider(user_id)
            if user:
                return jsonify({"status": "success", "user": user}), 200
        except Exception:
            pass
        
        private_key, public_key = wireguard_service.generate_keypair()

        created_provider = provider_service.create_provider(user_id, public_key)

        conf = wireguard_service.generate_client_wg_conf(
            private_key, 
            created_provider['ip']
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "server_public_key": server_config.SERVER_PUBLIC_KEY,
        "server_endpoint": server_config.SERVER_ENDPOINT,
        "allowed_ips": server_config.ALLOWED_IPS,
        "client_ip": created_provider['ip'],
        "conf": conf
    })


@app.route("/details", methods=["GET"])
def details():
    try:
        # # Get token from Authorization header
        # auth_header = request.headers.get('Authorization')
        # if not auth_header or not auth_header.startswith('Bearer '):
        #     return jsonify({"error": "Missing or invalid authorization token"}), 401
        # user_id = auth_header.split(' ')[1]

        created_provider = provider_service.get_provider("admin")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "server_public_key": server_config.SERVER_PUBLIC_KEY,
        "server_endpoint": server_config.SERVER_ENDPOINT,
        "allowed_ips": server_config.ALLOWED_IPS,
        "client_ip": created_provider['network_ip']
    })


@app.route("/trigger", methods=["GET"])
def trigger():
    try:
        wireguard_service.fetch_providers_and_generate_conf(conf_path="test_generated_config_files/wg0.conf")
        # wireguard_service.apply_wg_changes()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 