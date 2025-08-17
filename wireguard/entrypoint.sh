#!/bin/sh
set -euo pipefail

# Defaults
WG_INTERFACE=${WG_INTERFACE:-wg0}
WG_PORT=${WG_PORT:-51820}
WG_SERVER_IP=${WG_SERVER_IP:-10.10.0.1/24}
WG_SUBNET=${WG_SUBNET:-10.10.0.0/24}
WG_ENABLE_NAT=${WG_ENABLE_NAT:-true}

mkdir -p /etc/wireguard

# Generate keys if missing
if [ ! -f /etc/wireguard/server_private.key ]; then
    umask 077
    wg genkey > /etc/wireguard/server_private.key
    wg pubkey < /etc/wireguard/server_private.key > /etc/wireguard/server_public.key
    echo "Generated server keys"
fi

# Create config with NAT and routing rules
cat > /etc/wireguard/$WG_INTERFACE.conf << EOF
[Interface]
Address = $WG_SERVER_IP
ListenPort = $WG_PORT
PrivateKey = $(cat /etc/wireguard/server_private.key)
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth+ -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth+ -j MASQUERADE

EOF

# Start WireGuard
wg-quick up $WG_INTERFACE

echo "WireGuard server started"
echo "Public key: $(cat /etc/wireguard/server_public.key)"

# Debug: Check if files exist
echo "Checking for app.py..."
if [ ! -f /app.py ]; then
    echo "ERROR: /app.py not found!"
    exit 1
fi

# Debug: Check Python and virtual environment
echo "Checking Python environment..."
python3 --version
which python3
echo "PATH: $PATH"

# Test Flask import
echo "Testing Flask import..."
python3 -c "import flask; print(f'Flask available')" || {
    echo "Flask import failed!"
    python3 -c "import sys; print('Python path:', sys.path)"
    pip list | grep -i flask || echo "Flask not in pip list"
    exit 1
}

# Start Flask server in background with detailed logging
echo "Starting Flask server..."
python3 /app.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    if [ -f /tmp/flask.log ]; then
        echo "=== Flask log output ==="
        cat /tmp/flask.log
        echo "======================="
    fi
    kill $FLASK_PID 2>/dev/null || true
    wg-quick down $WG_INTERFACE 2>/dev/null || true
    exit 0
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Wait for Flask to start with more patience
echo "Waiting for Flask to start..."
sleep 3

# Check if Flask process is still running
if ! kill -0 $FLASK_PID 2>/dev/null; then
    echo "Flask process died! Logs:"
    cat /tmp/flask.log 2>/dev/null || echo "No log file found"
    exit 1
fi

# Check if Flask is responding with retries
echo "Testing Flask health endpoint..."
FLASK_READY=false
for i in $(seq 1 15); do
    if curl -f --connect-timeout 2 http://localhost:5000/health >/dev/null 2>&1; then
        echo "Flask server started successfully on port 5000"
        FLASK_READY=true
        break
    fi
    echo "Attempt $i: Flask not ready yet..."
    
    # Check if process is still alive
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        echo "Flask process died during startup! Logs:"
        cat /tmp/flask.log 2>/dev/null || echo "No log file found"
        exit 1
    fi
    
    sleep 2
done

if [ "$FLASK_READY" = false ]; then
    echo "Flask server failed to respond after 30 seconds"
    echo "=== Flask logs ==="
    cat /tmp/flask.log 2>/dev/null || echo "No log file found"
    echo "=================="
    
    # Additional debugging
    echo "=== Network info ==="
    netstat -tlnp 2>/dev/null | grep :5000 || echo "Port 5000 not listening"
    echo "==================="
    exit 1
fi

echo "All services started successfully!"

# Keep alive and monitor both services
while true; do
    # Check WireGuard
    if ! wg show $WG_INTERFACE >/dev/null 2>&1; then
        echo "WireGuard interface down, exiting"
        exit 1
    fi
    
    # Check Flask
    if ! curl -f --connect-timeout 2 http://localhost:5000/health >/dev/null 2>&1; then
        echo "Flask server health check failed, exiting"
        exit 1
    fi
    
    sleep 60
done