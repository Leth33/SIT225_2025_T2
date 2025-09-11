# SIT225 Week 6 – Plotly Dash Gyroscope Dashboard
# Author: (Your Name)
# Usage: python app.py
# This app loads a CSV with columns: time, x, y, z
# and provides interactive controls for chart type, variable selection,
# pagination (N samples + next/prev), and a live summary table.

import os
import math
import pandas as pd
from datetime import datetime
from typing import List
from dash import Dash, dcc, html, Input, Output, State, dash_table, ctx, no_update
import plotly.graph_objs as go

# ---------- CONFIG ----------
DEFAULT_CSV = os.environ.get("GYRO_CSV", "gyro_data.csv")  # override with env var if desired
DATE_COLS = ["time"]
REQUIRED_COLS = ["time", "x", "y", "z"]

app = Dash(__name__)
app.title = "SIT225 Week 6 – Gyro Dashboard"
server = app.server

def load_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        # Create a small demo dataframe so the app still runs.
        # 1200 samples (~2 minutes at 10Hz) as placeholder.
        n = 1200
        t0 = pd.Timestamp.utcnow().floor("s")
        times = pd.date_range(t0, periods=n, freq="100L")  # 10 Hz
        import numpy as np
        x = np.sin(np.linspace(0, 20, n)) * 50 + np.random.normal(0, 2, n)
        y = np.cos(np.linspace(0, 20, n)) * 50 + np.random.normal(0, 2, n)
        z = np.sin(np.linspace(0, 40, n)) * 20 + np.random.normal(0, 1.5, n)
        df_demo = pd.DataFrame({"time": times, "x": x, "y": y, "z": z})
        return df_demo

    try:
        df = pd.read_csv(path)
    except Exception:
        # try with datetime parse
        df = pd.read_csv(path, parse_dates=DATE_COLS, infer_datetime_format=True)

    # Normalize column names
    df.columns = [c.strip().lower() for c in df.columns]
    # Try to coerce time into datetime if not already
    if "time" in df.columns:
        try:
            df["time"] = pd.to_datetime(df["time"], errors="coerce")
        except Exception:
            pass
    # keep only required columns if present
    keep = [c for c in REQUIRED_COLS if c in df.columns]
    df = df[keep]
    df = df.dropna().reset_index(drop=True)
    return df

df = load_csv(DEFAULT_CSV)

def compute_summary(df_slice: pd.DataFrame) -> pd.DataFrame:
    # Return basic stats for x, y, z on the visible slice
    if df_slice.empty:
        return pd.DataFrame({"stat": [], "x": [], "y": [], "z": []})
    stats = ["count", "mean", "std", "min", "max"]
    out = {"stat": stats}
    for col in ["x", "y", "z"]:
        if col in df_slice.columns:
            s = df_slice[col].astype(float, errors="ignore")
            out[col] = [
                int(s.count()),
                s.mean(),
                s.std(),
                s.min(),
                s.max(),
            ]
        else:
            out[col] = [None]*len(stats)
    return pd.DataFrame(out)

GRAPH_TYPES = [
    {"label": "Line", "value": "line"},
    {"label": "Scatter (vs time)", "value": "scatter"},
    {"label": "Distribution (Histogram)", "value": "hist"},
    {"label": "Distribution (Box)", "value": "box"},
    {"label": "Distribution (Violin)", "value": "violin"},
]

VAR_OPTIONS = [{"label": "x", "value": "x"},
               {"label": "y", "value": "y"},
               {"label": "z", "value": "z"}]

app.layout = html.Div([
    html.H2("SIT225 Week 6 – Plotly Dash: Gyroscope (x, y, z)"),
    html.Div(f"Loaded CSV: {DEFAULT_CSV} | Total samples: {len(df)}"),
    dcc.Store(id="current-page", data=0),
    dcc.Store(id="page-size", data=500),
    dcc.Store(id="cached-csv-size", data=len(df)),

    html.Hr(),
    html.Div([
        html.Div([
            html.Label("Chart type"),
            dcc.Dropdown(id="chart-type", options=GRAPH_TYPES, value="line", clearable=False),
        ], style={"flex": 1, "minWidth": 220, "paddingRight": 10}),

        html.Div([
            html.Label("Variables (x/y/z)"),
            dcc.Dropdown(id="vars", options=VAR_OPTIONS, value=["x", "y", "z"], multi=True),
        ], style={"flex": 1, "minWidth": 220, "paddingRight": 10}),

        html.Div([
            html.Label("Samples per page"),
            dcc.Input(id="samples-input", type="number", value=500, min=50, step=50, debounce=True),
        ], style={"flex": 1, "minWidth": 220, "paddingRight": 10}),

        html.Div([
            html.Label("Go to page"),
            dcc.Input(id="goto-page", type="number", value=0, min=0, step=1, debounce=True),
        ], style={"flex": 1, "minWidth": 220, "paddingRight": 10}),

        html.Div([
            html.Label("Reload CSV"),
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Drag and Drop or ", html.A("Select CSV")]),
                multiple=False,
                style={
                    "width": "100%", "height": "42px", "lineHeight": "42px",
                    "borderWidth": "1px", "borderStyle": "dashed",
                    "borderRadius": "6px", "textAlign": "center"
                }
            ),
        ], style={"flex": 1, "minWidth": 220}),
    ], style={"display": "flex", "flexWrap": "wrap", "gap": "8px"}),

    html.Div([
        html.Button("⟵ Prev", id="prev-btn", n_clicks=0, style={"marginRight": "8px"}),
        html.Button("Next ⟶", id="next-btn", n_clicks=0),
    ], style={"marginTop": "10px"}),

    html.Hr(),
    dcc.Graph(id="main-graph"),
    html.H4("Summary of visible data"),
    dash_table.DataTable(
        id="summary-table",
        columns=[{"name": c, "id": c} for c in ["stat", "x", "y", "z"]],
        data=[],
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "6px"},
        style_header={"fontWeight": "bold"}
    ),
    html.Div(id="page-info", style={"marginTop": "8px", "fontStyle": "italic"}),
])

def get_slice(df: pd.DataFrame, page: int, page_size: int) -> pd.DataFrame:
    total = len(df)
    start = max(0, page * page_size)
    end = min(total, start + page_size)
    return df.iloc[start:end].reset_index(drop=True)

def make_fig(chart_type: str, df_slice: pd.DataFrame, vars_selected: List[str]) -> go.Figure:
    fig = go.Figure()
    if df_slice.empty or not vars_selected:
        fig.update_layout(title="No data to display")
        return fig

    if chart_type in ("line", "scatter"):
        for v in vars_selected:
            mode = "lines" if chart_type == "line" else "markers"
            fig.add_trace(go.Scatter(x=df_slice["time"], y=df_slice[v], mode=mode, name=v))
        fig.update_layout(xaxis_title="time", yaxis_title="value")
    elif chart_type == "hist":
        for v in vars_selected:
            fig.add_trace(go.Histogram(x=df_slice[v], name=v, opacity=0.75))
        fig.update_layout(barmode="overlay", xaxis_title="value", yaxis_title="count")
    elif chart_type == "box":
        for v in vars_selected:
            fig.add_trace(go.Box(y=df_slice[v], name=v, boxmean=True))
        fig.update_layout(yaxis_title="value")
    elif chart_type == "violin":
        for v in vars_selected:
            fig.add_trace(go.Violin(y=df_slice[v], name=v, box_visible=True, meanline_visible=True))
        fig.update_layout(yaxis_title="value")

    fig.update_layout(hovermode="x unified")
    return fig

# ---------- Callbacks ----------

@app.callback(
    Output("main-graph", "figure"),
    Output("summary-table", "data"),
    Output("current-page", "data"),
    Output("page-size", "data"),
    Output("page-info", "children"),
    Input("chart-type", "value"),
    Input("vars", "value"),
    Input("samples-input", "value"),
    Input("prev-btn", "n_clicks"),
    Input("next-btn", "n_clicks"),
    Input("goto-page", "value"),
    State("current-page", "data"),
    State("page-size", "data"),
)
def update_graph(chart_type, vars_selected, samples_value, n_prev, n_next, goto_page, cur_page, cur_size):
    global df
    trigger = ctx.triggered_id
    page = cur_page or 0
    page_size = cur_size or 500

    if isinstance(samples_value, int) and samples_value > 0:
        page_size = samples_value

    if trigger == "prev-btn":
        page = max(0, page - 1)
    elif trigger == "next-btn":
        page = page + 1
    elif trigger == "goto-page" and isinstance(goto_page, int) and goto_page >= 0:
        page = goto_page

    max_page = max(0, math.ceil(len(df) / page_size) - 1)
    page = min(page, max_page)

    df_slice = get_slice(df, page, page_size)
    fig = make_fig(chart_type or "line", df_slice, vars_selected or ["x", "y", "z"])
    summary = compute_summary(df_slice).round(3).to_dict("records")
    info = f"Page {page} / {max_page} | showing {len(df_slice)} of {len(df)} samples (page size = {page_size})"
    return fig, summary, page, page_size, info

@app.callback(
    Output("cached-csv-size", "data"),
    Input("upload-data", "contents"),
    State("upload-data", "filename")
)
def upload_csv(contents, filename):
    # Simple hot reload: save uploaded CSV to DEFAULT_CSV name and reload module-level df
    global df
    if contents is None:
        return len(df)
    import base64, io
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        new_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    except Exception:
        new_df = pd.read_csv(io.BytesIO(decoded))
    new_df.columns = [c.strip().lower() for c in new_df.columns]
    if "time" in new_df.columns:
        try:
            new_df["time"] = pd.to_datetime(new_df["time"], errors="coerce")
        except Exception:
            pass
    df = new_df.dropna().reset_index(drop=True)
    # Persist
    try:
        df.to_csv(DEFAULT_CSV, index=False)
    except Exception:
        pass
    return len(df)

if __name__ == "__main__":
    app.run_server(debug=True)
