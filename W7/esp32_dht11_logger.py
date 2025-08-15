import argparse, csv, sys, time
from datetime import datetime

try:
    import serial
except ImportError:
    print("pyserial is required. Install with: pip install pyserial")
    sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True, help="Serial port path, e.g. COM5 or /dev/ttyUSB0")
    ap.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    ap.add_argument("--out", default="sensor_data.csv", help="Output CSV filename")
    args = ap.parse_args()

    ser = serial.Serial(args.port, args.baud, timeout=2)
    print(f"Reading from {args.port} at {args.baud} baud. Writing to {args.out}")

    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temperature_C", "humidity_pct"])
        try:
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                parts = [p.strip() for p in line.split(",")]
                if len(parts) != 3:
                    # If the board prints only temp/hum, add timestamp here
                    if len(parts) == 2:
                        ts = datetime.now().isoformat(timespec="seconds")
                        parts = [ts] + parts
                    else:
                        print("Skipping malformed line:", line)
                        continue
                writer.writerow(parts)
                f.flush()
                print("logged:", parts)
        except KeyboardInterrupt:
            print("\\nStopped.")

if __name__ == "__main__":
    main()
