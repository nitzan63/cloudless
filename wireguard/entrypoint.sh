#!/bin/bash
set -euo pipefail

# Defaults
WG_INTERFACE=${WG_INTERFACE:-wg0}
WG_PORT=${WG_PORT:-51820}
WG_SERVER_IP=${WG_SERVER_IP:-10.10.0.1/24}
WG_SUBNET=${WG_SUBNET:-10.10.0.0/24}
WG_ENABLE_NAT=${WG_ENABLE_NAT:-true}

mkdir -p /etc/wireguard

# Generate keys if missing
if [[ ! -f /etc/wireguard/server_private.key ]]; then
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

[Peer]
PublicKey = 3tDI2t6P+36nKTLNtbOm4kEM3WqwPvPk9ySQE/2VlQc=
AllowedIPs = 10.10.0.2/32

EOF

# Start WireGuard
wg-quick up $WG_INTERFACE

echo "WireGuard server started"
echo "Public key: $(cat /etc/wireguard/server_public.key)"

# Start Flask server in background
echo "Starting Flask server..."
python3 /app.py &
FLASK_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $FLASK_PID 2>/dev/null || true
    wg-quick down $WG_INTERFACE 2>/dev/null || true
    exit 0
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

# Wait for Flask to start
sleep 2

# Check if Flask is running
if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "Flask server failed to start"
    exit 1
fi

echo "Flask server started successfully on port 5000"

# Keep alive and monitor both services
while true; do
    # Check WireGuard
    if ! wg show $WG_INTERFACE > /dev/null 2>&1; then
        echo "WireGuard interface down, exiting"
        exit 1
    fi
    
    # Check Flask
    if ! curl -f http://localhost:5000/health > /dev/null 2>&1; then
        echo "Flask server down, exiting"
        exit 1
    fi
    
    sleep 60
done