#!/usr/bin/env python3
import subprocess
import requests
import json
from flask import Flask, jsonify, request
import threading
import time
import os
import base64
import secrets

app = Flask(__name__)

# WireGuard configuration paths
WG_CONFIG_PATH = '/etc/wireguard/wg0.conf'
WG_KEYS_DIR = '/etc/wireguard'

def get_wg_status():
    """Get WireGuard status and return connected endpoints"""
    try:
        result = subprocess.run(['wg', 'show'], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error getting WireGuard status: {e.stderr}"
    except FileNotFoundError:
        return "WireGuard command not found"

def get_public_key():
    """Get the WireGuard server's public key"""
    try:
        with open('/etc/wireguard/server_public.key', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Public key file not found"
    except Exception as e:
        return f"Error reading public key: {str(e)}"

def get_private_key():
    """Get the WireGuard server's private key"""
    try:
        with open('/etc/wireguard/server_private.key', 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Private key file not found"
    except Exception as e:
        return f"Error reading private key: {str(e)}"

def check_wg_running():
    """Check if WireGuard is running"""
    try:
        result = subprocess.run(['wg', 'show'], capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def generate_keypair():
    """Generate a new WireGuard keypair"""
    try:
        # Generate private key
        private_key = subprocess.run(['wg', 'genkey'], capture_output=True, text=True, check=True)
        private_key = private_key.stdout.strip()
        
        # Generate public key from private key
        public_key = subprocess.run(['wg', 'pubkey'], input=private_key, capture_output=True, text=True, check=True)
        public_key = public_key.stdout.strip()
        
        return {
            'private_key': private_key,
            'public_key': public_key
        }
    except subprocess.CalledProcessError as e:
        return None

def add_peer_to_config(peer_public_key, allowed_ips):
    """Add a new peer to the WireGuard configuration file"""
    try:
        # Read current config
        with open(WG_CONFIG_PATH, 'r') as f:
            config_lines = f.readlines()
        
        peer_section = f"\n[Peer]\n"
        peer_section += f"PublicKey = {peer_public_key}\n"
        peer_section += f"AllowedIPs = {allowed_ips}\n"
        
        config_lines.append(peer_section)
        
        with open(WG_CONFIG_PATH, 'w') as f:
            f.writelines(config_lines)
        
        return True
    except Exception as e:
        return False

def add_peer_to_wg(peer_public_key, allowed_ips):
    """Add a peer to the running WireGuard interface"""
    try:
        # Add peer to WireGuard interface
        cmd = [
            'wg', 'set', 'wg0', 'peer', peer_public_key,
            'allowed-ips', allowed_ips
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

def restart_wireguard():
    """Restart the WireGuard service"""
    try:
        # Stop WireGuard
        subprocess.run(['systemctl', 'stop', 'wg-quick@wg0'], capture_output=True, check=True)
        time.sleep(2)
        
        # Start WireGuard
        subprocess.run(['systemctl', 'start', 'wg-quick@wg0'], capture_output=True, check=True)
        time.sleep(3)
        
        # Check if it's running
        return check_wg_running()
    except subprocess.CalledProcessError as e:
        return False

def reload_wireguard_config():
    """Reload WireGuard configuration without full restart"""
    try:
        # Sync configuration
        subprocess.run(['wg', 'syncconf', 'wg0', WG_CONFIG_PATH], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify WireGuard is running"""
    wg_running = check_wg_running()
    
    if wg_running:
        return jsonify({
            'status': 'healthy',
            'wireguard': 'running',
            'message': 'WireGuard is running'
        }), 200
    else:
        return jsonify({
            'status': 'unhealthy',
            'wireguard': 'not running',
            'message': 'WireGuard is not running'
        }), 503

@app.route('/status', methods=['GET'])
def wireguard_status():
    """Get WireGuard status showing all connected endpoints"""
    status = get_wg_status()
    
    return jsonify({
        'status': 'success',
        'wireguard_status': status
    }), 200

@app.route('/public-key', methods=['GET'])
def public_key():
    """Get the WireGuard server's public key"""
    key = get_public_key()
    
    return jsonify({
        'status': 'success',
        'public_key': key
    }), 200

@app.route('/private-key', methods=['GET'])
def private_key():
    """Get the WireGuard server's private key"""
    key = get_private_key()
    
    return jsonify({
        'status': 'success',
        'private_key': key
    }), 200

@app.route('/keys', methods=['GET'])
def get_keys():
    """Get both public and private keys"""
    public = get_public_key()
    private = get_private_key()
    
    return jsonify({
        'status': 'success',
        'public_key': public,
        'private_key': private
    }), 200

@app.route('/generate-keys', methods=['GET'])
def generate_keys():
    """Generate a new WireGuard keypair"""
    keypair = generate_keypair()
    
    if keypair:
        return jsonify({
            'status': 'success',
            'message': 'Keypair generated successfully',
            'private_key': keypair['private_key'],
            'public_key': keypair['public_key']
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate keypair'
        }), 500

@app.route('/add-peer', methods=['POST'])
def add_peer():
    """Add a new peer to WireGuard"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No JSON data provided'
            }), 400
        
        required_fields = ['peer_public_key', 'allowed_ips']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        peer_public_key = data['peer_public_key']
        allowed_ips = data['allowed_ips']
        
        config_success = add_peer_to_config(peer_public_key, allowed_ips)
        
        wg_success = add_peer_to_wg(peer_public_key, allowed_ips)
        
        if config_success and wg_success:
            return jsonify({
                'status': 'success',
                'message': f'Peer added successfully',
                'peer_public_key': peer_public_key,
                'allowed_ips': allowed_ips
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to add peer completely',
                'config_success': config_success,
                'wg_success': wg_success
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error adding peer: {str(e)}'
        }), 500

@app.route('/restart', methods=['GET'])
def restart_wg():
    """Restart WireGuard service"""
    success = restart_wireguard()
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'WireGuard restarted successfully'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to restart WireGuard'
        }), 500

@app.route('/reload', methods=['GET'])
def reload_config():
    """Reload WireGuard configuration"""
    success = reload_wireguard_config()
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'WireGuard configuration reloaded successfully'
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to reload WireGuard configuration'
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic info"""
    return jsonify({
        'service': 'WireGuard Status Server',
        'endpoints': {
            'health': '/health',
            'status': '/status', 
            'public_key': '/public-key',
            'private_key': '/private-key',
            'keys': '/keys',
            'generate_keys': '/generate-keys (POST)',
            'add_peer': '/add-peer (POST)',
            'restart': '/restart (POST)',
            'reload': '/reload (POST)'
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 