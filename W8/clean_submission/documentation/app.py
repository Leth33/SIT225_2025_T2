# week8_app.py
# SIT225 Week 8 — Phone Accelerometer → Plotly Dash (live updates + buffers)
# Mode: SIMULATION by default; switch to LIVE once you have Arduino IoT Cloud creds.
#
# How it works:
# - Collects continuous (x,y,z,timestamp) samples into buffer_a.
# - Every N samples (e.g., 1000), it copies a window to buffer_b and updates graphs.
# - Each refresh also saves a PNG graph and a CSV with a timestamped filename.
#
# Requirements:
#   pip install dash plotly pandas numpy
#
# Usage:
#   python week8_app.py
#   (Then open the printed local URL in your browser)
#
# To use LIVE mode later:
#   1) Fill the TODO section in get_live_sample() to fetch from Arduino IoT Cloud.
#   2) Set SIM_MODE = False.

import os, time, random, math
from collections import deque
from datetime import datetime
import numpy as np
import pandas as pd

from dash import Dash, dcc, html, Output, Input
import plotly.graph_objects as go

# ------------- Config -------------
SIM_MODE = False         # Live mode: fetch data from Arduino IoT Cloud
SAMPLE_RATE_HZ = 20      # ~20 samples/sec
N_WINDOW = 1000          # Number of samples per saved/refresh window (~50 sec @ 20 Hz)
SAVE_DIR = os.path.join(os.path.dirname(__file__), "graphs")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Buffers
buffer_a = deque(maxlen=10_000)   # continuously receives data
buffer_b = []                     # copy window from A to B for plotting/saving

# ------------- Data Sources -------------
def get_live_sample():
    """Fetch live data from Arduino IoT Cloud.
    Return a single (timestamp, x, y, z) tuple.
    """
    try:
        # Import Arduino IoT Cloud client
        from arduino_iot_cloud import ArduinoCloudClient
        from arduino_config import (
            ARDUINO_DEVICE_ID, ARDUINO_THING_ID, DEVICE_KEY,
            ACCEL_X_VARIABLE, ACCEL_Y_VARIABLE, ACCEL_Z_VARIABLE
        )
        
        # Check if credentials are configured
        if (ARDUINO_DEVICE_ID == "your_device_id_here" or
            ARDUINO_THING_ID == "your_thing_id_here"):
            print("⚠️  Arduino IoT Cloud credentials not configured. Using simulation mode.")
            raise Exception("Credentials not configured")
        
        # Create Arduino IoT Cloud client using device key
        client = ArduinoCloudClient(
            device_id=ARDUINO_DEVICE_ID,
            username=ARDUINO_CLIENT_ID,
            password=ARDUINO_CLIENT_SECRET
        )
        
        # Fetch accelerometer data
        x = client.get_variable(ACCEL_X_VARIABLE)
        y = client.get_variable(ACCEL_Y_VARIABLE)
        z = client.get_variable(ACCEL_Z_VARIABLE)
        
        print(f"📡 Live data: x={x:.3f}, y={y:.3f}, z={z:.3f}")
        return (datetime.now(), x, y, z)
        
    except ImportError:
        print("❌ Arduino IoT Cloud client not installed. Run: pip install arduino-iot-cloud")
        raise Exception("Arduino IoT Cloud client not available")
        
    except Exception as e:
        print(f"❌ Error fetching live data: {e}")
        print("🔄 Falling back to simulation mode...")
        # Fallback to simulated data
        import random
        x = random.gauss(0, 0.1)
        y = random.gauss(0, 0.1)
        z = random.gauss(1, 0.1)
        return (datetime.now(), x, y, z)

# Simple activity simulator: walk, jog, jump, idle segments with distinct patterns
class ActivitySim:
    def __init__(self, seed=42):
        random.seed(seed)
        self.t = 0.0
        self.activity = "idle"
        self.segment_end = 0
        self._schedule_next()

    def _schedule_next(self):
        self.activity = random.choice(["idle", "walk", "jog", "jump"])
        dur = {"idle": 6, "walk": 10, "jog": 8, "jump": 5}[self.activity]
        self.segment_end = self.t + dur

    def step(self, dt=1.0/SAMPLE_RATE_HZ):
        # Base gravity on z
        ax, ay, az = 0.0, 0.0, 1.0  # g units-ish
        if self.t >= self.segment_end:
            self._schedule_next()

        if self.activity == "idle":
            # small noise
            ax += random.gauss(0, 0.01)
            ay += random.gauss(0, 0.01)
            az += random.gauss(0, 0.01)
        elif self.activity == "walk":
            freq = 1.8
            ax += 0.15 * math.sin(2*math.pi*freq*self.t) + random.gauss(0, 0.02)
            ay += 0.10 * math.cos(2*math.pi*freq*self.t) + random.gauss(0, 0.02)
            az += 0.08 * math.sin(2*math.pi*freq*self.t + 0.7) + random.gauss(0, 0.02)
        elif self.activity == "jog":
            freq = 3.0
            ax += 0.35 * math.sin(2*math.pi*freq*self.t) + random.gauss(0, 0.03)
            ay += 0.25 * math.cos(2*math.pi*freq*self.t) + random.gauss(0, 0.03)
            az += 0.20 * math.sin(2*math.pi*freq*self.t + 0.5) + random.gauss(0, 0.03)
        elif self.activity == "jump":
            # spikes on z
            if int(self.t * 2) % 3 == 0:
                az += 0.8 + random.gauss(0, 0.05)
            ax += random.gauss(0, 0.05)
            ay += random.gauss(0, 0.05)
        self.t += dt
        return (datetime.now(), ax, ay, az, self.activity)

sim = ActivitySim()

def get_next_sample():
    if SIM_MODE:
        ts, x, y, z, act = sim.step()
        return ts, x, y, z, act
    else:
        ts, x, y, z = get_live_sample()
        return ts, x, y, z, "live"

# ------------- Dash App -------------
app = Dash(__name__)
app.layout = html.Div([
    html.H2("SIT225 Week 8 — Live Accelerometer (x,y,z)"),
    html.Div("Mode: SIMULATION" if SIM_MODE else "Mode: LIVE (Arduino IoT Cloud)"),
    dcc.Graph(id="xyz-graph"),
    dcc.Graph(id="mag-graph"),
    dcc.Interval(id="tick", interval=1000//SAMPLE_RATE_HZ, n_intervals=0),
    html.Div(id="status", style={"marginTop": "10px", "fontSize": "0.9em"})
])

def df_from_buffer(buf):
    if not buf:
        return pd.DataFrame(columns=["ts","x","y","z","label"])
    df = pd.DataFrame(buf, columns=["ts","x","y","z","label"])
    return df

@app.callback(
    Output("xyz-graph", "figure"),
    Output("mag-graph", "figure"),
    Output("status", "children"),
    Input("tick", "n_intervals")
)
def on_tick(n):
    # 1) Push one sample to buffer_a
    ts, x, y, z, label = get_next_sample()
    buffer_a.append((ts, x, y, z, label))

    # 2) If enough samples, move a window from A to B and save artefacts
    saved_info = ""
    if len(buffer_a) >= N_WINDOW:
        # copy oldest N_WINDOW into buffer_b
        df_a = df_from_buffer(list(buffer_a))
        df_b = df_a.iloc[:N_WINDOW].copy()
        # remove those from A by rebuilding
        remaining = df_a.iloc[N_WINDOW:]
        buffer_a.clear()
        for row in remaining.itertuples(index=False):
            buffer_a.append((row.ts, row.x, row.y, row.z, row.label))
        # assign buffer_b for plotting/saving
        global buffer_b
        buffer_b = df_b.to_dict("records")

        # save CSV + PNG
        ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(DATA_DIR, f"activity_{ts_str}.csv")
        df_b.to_csv(csv_path, index=False)

        # Generate Plotly figures and save static images via kaleido
        # XYZ graph
        fig_xyz = go.Figure()
        fig_xyz.add_trace(go.Scatter(y=df_b["x"], mode="lines", name="x"))
        fig_xyz.add_trace(go.Scatter(y=df_b["y"], mode="lines", name="y"))
        fig_xyz.add_trace(go.Scatter(y=df_b["z"], mode="lines", name="z"))
        fig_xyz.update_layout(title=f"x/y/z (N={len(df_b)})")

        # Magnitude graph
        mag = np.sqrt(df_b["x"]**2 + df_b["y"]**2 + df_b["z"]**2)
        fig_mag = go.Figure()
        fig_mag.add_trace(go.Scatter(y=mag, mode="lines", name="|a|"))
        fig_mag.update_layout(title=f"Acceleration magnitude |a| (N={len(df_b)})")

        # Try image export
        png_xyz_path = os.path.join(SAVE_DIR, f"xyz_{ts_str}.png")
        png_mag_path = os.path.join(SAVE_DIR, f"magnitude_{ts_str}.png")
        try:
            fig_xyz.write_image(png_xyz_path, scale=2, width=1000, height=400)
            fig_mag.write_image(png_mag_path, scale=2, width=1000, height=400)
            saved_info = f"Saved {os.path.basename(csv_path)}, {os.path.basename(png_xyz_path)}, and {os.path.basename(png_mag_path)}"
        except Exception as e:
            saved_info = f"Saved {os.path.basename(csv_path)} (PNG export failed: {e})"

    # 3) Build figures from recent data
    df_recent = df_from_buffer(list(buffer_a)[-min(2000, len(buffer_a)):])
    if len(buffer_b) > 0:
        df_b = pd.DataFrame(buffer_b)
    else:
        df_b = df_recent

    # xyz plot
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(y=df_recent["x"], mode="lines", name="x (recent)"))
    fig1.add_trace(go.Scatter(y=df_recent["y"], mode="lines", name="y (recent)"))
    fig1.add_trace(go.Scatter(y=df_recent["z"], mode="lines", name="z (recent)"))
    fig1.update_layout(title="Recent x, y, z")

    # magnitude plot
    if len(df_recent) > 0:
        mag = np.sqrt(df_recent["x"]**2 + df_recent["y"]**2 + df_recent["z"]**2)
    else:
        mag = []
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(y=mag, mode="lines", name="|a|"))
    fig2.update_layout(title="Acceleration magnitude |a|")

    status = f"samples_in_A={len(buffer_a)} | window_size={N_WINDOW} | {saved_info}"
    return fig1, fig2, status

if __name__ == "__main__":
    print("Starting Dash on http://127.0.0.1:8050 ...")
    app.run(debug=False)
