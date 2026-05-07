import time
import csv
import os
import json
from datetime import datetime

from network_monitor import get_interfaces_bandwidth_mbps
from ai_engine import InterfaceThresholdDetector
from email_alert import send_email_alert

# ================= CONFIG =================
INTERVAL = 5
LOG_FILE = "bandwidth_log.csv"
EMAIL_COOLDOWN = 60

DEFAULT_THRESHOLDS = {
    "wifi": {"in": 1.0, "out": 0.5},
    "ethernet": {"in": 5.0, "out": 2.0},
    "other": {"in": 1.0, "out": 1.0}
}
# ==========================================

def load_config():
    """Load settings from settings.json if it exists, otherwise use defaults"""
    settings_file = os.path.join(os.path.dirname(__file__), "..", "settings.json")
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                thresholds = settings.get("thresholds", {})
                # Map UI names to CLI names
                mapped = {
                    "wifi": thresholds.get("WiFi", DEFAULT_THRESHOLDS["wifi"]),
                    "ethernet": thresholds.get("Ethernet", DEFAULT_THRESHOLDS["ethernet"]),
                    "other": DEFAULT_THRESHOLDS["other"]
                }
                return mapped
        except Exception:
            pass
    return DEFAULT_THRESHOLDS

def normalize_interface_name(iface):
    name = iface.lower()
    if "wi" in name or "wlan" in name:
        return "wifi"
    if "eth" in name:
        return "ethernet"
    return "other"

THRESHOLDS = load_config()
detector = InterfaceThresholdDetector(THRESHOLDS)
last_email_time = {}

# ---------- CSV SETUP ----------
file_exists = os.path.isfile(LOG_FILE)
with open(LOG_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow([
            "timestamp",
            "interface",
            "inbound_mbps",
            "outbound_mbps",
            "status"
        ])

print("✅ Network AI Monitor STARTED")
print("-" * 60)

cycle_count = 0

# ---------- MAIN LOOP ----------
while True:
    cycle_count += 1

    data = get_interfaces_bandwidth_mbps()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for iface, bw in data.items():
        inbound = bw["in"]
        outbound = bw["out"]

        if cycle_count > 2:
            if inbound == 0.0 and outbound == 0.0:
                continue

        mapped_iface = normalize_interface_name(iface)
        status = detector.predict(mapped_iface, inbound, outbound)

        print(
            f"{timestamp} | {iface} ({mapped_iface}) | "
            f"In: {inbound:.6f} | Out: {outbound:.6f} → {status}"
        )

        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                iface,
                f"{inbound:.8f}",
                f"{outbound:.8f}",
                status
            ])

        now = time.time()
        if status != "NORMAL":
            last = last_email_time.get(mapped_iface, 0)
            if now - last > EMAIL_COOLDOWN:
                send_email_alert(
                    f"⚠️ Network Alert on {iface}",
                    f"""
Time      : {timestamp}
Interface : {iface}

Inbound   : {inbound:.6f} Mbps
Outbound  : {outbound:.6f} Mbps
Status    : {status}
"""
                )
                last_email_time[mapped_iface] = now

    time.sleep(INTERVAL)
