from flask import Flask, request, jsonify
import subprocess
import server_config
import os
import logging
import requests
from flask import g
from services.auth_service import AuthService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
from services.provider_service import ProviderService
from services.wireguard_service import WireguardService


provider_service = ProviderService(os.environ.get('DATA_SERVICE_URL', "http://localhost:8002"))
wireguard_service = WireguardService()

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
            user = provider_service.get_provider(user_id)
            if user:
                return jsonify({"status": "registered"}), 200
        except Exception:
            pass
        
        private_key, public_key = wireguard_service.generate_keypair()

        created_provider = provider_service.create_provider(user_id, public_key)

        conf = wireguard_service.generate_client_wg_conf(
            private_key,
            created_provider['ip']
        )

        # wireguard_service.add_provider(public_key, created_provider['ip'])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "client_ip": created_provider['ip'],
        "conf": conf
    })


@app.route("/trigger", methods=["GET"])
def trigger():
    try:
        wireguard_service.fetch_providers_and_generate_conf()
        wireguard_service.start_wg_server()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 