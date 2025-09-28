import argparse, csv, datetime as dt, time
import serial
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--out", default="deskcoach_session.csv")
    args = ap.parse_args()

    out = Path(args.out)
    print(f"Logging from {args.port} @ {args.baud} -> {out.resolve()}")
    
    # Write header first
    with out.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp_iso", "temp_c", "hum_pct", "pitch_deg"])
    
    with serial.Serial(args.port, args.baud, timeout=1) as ser, out.open("a", newline="") as f:
        writer = csv.writer(f)
        try:
            while True:
                try:
                    line = ser.readline().decode(errors="ignore").strip()
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) >= 4:
                        # Replace first column (timestamp) with current ISO timestamp
                        parts[0] = dt.datetime.now().isoformat()
                        writer.writerow(parts)
                        f.flush()  # Ensure data is written immediately
                        print(line)
                except Exception as e:
                    print(f"Error reading line: {e}")
                    continue
        except KeyboardInterrupt:
            pass
    print("Saved:", out)

if __name__ == "__main__":
    main()
