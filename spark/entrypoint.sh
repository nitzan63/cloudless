#!/bin/bash
set -e

# Use env vars
REGISTRATION_URL="${REGISTRATION_URL:-http://localhost:8001}"

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

WG_CONF_PATH="/etc/wireguard/wg0.conf"
DETAILS_CACHE="/etc/wireguard/registration_details.json"

fetch_details() {
    # Try to fetch details using GET (assuming GET /register/<public_key>)
    RESPONSE=$(curl -s -X GET "$REGISTRATION_URL/details" \
        -H "Authorization: Bearer $TOKEN")
    echo "$RESPONSE"
}

register_and_get_details() {
    # Register with the VPN registration server using POST
    RESPONSE=$(curl -s -X GET "$REGISTRATION_URL/register/$PUBLIC_KEY" \
        -H "Authorization: Bearer $TOKEN")
    echo "$RESPONSE"
}

get_field() {
    echo "$1" | grep -o "\"$2\":\"[^\"]*" | grep -o '[^"]*$'
}

# If we already have a wg0.conf and registration details, try to reuse them
if [ -f "$WG_CONF_PATH" ] && [ -f "$DETAILS_CACHE" ]; then
    echo "Existing VPN configuration found. Verifying connection details..."
    RESPONSE=$(cat "$DETAILS_CACHE")
    # Optionally, you could re-fetch details to ensure they're still valid
    # RESPONSE=$(fetch_details)
else
    # Try to fetch details (if already registered)
    RESPONSE=$(fetch_details)
    SERVER_PUBLIC_KEY=$(get_field "$RESPONSE" "server_public_key")
    SERVER_ENDPOINT=$(get_field "$RESPONSE" "server_endpoint")
    ALLOWED_IPS=$(get_field "$RESPONSE" "allowed_ips")
    CLIENT_IP=$(get_field "$RESPONSE" "client_ip")

    if [ -z "$SERVER_PUBLIC_KEY" ] || [ -z "$SERVER_ENDPOINT" ] || [ -z "$ALLOWED_IPS" ] || [ -z "$CLIENT_IP" ]; then
        echo "Not registered or missing fields, registering now..."
        RESPONSE=$(register_and_get_details)
        SERVER_PUBLIC_KEY=$(get_field "$RESPONSE" "server_public_key")
        SERVER_ENDPOINT=$(get_field "$RESPONSE" "server_endpoint")
        ALLOWED_IPS=$(get_field "$RESPONSE" "allowed_ips")
        CLIENT_IP=$(get_field "$RESPONSE" "client_ip")
        if [ -z "$SERVER_PUBLIC_KEY" ] || [ -z "$SERVER_ENDPOINT" ] || [ -z "$ALLOWED_IPS" ] || [ -z "$CLIENT_IP" ]; then
            echo "Registration failed or missing fields in server response: $RESPONSE"
            exit 1
        fi
    fi

    # Save details for future runs
    echo "$RESPONSE" > "$DETAILS_CACHE"

    # Create wg0.conf
    cat > "$WG_CONF_PATH" <<EOF
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
    cat "$WG_CONF_PATH"
fi

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