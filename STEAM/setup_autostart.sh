#!/bin/bash
# Setup script for auto-starting STEAM app on boot

set -e

echo "🚀 Setting up STEAM app for auto-start..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run with sudo: sudo bash setup_autostart.sh"
    exit 1
fi

# 1. Enable pigpiod to start on boot
echo "📦 Enabling pigpiod service..."
systemctl enable pigpiod
systemctl start pigpiod

# 2. Copy service file to systemd directory
echo "📝 Installing STEAM service..."
cp steam-app.service /etc/systemd/system/

# 3. Reload systemd to recognize the new service
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# 4. Enable the service to start on boot
echo "✅ Enabling STEAM service..."
systemctl enable steam-app.service

# 5. Start the service immediately
echo "▶️  Starting STEAM service..."
systemctl start steam-app.service

# 6. Show status
echo ""
echo "✨ Setup complete! Checking status..."
systemctl status steam-app.service --no-pager

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Auto-start configured successfully!"
echo ""
echo "Useful commands:"
echo "  • View logs:    sudo journalctl -u steam-app -f"
echo "  • Stop app:     sudo systemctl stop steam-app"
echo "  • Restart app:  sudo systemctl restart steam-app"
echo "  • Disable auto: sudo systemctl disable steam-app"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
