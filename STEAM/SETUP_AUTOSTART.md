# Auto-Start Setup - Quick Guide

## Prerequisites

Ensure your Raspberry Pi has:

- Project files at `/home/pi/STEAM`
- Virtual environment at `/home/pi/STEAM/venv`
- All dependencies installed in venv

## Installation Steps

### 1. Install pigpio (if not already installed)

```bash
sudo apt-get update
sudo apt-get install pigpio -y
```

### 2. Adjust Paths (if needed)

If your project is **not** at `/home/pi/STEAM` or your username is **not** `pi`:

```bash
nano steam-app.service
```

Update these lines:

- `User=pi` → your username
- `WorkingDirectory=/home/pi/STEAM` → your project path
- `ExecStart=/home/pi/STEAM/venv/bin/python /home/pi/STEAM/main.py` → your paths

### 3. Run Setup Script

```bash
cd /home/pi/STEAM
chmod +x setup_autostart.sh
sudo bash setup_autostart.sh
```

### 4. Verify It's Running

```bash
sudo systemctl status steam-app
```

You should see: **"Active: active (running)"** ✅

### 5. Test Auto-Start

```bash
sudo reboot
```

After reboot, check status again to confirm it started automatically.

---

## Useful Commands

**View live logs:**

```bash
sudo journalctl -u steam-app -f
```

**Restart the app:**

```bash
sudo systemctl restart steam-app
```

**Stop the app:**

```bash
sudo systemctl stop steam-app
```

**Disable auto-start:**

```bash
sudo systemctl disable steam-app
```

---

## Done! 🎉

Your Raspberry Pi will now automatically run the STEAM app every time it boots.
