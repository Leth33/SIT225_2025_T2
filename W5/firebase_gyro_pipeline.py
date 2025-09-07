import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import requests
import serial

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

def push_firebase(db_url, path, payload, auth=None):
    url = f"{db_url.rstrip('/')}/{path.strip('/')}.json"
    params = {}
    if auth:
        params["auth"] = auth
    r = requests.post(url, params=params, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def get_all_firebase(db_url, path, auth=None):
    url = f"{db_url.rstrip('/')}/{path.strip('/')}.json"
    params = {"print": "pretty"}
    if auth:
        params["auth"] = auth
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def mode_listen(args):
    ser = serial.Serial(args.port, args.baud, timeout=1)
    print(f"[listen] Connected to {args.port} @ {args.baud} baud")
    print(f"[listen] Pushing samples to: {args.db_url}/{args.path}")
    try:
        while True:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue
            if line.startswith("#"):
                print(line)
                continue

            # Expected format from Arduino: ",gx,gy,gz"
            parts = line.split(",")
            if len(parts) != 4:
                try:
                    gx, gy, gz = map(float, parts[-3:])
                except Exception:
                    print(f"[warn] Unexpected line: {line}")
                    continue
            else:
                # parts[0] is empty timestamp field from Arduino
                try:
                    gx, gy, gz = float(parts[1]), float(parts[2]), float(parts[3])
                except Exception:
                    print(f"[warn] Parse fail: {line}")
                    continue

            ts = now_iso()
            sample = {"ts": ts, "gx": gx, "gy": gy, "gz": gz}
            try:
                push_firebase(args.db_url, args.path, sample, auth=args.auth)
                print(f"[ok] {sample}")
            except Exception as e:
                print(f"[error] Firebase push failed: {e}")
            if args.max_samples and args.max_samples > 0:
                args.max_samples -= 1
                if args.max_samples <= 0:
                    print("[listen] Reached max_samples, exiting.")
                    break

    finally:
        ser.close()

def save_csv(samples, csv_path):
    # samples is list of dicts with keys ts, gx, gy, gz
    fieldnames = ["ts", "gx", "gy", "gz"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in samples:
            writer.writerow(s)

def flatten_firebase_tree(tree):
    """Firebase returns a dict keyed by push ids -> sample dicts.
    Return as a list sorted by ts."""
    if not tree:
        return []
    rows = []
    for _, v in tree.items():
        if not isinstance(v, dict):
            continue
        ts = v.get("ts")
        gx = v.get("gx")
        gy = v.get("gy")
        gz = v.get("gz")
        rows.append({"ts": ts, "gx": gx, "gy": gy, "gz": gz})
    rows.sort(key=lambda r: (r["ts"] or ""))
    return rows

def clean_dataframe(df):
    # Drop rows with any NaN or non-convertible values, enforce dtypes
    for col in ["gx", "gy", "gz"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["ts", "gx", "gy", "gz"]).copy()
    after = len(df)
    print(f"[clean] Removed {before - after} invalid rows")
    return df

def mode_export(args):
    print(f"[export] Downloading from {args.db_url}/{args.path}")
    tree = get_all_firebase(args.db_url, args.path, auth=args.auth)
    rows = flatten_firebase_tree(tree)
    if not rows:
        print("[export] No data found.")
        return
    df = pd.DataFrame(rows)
    df = clean_dataframe(df)
    csv_path = Path(args.out)
    df.to_csv(csv_path, index=False)
    print(f"[export] Saved CSV -> {csv_path.resolve()}")

def plot_series(df, out_prefix):
    # Ensure datetime index
    df = df.sort_values("ts").set_index("ts")

    # Plot individual axes
    for axis in ["gx", "gy", "gz"]:
        plt.figure()
        df[axis].plot()
        plt.title(f"Gyroscope {axis} over time")
        plt.xlabel("Time (UTC)")
        plt.ylabel("deg/s")
        png = f"{out_prefix}_{axis}.png"
        plt.tight_layout()
        plt.savefig(png, dpi=150)
        plt.close()
        print(f"[plot] Saved {png}")

    # Combined
    plt.figure()
    df[["gx", "gy", "gz"]].plot()
    plt.title("Gyroscope gx, gy, gz over time")
    plt.xlabel("Time (UTC)")
    plt.ylabel("deg/s")
    png = f"{out_prefix}_combined.png"
    plt.tight_layout()
    plt.savefig(png, dpi=150)
    plt.close()
    print(f"[plot] Saved {png}")

def mode_plot(args):
    df = pd.read_csv(args.csv, parse_dates=["ts"])
    df = clean_dataframe(df)
    out_prefix = Path(args.csv).with_suffix("")
    plot_series(df, str(out_prefix))

def build_parser():
    p = argparse.ArgumentParser(description="SIT225 Week 5 Firebase Gyro Pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_listen = sub.add_parser("listen", help="Read gyro over Serial and push to Firebase")
    p_listen.add_argument("--port", required=True, help="Serial port, e.g. /dev/tty.usbmodem101 or COM5")
    p_listen.add_argument("--baud", type=int, default=115200)
    p_listen.add_argument("--db-url", required=True, help="Firebase Realtime Database URL")
    p_listen.add_argument("--path", default="sessions/session1", help="DB path to push under")
    p_listen.add_argument("--auth", default=None, help="Database secret or ID token (optional)")
    p_listen.add_argument("--max-samples", type=int, default=0, help="Stop after N samples (0 = unlimited)")
    p_listen.set_defaults(func=mode_listen)

    p_export = sub.add_parser("export", help="Download all samples from Firebase and save to CSV")
    p_export.add_argument("--db-url", required=True)
    p_export.add_argument("--path", default="sessions/session1")
    p_export.add_argument("--auth", default=None)
    p_export.add_argument("--out", default="gyro_data.csv")
    p_export.set_defaults(func=mode_export)

    p_plot = sub.add_parser("plot", help="Plot CSV into 4 PNG graphs")
    p_plot.add_argument("--csv", required=True)
    p_plot.set_defaults(func=mode_plot)

    return p

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)