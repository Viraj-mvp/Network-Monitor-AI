import psutil
import time

_prev_data = {}

def get_interfaces_bandwidth_mbps():
    """
    Returns:
    {
      'eth0':   {'in': x, 'out': y},
      'wlan0':  {'in': x, 'out': y}
    }
    Values are RAW floats (no rounding).
    """
    global _prev_data

    stats = psutil.net_io_counters(pernic=True)
    current_time = time.time()
    results = {}

    for iface, data in stats.items():

        # ignore loopback
        if iface.lower() == "lo":
            continue

        recv = data.bytes_recv
        sent = data.bytes_sent

        # first time init
        if iface not in _prev_data:
            _prev_data[iface] = {
                "recv": recv,
                "sent": sent,
                "time": current_time
            }
            results[iface] = {"in": 0.0, "out": 0.0}
            continue

        prev = _prev_data[iface]
        time_diff = current_time - prev["time"]

        if time_diff <= 0:
            continue

        # ❗ NO ROUNDING HERE (MOST IMPORTANT FIX)
        in_mbps = ((recv - prev["recv"]) * 8) / (time_diff * 1024 * 1024)
        out_mbps = ((sent - prev["sent"]) * 8) / (time_diff * 1024 * 1024)

        # safety: negative noise avoid
        if in_mbps < 0:
            in_mbps = 0.0
        if out_mbps < 0:
            out_mbps = 0.0

        results[iface] = {
            "in": in_mbps,
            "out": out_mbps
        }

        _prev_data[iface] = {
            "recv": recv,
            "sent": sent,
            "time": current_time
        }

    return results
