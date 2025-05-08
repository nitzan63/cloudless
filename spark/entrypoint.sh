#!/bin/bash
set -e

# Use env vars
REGISTRATION_URL="${REGISTRATION_URL:-http://vpn-server:5000}"

if [ -z "$REGISTRATION_URL" ]; then
echo "Error: REGISTRATION_URL environment variable is required."
exit 1
fi

# Generate WireGuard keypair if not present

if [ ! -f /etc/wireguard/privatekey ]; then
umask 077
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey
fi

PRIVATE_KEY=$(cat /etc/wireguard/privatekey)
PUBLIC_KEY=$(cat /etc/wireguard/publickey)

# Register with the VPN registration server

echo "Registering keys with VPN server..."
RESPONSE=$(curl -s -X POST "$REGISTRATION_URL/register" \
 -H "Content-Type: application/json" \
 -d "{\"private_key\": \"$PRIVATE_KEY\", \"public_key\": \"$PUBLIC_KEY\"}")

SERVER_PUBLIC_KEY=$(echo "$RESPONSE" | grep -o '"server_public_key":"[^"]*' | grep -o '[^"]*$')
SERVER_ENDPOINT=$(echo "$RESPONSE" | grep -o '"server_endpoint":"[^"]*' | grep -o '[^"]*$')
ALLOWED_IPS=$(echo "$RESPONSE" | grep -o '"allowed_ips":"[^"]*' | grep -o '[^"]*$')
CLIENT_IP=$(echo "$RESPONSE" | grep -o '"client_ip":"[^"]*' | grep -o '[^"]*$')

if [ -z "$SERVER_PUBLIC_KEY" ] || [ -z "$SERVER_ENDPOINT" ] || [ -z "$ALLOWED_IPS" ] || [ -z "$CLIENT_IP" ]; then
echo "Registration failed or missing fields in server response: $RESPONSE"
exit 1
fi

# Create wg0.conf

cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
PrivateKey = $PRIVATE_KEY
Address = $CLIENT_IP/32
DNS = 8.8.8.8

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $SERVER_ENDPOINT
AllowedIPs = $ALLOWED_IPS/32
PersistentKeepalive = 25
EOF

echo "wg0.conf generated:"
cat /etc/wireguard/wg0.conf

# Start WireGuard
wg-quick up wg0

# Wait for VPN connection to be established
echo "Waiting for VPN connection to be established..."
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if wg show wg0 | grep -q "latest handshake"; then
        echo "VPN connection established successfully"
        break
    fi
    echo "Attempt $attempt/$max_attempts: Waiting for VPN connection..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    echo "Failed to establish VPN connection after $max_attempts attempts"
    exit 1
fi

# Start Spark worker
exec /run.sh