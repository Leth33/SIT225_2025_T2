import pandas as pd
import matplotlib.pyplot as plt
import sys

if len(sys.argv) < 3:
    print("Usage: python analysis_week3.py week3_temperature.csv week3_humidity.csv")
    sys.exit(1)

temp_file, hum_file = sys.argv[1], sys.argv[2]

# Load both CSVs
df_temp = pd.read_csv(temp_file)
df_hum = pd.read_csv(hum_file)

# Rename columns for clarity
df_temp = df_temp.rename(columns={"time": "timestamp", "value": "temperature_c"})
df_hum = df_hum.rename(columns={"time": "timestamp", "value": "humidity"})

# Convert timestamps to datetime
df_temp["timestamp"] = pd.to_datetime(df_temp["timestamp"])
df_hum["timestamp"] = pd.to_datetime(df_hum["timestamp"])

# Merge on timestamp (inner join to get only matching timestamps)
df = pd.merge(df_temp, df_hum, on="timestamp", how="inner")

# Sort by timestamp
df = df.sort_values("timestamp")

# Save merged CSV
df.to_csv("week3_dht_data.csv", index=False)

print(f"Merged data shape: {df.shape}")
print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")

# Plot temperature
plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["temperature_c"], label="Temperature (°C)", linewidth=2)
plt.xticks(rotation=45)
plt.ylabel("Temperature (°C)")
plt.xlabel("Time")
plt.title("Temperature over Time")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("week3_temp.png", dpi=300, bbox_inches='tight')
plt.close()

# Plot humidity
plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["humidity"], color="orange", label="Humidity (%)", linewidth=2)
plt.xticks(rotation=45)
plt.ylabel("Humidity (%)")
plt.xlabel("Time")
plt.title("Humidity over Time")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("week3_hum.png", dpi=300, bbox_inches='tight')
plt.close()

# Combined plot
fig, ax1 = plt.subplots(figsize=(14, 8))

# Temperature on left y-axis
color1 = 'tab:blue'
ax1.set_xlabel('Time')
ax1.set_ylabel('Temperature (°C)', color=color1)
ax1.plot(df["timestamp"], df["temperature_c"], color=color1, linewidth=2, label="Temperature (°C)")
ax1.tick_params(axis='y', labelcolor=color1)
ax1.grid(True, alpha=0.3)

# Humidity on right y-axis
ax2 = ax1.twinx()
color2 = 'tab:orange'
ax2.set_ylabel('Humidity (%)', color=color2)
ax2.plot(df["timestamp"], df["humidity"], color=color2, linewidth=2, label="Humidity (%)")
ax2.tick_params(axis='y', labelcolor=color2)

# Rotate x-axis labels
plt.xticks(rotation=45)

# Add legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.title("Temperature and Humidity Over Time")
plt.tight_layout()
plt.savefig("week3_combined.png", dpi=300, bbox_inches='tight')
plt.close()

print("Done: Saved week3_dht_data.csv and 3 plots")
print("Files created:")
print("- week3_dht_data.csv (merged data)")
print("- week3_temp.png (temperature plot)")
print("- week3_hum.png (humidity plot)")
print("- week3_combined.png (combined plot)")
