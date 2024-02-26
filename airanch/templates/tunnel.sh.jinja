#!/bin/bash

# Variables (to be filled in by Jinja template)
USERNAME="{{ username }}"
LOCALPORT="{{ local_port }}"
REMOTEPORT="{{ remote_port }}"
REMOTEHOST="{{ remote_host }}"

# Prepare SSH Key
SSHKEYPATH="$HOME/.ssh/generated_key"
SSHKEYPUBPATH="$SSHKEYPATH.pub"
mkdir -p "$HOME/.ssh"

# Generate SSH Key (without passphrase)
ssh-keygen -t rsa -b 2048 -f "$SSHKEYPATH" -q -N ""

# Set permissions
chmod 600 "$SSHKEYPATH"

# Create systemd service file
create_service_file() {
    cat <<EOF > /etc/systemd/system/ssh-tunnel.service
[Unit]
Description=Keep Alive SSH Tunnel for $USERNAME
After=network.target

[Service]
User=$USERNAME
ExecStart=/usr/bin/ssh -NT -o ExitOnForwardFailure=yes -o ServerAliveInterval=60 -o IdentityFile=$SSHKEYPATH -L $LOCALPORT:localhost:$REMOTEPORT $USERNAME@$REMOTEHOST
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
}

# Check for systemd
if ! command -v systemctl &> /dev/null; then
    echo "Systemd does not appear to be installed. Exiting."
    exit 1
fi

# Ensure the script is run as root
if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root. Please use sudo or switch to root."
    exit 1
fi

# Create systemd service file
create_service_file

# Enable and start the service
systemctl enable ssh-tunnel.service
systemctl start ssh-tunnel.service

echo "SSH Tunnel service has been successfully created, enabled, and started."

# Bright red warning for the user
echo -e "\e[91mIMPORTANT: Paste the public key into the database:\e[0m"
cat "$SSHKEYPUBPATH"
