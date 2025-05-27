#!/bin/bash
set -e

# --- Configuration and Environment Variables ---

# The registration server URL (can be overridden by environment variable)
REGISTRATION_URL="${REGISTRATION_URL:-http://localhost:8001}"

# Path to WireGuard config and cache files
WG_CONF_PATH="/etc/wireguard/wg0.conf"
DETAILS_CACHE="/etc/wireguard/registration_details.json"
PRIVATE_KEY_PATH="/etc/wireguard/privatekey"
PUBLIC_KEY_PATH="/etc/wireguard/publickey"

# Optionally, a token for authentication (can be empty)
TOKEN="${TOKEN:-}"

# Check that REGISTRATION_URL is set
if [ -z "$REGISTRATION_URL" ]; then
    echo "Error: REGISTRATION_URL environment variable is required."
    exit 1
fi

# --- WireGuard Key Generation ---

# If private/public key do not exist, generate them (first time registration)
if [ ! -f "$PRIVATE_KEY_PATH" ] || [ ! -f "$PUBLIC_KEY_PATH" ]; then
    echo "WireGuard keypair not found, generating new keys..."
    umask 077
    wg genkey | tee "$PRIVATE_KEY_PATH" | wg pubkey > "$PUBLIC_KEY_PATH"
fi

# Read keys into variables
PRIVATE_KEY=$(cat "$PRIVATE_KEY_PATH")
PUBLIC_KEY=$(cat "$PUBLIC_KEY_PATH")

# --- Helper Functions ---

# Fetch registration details from the server (if already registered)
fetch_details() {
    # This endpoint returns details if already registered
    if [ -n "$TOKEN" ]; then
        curl -s -X GET "$REGISTRATION_URL/details" -H "Authorization: Bearer $TOKEN"
    else
        curl -s -X GET "$REGISTRATION_URL/details"
    fi
}

# Register this client with the server (first time registration)
register_and_get_details() {
    # This endpoint registers the client and returns connection details
    if [ -n "$TOKEN" ]; then
        curl -s -X GET "$REGISTRATION_URL/register/$PUBLIC_KEY" -H "Authorization: Bearer $TOKEN"
    else
        curl -s -X GET "$REGISTRATION_URL/register/$PUBLIC_KEY"
    fi
}

# Extract a field from a JSON string (very simple, not robust for nested JSON)
get_field() {
    echo "$1" | grep -o "\"$2\":\"[^\"]*" | grep -o '[^"]*$'
}

# --- Main Logic ---

# If we already have a valid config and cached details, just use them
if [ -f "$WG_CONF_PATH" ] && [ -f "$DETAILS_CACHE" ]; then
    echo "Existing VPN configuration found. Using cached details and config."
    RESPONSE=$(cat "$DETAILS_CACHE")
else
    # Try to fetch details from the server (may succeed if already registered)
    echo "No valid config found. Checking if already registered with VPN server..."
    RESPONSE=$(fetch_details)
    SERVER_PUBLIC_KEY=$(get_field "$RESPONSE" "server_public_key")
    SERVER_ENDPOINT=$(get_field "$RESPONSE" "server_endpoint")
    ALLOWED_IPS=$(get_field "$RESPONSE" "allowed_ips")
    CLIENT_IP=$(get_field "$RESPONSE" "client_ip")

    # If any required field is missing, we are not registered yet
    if [ -z "$SERVER_PUBLIC_KEY" ] || [ -z "$SERVER_ENDPOINT" ] || [ -z "$ALLOWED_IPS" ] || [ -z "$CLIENT_IP" ]; then
        echo "Not registered or missing fields, registering with VPN server now..."
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

    # Save the details for future runs
    echo "$RESPONSE" > "$DETAILS_CACHE"

    # Generate the WireGuard config file
    echo "Generating new WireGuard configuration..."
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

# --- Connect to VPN ---

# Bring up the WireGuard interface
echo "Bringing up WireGuard interface..."
wg-quick up wg0

# Wait for VPN connection to be established (check for handshake)
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

# --- Start Spark Worker ---

# Start the Spark worker process (replace shell with run.sh)
exec /run.sh