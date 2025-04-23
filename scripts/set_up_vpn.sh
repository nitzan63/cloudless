#!/bin/bash

echo "Installing WireGuard..."
sudo apt update
sudo apt install -y wireguard

echo "Generating server keys..."
umask 077
wg genkey | tee server_private.key | wg pubkey > server_public.key

echo "Creating WireGuard config file at /etc/wireguard/wg0.conf..."
sudo bash -c 'cat > /etc/wireguard/wg0.conf <<EOF
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = $(cat server_private.key)
EOF'

echo "Enabling IP forwarding..."
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

echo "Configuring Google Cloud Firewall (manual step)..."
echo "Please create a rule to allow UDP traffic on port 51820 in your GCP console."

echo "Starting WireGuard..."
sudo wg-quick up wg0

echo "Enabling WireGuard to start on boot..."
sudo systemctl enable wg-quick@wg0

echo "Checking WireGuard status..."
sudo wg show

echo "To restart WireGuard after config changes, use:"
echo "  sudo wg-quick down wg0 && sudo wg-quick up wg0"

echo "WireGuard VPN server setup complete!"
