import serial
import time
from datetime import datetime
import re

ser = serial.Serial('/dev/cu.usbmodem11101', 115200)
filename = "dht11_data.csv"

# Write CSV header if file is empty
with open(filename, "a") as file:
    if file.tell() == 0:  # File is empty
        file.write("Timestamp,Date,Time,Humidity (%),Temperature (°C)\n")
        file.flush()

with open(filename, "a") as file:
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            # Look for lines with the format: "OK         | 56.0         | 17.0"
            if '|' in line and 'OK' in line:
                # Extract humidity and temperature values
                parts = line.split('|')
                if len(parts) >= 3:
                    humidity = parts[1].strip()
                    temperature = parts[2].strip()
                    # Extract numeric values
                    humidity_match = re.search(r'(\d+\.?\d*)', humidity)
                    temp_match = re.search(r'(\d+\.?\d*)', temperature)
                    
                    if humidity_match and temp_match:
                        humidity_val = humidity_match.group(1)
                        temp_val = temp_match.group(1)
                        
                        # Create readable timestamp
                        now = datetime.now()
                        timestamp = now.strftime("%Y%m%d%H%M%S")
                        date_str = now.strftime("%Y-%m-%d")
                        time_str = now.strftime("%H:%M:%S")
                        
                        # Write to CSV
                        file.write(f"{timestamp},{date_str},{time_str},{humidity_val},{temp_val}\n")
                        file.flush()  # Force write to disk :))
                        
                        # Print formatted output
                        print(f"[{time_str}] Humidity: {humidity_val}% | Temperature: {temp_val}°C")
        except KeyboardInterrupt:
            print("\nData collection stopped.")
            break
