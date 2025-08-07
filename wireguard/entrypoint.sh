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

# Create config
cat > /etc/wireguard/$WG_INTERFACE.conf << EOF
[Interface]
Address = $WG_SERVER_IP
ListenPort = $WG_PORT
PrivateKey = $(cat /etc/wireguard/server_private.key)

EOF

# Add peers
for peer in /etc/wireguard/peers/*.conf 2>/dev/null; do
    [[ -f "$peer" ]] && cat "$peer" >> /etc/wireguard/$WG_INTERFACE.conf
done

# Enable forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# Setup NAT
if [[ "$WG_ENABLE_NAT" == "true" ]]; then
    iptables -t nat -A POSTROUTING -s $WG_SUBNET -j MASQUERADE
    iptables -A FORWARD -i $WG_INTERFACE -j ACCEPT
    iptables -A FORWARD -o $WG_INTERFACE -j ACCEPT
fi

# Start WireGuard
wg-quick up $WG_INTERFACE

echo "WireGuard server started"
echo "Public key: $(cat /etc/wireguard/server_public.key)"

# Cleanup on exit
trap "wg-quick down $WG_INTERFACE || true" EXIT

# Keep alive
while true; do
    sleep 3600
    wg show $WG_INTERFACE > /dev/null || exit 1
done