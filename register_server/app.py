from flask import Flask, request, jsonify
import subprocess
import server_config
import os
import logging
import requests
from flask import g
import time
from services.auth_service import AuthService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
from services.provider_service import ProviderService
from services.wireguard_service import WireguardService

provider_service = ProviderService(os.environ.get('DATA_SERVICE_URL', "http://localhost:8002"))
wireguard_service = WireguardService(os.environ.get('WIREGUARD_SERVICE_URL', "http://localhost:5000"))

auth_service = AuthService(os.environ.get('AUTH_SERVICE_URL', 'http://localhost:8003'))

@app.before_request
def authenticate_request():
    # Only skip for endpoints that don't require auth (e.g., health checks)
    if request.endpoint in ('static',):
        return
    if request.path in ('/health',):
        return
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid authorization token'}), 401
    token = auth_header.split(' ')[1]
    try:
        data = auth_service.validate_token(token)
        if not data:
            return jsonify({'error': 'Invalid or expired token'}), 401
        g.user_id = data['user_id']
    except Exception as e:
        return jsonify({'error': f'Auth service error: {str(e)}'}), 401


@app.route("/register", methods=["GET"])
def register():
    try:
        user_id = g.user_id

        try:
            provider = provider_service.get_provider(user_id)
            if provider:
                return jsonify({
                    "server_ip": wireguard_service.get_server_ip(),
                    "status": "EXISTING_USER_REGISTERED",
                    "network_ip": provider["network_ip"],
                    "credits": provider["credits"]
                }), 200
        except Exception:
            pass
        
        private_key, public_key = wireguard_service.generate_keypair()

        created_provider = provider_service.create_provider(user_id, public_key)

        conf = wireguard_service.generate_client_wg_conf(
            private_key,
            created_provider['ip']
        )

        wireguard_service.add_provider(public_key, created_provider['ip'])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "network_ip": created_provider['ip'],
        "server_ip": wireguard_service.get_server_ip(),
        "conf": conf,
        "status": "NEW_USER_REGISTERED"
    })


@app.route("/details", methods=["GET"])
def details():
    try:
        user_id = g.user_id
        provider = provider_service.get_provider(user_id)
        if not provider:
            return jsonify({"error": "No provider for user", "status": "NO_PROVIDER_YET"}), 400
    
        return jsonify({
            "status": "SUCCESS",
            "credits": provider["credits"],
            "last_connection": provider["last_connection_time"],
            "network_ip": provider["network_ip"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 