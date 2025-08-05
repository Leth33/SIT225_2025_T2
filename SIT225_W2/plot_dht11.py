import matplotlib.pyplot as plt
import csv
from datetime import datetime

timestamps = []
humidity = []
temperature = []

with open('dht11_data.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row
    for row in reader:
        if len(row) != 5:  # New format: timestamp, date, time, humidity, temperature
            continue
        ts, date_str, time_str, hum, temp = row
        try:
            # Parse the timestamp
            dt = datetime.strptime(ts, "%Y%m%d%H%M%S")
            timestamps.append(dt)
            humidity.append(float(hum))
            temperature.append(float(temp))
        except ValueError:
            continue  # Skip any bad data lines

# Create the plot
plt.figure(figsize=(12, 8))

# Create subplots for better visualization
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Plot humidity
ax1.plot(timestamps, humidity, label='Humidity (%)', color='blue', marker='o', markersize=4)
ax1.set_ylabel('Humidity (%)')
ax1.set_title('DHT11 Humidity over Time')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot temperature
ax2.plot(timestamps, temperature, label='Temperature (°C)', color='red', marker='x', markersize=4)
ax2.set_ylabel('Temperature (°C)')
ax2.set_xlabel('Time')
ax2.set_title('DHT11 Temperature over Time')
ax2.grid(True, alpha=0.3)
ax2.legend()

# Format x-axis
plt.xticks(rotation=45)

# Adjust layout
plt.tight_layout()

# Save to file
plt.savefig("dht11_graph.png", dpi=300, bbox_inches='tight')
print("Graph saved as dht11_graph.png")

# Show the plot
plt.show()
