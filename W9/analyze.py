# analyze.py
# Analysis script for Desk Coach Lite (IMU data)
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

CSV = "deskcoach_session.csv"

def main():
    # Load data
    df = pd.read_csv(CSV)
    print("Columns found:", df.columns.tolist())
    print("Data shape:", df.shape)
    
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp_iso"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    
    # Convert pitch_deg to numeric
    df["pitch_deg"] = pd.to_numeric(df["pitch_deg"], errors="coerce")
    
    # Calculate baseline pitch from first 10 readings
    BASELINE_PITCH = df["pitch_deg"].dropna().iloc[:10].mean() if len(df["pitch_deg"].dropna()) > 0 else 0.0
    SLOUCH_DELTA = 8.0
    
    print(f"Baseline pitch: {BASELINE_PITCH:.1f} degrees")
    print(f"Slouch threshold: {BASELINE_PITCH + SLOUCH_DELTA:.1f}° (upper), {BASELINE_PITCH - SLOUCH_DELTA:.1f}° (lower)")
    print(f"Max pitch in data: {df['pitch_deg'].max():.1f}°")
    print(f"Min pitch in data: {df['pitch_deg'].min():.1f}°")
    
    # Label posture states
    df["posture_state"] = np.where(
        (df["pitch_deg"] > BASELINE_PITCH + SLOUCH_DELTA) | 
        (df["pitch_deg"] < BASELINE_PITCH - SLOUCH_DELTA), 
        "SLOUCH", 
        "OK"
    )
    
    # Calculate session duration
    duration_min = (df["timestamp"].max() - df["timestamp"].min()).total_seconds() / 60
    slouch_pct = (df["posture_state"] == "SLOUCH").mean() * 100
    
    # Debug: Show slouching readings
    slouch_readings = df[df["posture_state"] == "SLOUCH"]
    print(f"\nSlouching readings found: {len(slouch_readings)}")
    if len(slouch_readings) > 0:
        print("Sample slouching readings:")
        print(slouch_readings[["timestamp", "pitch_deg", "posture_state"]].head())
    
    # Summary KPIs
    kpi = {
        "Duration_min": round(duration_min, 1),
        "Pct_Slouch": round(slouch_pct, 3),
        "Baseline_pitch_deg": round(BASELINE_PITCH, 1),
        "Min_pitch_deg": round(df["pitch_deg"].min(), 1),
        "Max_pitch_deg": round(df["pitch_deg"].max(), 1),
        "Avg_pitch_deg": round(df["pitch_deg"].mean(), 1)
    }
    
    print("\n=== SESSION ANALYSIS ===")
    for key, value in kpi.items():
        print(f"{key}: {value}")
    
    # Create plots using matplotlib (more reliable)
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(df["timestamp"], df["pitch_deg"], linewidth=1, alpha=0.7, label="Pitch")
        
        # Add baseline and threshold lines
        plt.axhline(y=BASELINE_PITCH, color='green', linestyle='--', 
                   label=f'Baseline ({BASELINE_PITCH}°)')
        plt.axhline(y=BASELINE_PITCH + SLOUCH_DELTA, color='red', linestyle='--', 
                   label=f'Slouch Threshold ({BASELINE_PITCH + SLOUCH_DELTA}°)')
        plt.axhline(y=BASELINE_PITCH - SLOUCH_DELTA, color='red', linestyle='--')
        
        # Formatting
        plt.title("Chair Pitch Over Time - Desk Coach Session")
        plt.xlabel("Time")
        plt.ylabel("Pitch (degrees)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        plt.xticks(rotation=45)
        
        # Save plot
        plt.tight_layout()
        plt.savefig("plot_pitch.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Saved: plot_pitch.png")
        
        # Create a summary plot with key statistics
        plt.figure(figsize=(10, 6))
        categories = ['Duration\n(min)', 'Slouching\n(%)', 'Min Pitch\n(°)', 'Max Pitch\n(°)', 'Avg Pitch\n(°)']
        values = [kpi['Duration_min'], kpi['Pct_Slouch'], kpi['Min_pitch_deg'], 
                 kpi['Max_pitch_deg'], kpi['Avg_pitch_deg']]
        colors = ['blue', 'green' if kpi['Pct_Slouch'] == 0 else 'orange', 'purple', 'red', 'teal']
        
        bars = plt.bar(categories, values, color=colors, alpha=0.7)
        plt.title("Desk Coach Session Summary")
        plt.ylabel("Values")
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    f'{value}', ha='center', va='bottom', fontweight='bold')
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.savefig("plot_summary.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Saved: plot_summary.png")
        
    except Exception as e:
        print(f"Plotting not available: {e}")
    
    # Save summary
    summary = (
        f"Duration (min): {kpi['Duration_min']}\n"
        f"Slouching (%): {kpi['Pct_Slouch']}\n"
        f"Baseline pitch (deg): {kpi['Baseline_pitch_deg']}\n"
        f"Pitch range: {kpi['Min_pitch_deg']} to {kpi['Max_pitch_deg']}\n"
        f"Average pitch (deg): {kpi['Avg_pitch_deg']}\n"
    )
    
    Path("session_summary.txt").write_text(summary, encoding="utf-8")
    print(f"\nSession summary saved to session_summary.txt")
    
    # Show sample data
    print(f"\nFirst 5 readings:")
    print(df[["timestamp", "pitch_deg", "posture_state"]].head())
    print(f"\nLast 5 readings:")
    print(df[["timestamp", "pitch_deg", "posture_state"]].tail())

if __name__ == "__main__":
    main()
