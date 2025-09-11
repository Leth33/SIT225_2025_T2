# Python serial logger for Nano 33 IoT gyroscope CSV
# Usage:
#   python serial_logger.py --port COM10 --baud 115200 --outfile gyro_data.csv --minutes 12
# On macOS, port might look like: /dev/cu.usbmodem14101

import argparse, csv, sys, time
from datetime import datetime, timezone
import serial

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", required=True)
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--outfile", default="gyro_data.csv")
    p.add_argument("--minutes", type=float, default=12.0, help="how long to log")
    args = p.parse_args()

    ser = serial.Serial(args.port, args.baud, timeout=1)
    # Give board a moment
    time.sleep(2.0)

    start = time.time()
    end = start + args.minutes * 60.0

    with open(args.outfile, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "x", "y", "z"])
        print(f"Logging to {args.outfile} for {args.minutes} minutes...")
        while time.time() < end:
            line = ser.readline().decode(errors="ignore").strip()
            if not line or line.startswith("time"):
                continue
            parts = line.split(",")
            if len(parts) != 4:
                continue
            try:
                # Convert ms_since_start to an ISO time relative to now
                ms_since = float(parts[0])
                timestamp = datetime.now(timezone.utc)
                x = float(parts[1]); y = float(parts[2]); z = float(parts[3])
            except Exception:
                continue
            w.writerow([timestamp.isoformat(), x, y, z])
            # Optional: print tiny heartbeat
            if int(ms_since) % 1000 < 10:
                sys.stdout.write("."); sys.stdout.flush()

    print("\nDone.")

if __name__ == "__main__":
    main()
