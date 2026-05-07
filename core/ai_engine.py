class InterfaceThresholdDetector:
    def __init__(self, thresholds):
        """
        thresholds = {
          'eth0':  {'in': 5.0, 'out': 2.0},
          'wlan0': {'in': 1.0, 'out': 0.5}
        }
        """
        self.thresholds = thresholds

    def predict(self, iface, inbound, outbound):
        if iface not in self.thresholds:
            return "NORMAL"

        th = self.thresholds[iface]

        if inbound >= th["in"]:
            return "ANOMALY_INBOUND"

        if outbound >= th["out"]:
            return "ANOMALY_OUTBOUND"

        return "NORMAL"

