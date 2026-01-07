# Auto-Start Setup Guide

This guide will configure your Raspberry Pi to automatically run the STEAM application on boot.

## Prerequisites

- Raspberry Pi with the project located at `/home/pi/STEAM`
- Virtual environment set up at `/home/pi/STEAM/venv`
- All dependencies installed in the venv

## Quick Setup

### 1. Transfer Files to Raspberry Pi

Copy the entire project directory to your Raspberry Pi at `/home/pi/STEAM`.

### 2. Adjust Paths (if needed)

If your project is **not** at `/home/pi/STEAM`, edit `steam-app.service`:

```bash
nano steam-app.service
```

Update these lines:

- `WorkingDirectory=/home/pi/STEAM` → your actual path
- `ExecStart=/home/pi/STEAM/venv/bin/python /home/pi/STEAM/main.py` → your actual paths

If your username is **not** `pi`, change:

- `User=pi` → your username

### 3. Run Setup Script

On the Raspberry Pi:

```bash
cd /home/pi/STEAM
chmod +x setup_autostart.sh
sudo bash setup_autostart.sh
```

This script will:

1. ✅ Enable `pigpiod` to start on boot
2. ✅ Install the STEAM app service
3. ✅ Enable auto-start on boot
4. ✅ Start the app immediately

## Verification

### Check if running:

```bash
sudo systemctl status steam-app
```

You should see **"Active: active (running)"** in green.

### View live logs:

```bash
sudo journalctl -u steam-app -f
```

Press `Ctrl+C` to stop viewing.

### Test auto-start:

```bash
sudo reboot
```

After reboot, check status again to confirm it started automatically.

## Useful Commands

| Action                   | Command                            |
| ------------------------ | ---------------------------------- |
| **View logs**            | `sudo journalctl -u steam-app -f`  |
| **Stop app**             | `sudo systemctl stop steam-app`    |
| **Start app**            | `sudo systemctl start steam-app`   |
| **Restart app**          | `sudo systemctl restart steam-app` |
| **Disable auto-start**   | `sudo systemctl disable steam-app` |
| **Enable auto-start**    | `sudo systemctl enable steam-app`  |
| **Check pigpiod status** | `sudo systemctl status pigpiod`    |

## Troubleshooting

### App won't start

1. **Check logs for errors:**

   ```bash
   sudo journalctl -u steam-app -n 50
   ```

2. **Verify pigpiod is running:**

   ```bash
   sudo systemctl status pigpiod
   ```

3. **Test manually:**
   ```bash
   cd /home/pi/STEAM
   source venv/bin/activate
   python main.py
   ```

### Permission issues

If you see permission errors, ensure the service runs as the correct user:

```bash
sudo nano /etc/systemd/system/steam-app.service
```

Change `User=pi` to your actual username.

Then reload:

```bash
sudo systemctl daemon-reload
sudo systemctl restart steam-app
```

### Camera not working

Add your user to the `video` group:

```bash
sudo usermod -aG video pi
```

Reboot after making this change.

## What Happens on Boot?

1. **Raspberry Pi powers on** 🔌
2. **pigpiod daemon starts** (for ultrasonic sensor)
3. **STEAM app starts** automatically
4. **Camera and sensor begin monitoring**
5. **Data sends to server** at `194.5.157.250:13869`

All automatic, no SSH required! 🎉
