# Network AI Monitor

**AI-Powered Real-Time Network Traffic Intelligence**

[![Download](https://img.shields.io/github/v/release/Viraj-mvp/Network-Monitor-AI?style=for-the-badge&logo=github)](https://github.com/Viraj-mvp/Network-Monitor-AI/releases/latest)

Monitor • Analyze • Detect • Alert

---

Network AI Monitor is a professional desktop application that provides real-time network traffic monitoring with AI-powered anomaly detection. Simply download, install, and start monitoring your network immediately — no configuration files to edit, no Python to install.

![Dashboard Preview](./assets/dashboard-preview.png)

---

## ✨ Features

- **🔍 Real-Time Monitoring** — Live upload/download tracking for all network interfaces
- **🤖 AI Anomaly Detection** — Automatically detects suspicious traffic patterns
- **📧 Email Alerts** — Get notified instantly when anomalies are detected
- **📊 Live Dashboard** — Beautiful real-time graphs and statistics
- **🌓 Dark/Light Themes** — Choose your preferred appearance
- **🔔 System Tray** — Runs quietly in the background
- **📝 Traffic Logging** — Historical data for analysis

---

## 🚀 Quick Start

### Windows

1. Download `NetworkAIMonitor-Windows.zip` from [Releases](https://github.com/Viraj-mvp/Network-Monitor-AI/releases)
2. Extract the ZIP to any folder
3. Run `NetworkAIMonitor.exe`
4. Complete the setup wizard on first launch
5. Done! Monitoring starts automatically

### macOS

1. Download `NetworkAIMonitor-macOS.tar.gz` from [Releases](https://github.com/Viraj-mvp/Network-Monitor-AI/releases)
2. Extract the archive: `tar -xzf NetworkAIMonitor-macOS.tar.gz`
3. Open `NetworkAIMonitor.app`
4. Complete the setup wizard on first launch
5. Done! Monitoring starts automatically

### Linux

1. Download `NetworkAIMonitor-Linux.tar.gz` from [Releases](https://github.com/Viraj-mvp/Network-Monitor-AI/releases)
2. Extract the archive: `tar -xzf NetworkAIMonitor-Linux.tar.gz`
3. Run: `./NetworkAIMonitor-Linux/NetworkAIMonitor`
4. Complete the setup wizard on first launch
5. Done! Monitoring starts automatically

---

## 📖 User Guide

### First Launch Setup

When you first open Network AI Monitor, a setup wizard will guide you through:

1. **Monitoring Preferences** — Select which network interface to monitor and set your traffic thresholds
2. **Email Alerts** (Optional) — Configure Gmail notifications for instant anomaly alerts
3. **Appearance** — Choose dark/light theme and startup behavior
4. **Ready!** — Start monitoring immediately

All settings are saved automatically and persist between sessions.

### Using the Dashboard

- **Start/Stop Monitoring** — Use the toolbar buttons or system tray menu
- **View Traffic** — See real-time bandwidth for each network interface
- **Check Alerts** — View detected anomalies in the Alerts tab
- **Review Logs** — Access historical data in the Logs tab
- **Change Settings** — Modify any setting from the Settings tab

### System Tray

Network AI Monitor runs in your system tray for continuous monitoring:

- **Double-click** the tray icon to show/hide the dashboard
- **Right-click** for quick actions (start/stop, settings, exit)
- **Minimize to tray** — The app keeps monitoring even when hidden

---

## ⚙️ Email Alerts Setup

To receive email notifications for network anomalies:

1. Go to **Settings** → **Email Alerts**
2. Enable "Email Alerts"
3. Enter your **Gmail address**
4. Enter your **Gmail App Password** (not your regular password)
5. Specify the **receiver email** (can be the same as sender)
6. Click **Test Email** to verify
7. Click **Save Settings**

**Creating a Gmail App Password:**
1. Go to [Google Account Settings](https://myaccount.google.com/security)
2. Enable 2-Step Verification if not already enabled
3. Go to "App passwords" under 2-Step Verification
4. Generate a new app password for "Mail"
5. Copy the 16-character password to Network AI Monitor

---

## 🖥️ System Requirements

| Platform | Minimum | Recommended |
|----------|---------|-------------|
| Windows | Windows 10 | Windows 11 |
| macOS | macOS 11 (Big Sur) | macOS 14 (Sonoma) |
| Linux | Ubuntu 20.04 / Fedora 34 | Latest LTS |
| RAM | 4 GB | 8 GB |
| Storage | 200 MB | 500 MB |
| Network | Any interface | WiFi or Ethernet |

---

## 🆘 Troubleshooting

### App won't start
- **Windows**: Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- **macOS**: Right-click app → Open (bypass Gatekeeper for first launch)
- **Linux**: Install Qt dependencies: `sudo apt install libgl1 libxkbcommon-x11-0`

### No network interfaces shown
- Run the app as administrator/root (required for network monitoring)
- Check firewall settings (app needs network access)

### Email alerts not working
- Verify Gmail App Password is correct (not your regular password)
- Enable "Less secure app access" is **not** required for App Passwords
- Check spam folders for test emails
- Use the "Test Email" button in settings to diagnose issues

### High CPU usage
- Increase the monitoring interval in Settings (try 5-10 seconds)
- Reduce the number of monitored interfaces

---

## 🔒 Security & Privacy

- **Local Only** — All data stays on your computer
- **Encrypted Credentials** — Email passwords stored in OS keyring
- **No External Connections** — App only connects to Gmail SMTP (if configured)
- **No Telemetry** — We don't collect any usage data

**Configuration Storage:**
- Windows: `%LOCALAPPDATA%\NetworkAIMonitor\`
- macOS: `~/Library/Application Support/NetworkAIMonitor/`
- Linux: `~/.config/NetworkAIMonitor/`

---

## 📦 What's Included

Each release package contains:

- `NetworkAIMonitor` — Main executable
- `_internal/` — Runtime dependencies (auto-managed)
- No Python installation required
- No additional downloads needed

---

## 🔄 Updates

Network AI Monitor checks for updates automatically. When a new version is available:

1. You'll see a notification in the dashboard
2. Click the download link in the notification
3. Download the new version
4. Replace your existing installation
5. Your settings are preserved

---

## 📄 License

MIT License — See [LICENSE](LICENSE) file for details.

---

## 🤝 Support

- **Issues & Bugs**: [GitHub Issues](https://github.com/Viraj-mvp/Network-Monitor-AI/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/Viraj-mvp/Network-Monitor-AI/discussions)

---

<p align="center">
  <b>Download → Open → Monitor. It's that simple.</b>
</p>
