#!/usr/bin/env python3
import subprocess
import requests
import json
from flask import Flask, jsonify
import threading
import time

app = Flask(__name__)

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

def check_wg_running():
    """Check if WireGuard is running"""
    try:
        result = subprocess.run(['wg', 'show'], capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
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

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic info"""
    return jsonify({
        'service': 'WireGuard Status Server',
        'endpoints': {
            'health': '/health',
            'status': '/status', 
            'public_key': '/public-key'
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 