import time
import csv
import os
from datetime import datetime

from network_monitor import get_interfaces_bandwidth_mbps
from ai_engine import InterfaceThresholdDetector
from email_alert import send_email_alert

# ---------- CONFIG ----------
INTERVAL = 5
LOG_FILE = "bandwidth_log.csv"
EMAIL_COOLDOWN = 60

THRESHOLDS = {
    "wifi": {
        "in": 1.0,
        "out": 0.5
    },
    "ethernet": {
        "in": 5.0,
        "out": 2.0
    },
    "other": {
        "in": 10.0,
        "out": 5.0
    }
}
# ----------------------------

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

print("✅ Network AI Monitor started")
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

        # 🟢 FIRST 2 CYCLES: FORCE LOG (psutil warm-up fix)
        if cycle_count > 2:
            # 🧹 FILTER: true idle interfaces only
            if inbound == 0.0 and outbound == 0.0:
                continue

        status = detector.predict(iface, inbound, outbound)

        print(
            f"{timestamp} | {iface} | "
            f"In: {inbound:.6f} Mbps | "
            f"Out: {outbound:.6f} Mbps → {status}"
        )

        # ---------- CSV WRITE ----------
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
    str(timestamp),   # 👈 force string
    iface,
    f"{inbound:.8f}",
    f"{outbound:.8f}",
    status
])


        # ---------- EMAIL ALERT ----------
        now = time.time()
        if status != "NORMAL":
            last = last_email_time.get(iface, 0)
            if now - last > EMAIL_COOLDOWN:
                subject = f"⚠️ Network Alert on {iface}"
                message = f"""
Time      : {timestamp}
Interface : {iface}

Inbound   : {inbound:.6f} Mbps
Outbound  : {outbound:.6f} Mbps
Status    : {status}
"""
                send_email_alert(subject, message)
                last_email_time[iface] = now

    time.sleep(INTERVAL)
