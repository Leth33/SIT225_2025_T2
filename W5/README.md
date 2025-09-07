# SIT225 Week 5: Store data to cloud

A complete data capture and analysis system for Arduino Nano 33 IoT gyroscope data using Firebase Realtime Database.

## Overview

This project implements a 3-stage pipeline:
1. **Data Collection**: Arduino reads gyroscope data and sends via Serial
2. **Cloud Storage**: Python script receives data and pushes to Firebase
3. **Analysis**: Export data from Firebase and generate visualizations

## Hardware Requirements

- Arduino Nano 33 IoT (with LSM6DS3 IMU)
- USB cable for serial communication
- Computer with Python 3.7+

## Software Setup

### 1. Arduino IDE Setup

1. Install Arduino IDE
2. Install Arduino_LSM6DS3 library:
   - Go to Tools → Manage Libraries
   - Search for "Arduino_LSM6DS3"
   - Install the library by Arduino

### 2. Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install pyserial requests pandas matplotlib scipy
```

### 3. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing one
3. Enable Realtime Database:
   - Go to "Realtime Database" in left sidebar
   - Click "Create Database"
   - Choose "Start in test mode" (for development)
   - Select a location (e.g., asia-southeast1)
4. Note your database URL (e.g., `https://your-project-id.asia-southeast1.firebasedatabase.app/`)

## Arduino Code

Upload this code to your Arduino Nano 33 IoT:

```cpp
#include <Arduino_LSM6DS3.h>

void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  
  Serial.println("Gyroscope data logger ready");
  Serial.println("Format: ,gx,gy,gz");
}

void loop() {
  float gx, gy, gz;
  
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(gx, gy, gz);
    Serial.print(",");
    Serial.print(gx);
    Serial.print(",");
    Serial.print(gy);
    Serial.print(",");
    Serial.println(gz);
  }
  
  delay(20); // ~50Hz sampling rate
}
```

## Python Pipeline Usage

### 1. Data Collection (Listen Mode)

```bash
# Basic usage
python firebase_gyro_pipeline.py listen --port /dev/tty.usbmodem1301 --db-url https://your-project-id.asia-southeast1.firebasedatabase.app

# With custom path and authentication
python firebase_gyro_pipeline.py listen \
  --port /dev/tty.usbmodem1301 \
  --baud 115200 \
  --db-url https://your-project-id.asia-southeast1.firebasedatabase.app \
  --path sessions/session1 \
  --auth your_database_secret \
  --max-samples 1000
```

**Finding your serial port:**
- **macOS**: `ls /dev/tty.usbmodem*`
- **Windows**: Check Device Manager → Ports (COM & LPT)
- **Linux**: `ls /dev/ttyUSB*` or `ls /dev/ttyACM*`

### 2. Data Export (Export Mode)

```bash
# Export data from Firebase to CSV
python firebase_gyro_pipeline.py export \
  --db-url https://your-project-id.asia-southeast1.firebasedatabase.app \
  --path sessions/session1 \
  --out gyro_data.csv \
  --auth your_database_secret
```

### 3. Data Visualization (Plot Mode)

```bash
# Generate plots from CSV data
python firebase_gyro_pipeline.py plot --csv gyro_data.csv
```

This creates 4 PNG files:
- `gyro_data_gx.png` - X-axis (pitch) rotation
- `gyro_data_gy.png` - Y-axis (roll) rotation  
- `gyro_data_gz.png` - Z-axis (yaw) rotation
- `gyro_data_combined.png` - All axes combined

## Complete Workflow Example

```bash
# 1. Start data collection (run for 30+ minutes)
python firebase_gyro_pipeline.py listen \
  --port /dev/tty.usbmodem1301 \
  --db-url https://sit225-gyro-data-default-rtdb.asia-southeast1.firebasedatabase.app \
  --path sessions/session1

# 2. Export data to CSV
python firebase_gyro_pipeline.py export \
  --db-url https://sit225-gyro-data-default-rtdb.asia-southeast1.firebasedatabase.app \
  --path sessions/session1 \
  --out gyro_data_final.csv

# 3. Generate visualizations
python firebase_gyro_pipeline.py plot --csv gyro_data_final.csv
```

## Command Line Options

### Listen Mode
- `--port`: Serial port (required)
- `--baud`: Baud rate (default: 115200)
- `--db-url`: Firebase database URL (required)
- `--path`: Database path (default: sessions/session1)
- `--auth`: Database secret or ID token (optional)
- `--max-samples`: Stop after N samples (default: 0 = unlimited)

### Export Mode
- `--db-url`: Firebase database URL (required)
- `--path`: Database path (default: sessions/session1)
- `--auth`: Database secret or ID token (optional)
- `--out`: Output CSV filename (default: gyro_data.csv)

### Plot Mode
- `--csv`: Input CSV filename (required)

## Data Format

### Serial Input Format
```
,gx,gy,gz
,0.0,-0.305176,-0.183105
,-0.305176,-0.366211,-0.183105
```

### Firebase JSON Format
```json
{
  "sessions": {
    "session1": {
      "-OZWlt_ysO1O9wyjGi35": {
        "ts": "2025-09-07T01:25:52.833+00:00",
        "gx": 0.0,
        "gy": -0.305176,
        "gz": -0.183105
      }
    }
  }
}
```

### CSV Output Format
```csv
ts,gx,gy,gz
2025-09-07 01:25:52.833000+00:00,0.0,-0.305176,-0.183105
2025-09-07 01:25:53.116000+00:00,-0.305176,-0.366211,-0.183105
```

## Troubleshooting

### Common Issues

1. **Serial Port Not Found**
   - Check USB connection
   - Verify Arduino is powered on
   - Try different USB ports
   - Check device permissions (Linux/macOS)

2. **Firebase Connection Failed**
   - Verify database URL is correct
   - Check internet connection
   - Ensure database rules allow writes
   - Try with `--auth` parameter

3. **Permission Denied (macOS/Linux)**
   ```bash
   sudo chmod 666 /dev/tty.usbmodem1301
   ```

4. **Import Errors**
   - Ensure virtual environment is activated
   - Install missing packages: `pip install package_name`

### Data Quality Issues

- **Missing samples**: Check serial connection stability
- **Invalid values**: Verify Arduino code is correct
- **Timing issues**: Adjust sampling rate in Arduino code

## Project Structure

```
W5/
├── firebase_gyro_pipeline.py    # Main Python script
├── nano33_gyro_logger.ino       # Arduino sketch
├── gyro_data_final.csv          # Exported data (7,953 samples)
├── gyro_data_final_*.png        # Generated plots
├── sit225_Gyro_Data_Export.json # Raw Firebase data
├── SIT225_Week5_Answers.txt     # Assignment answers
├── README.md                    # This file
└── venv/                        # Python virtual environment
```

## Results Summary

**Dataset Characteristics:**
- Duration: 40.5 minutes
- Samples: 7,953
- Data rate: 3.27 samples/second
- Data quality: 100% (0 invalid rows)

**Statistical Analysis:**
- **GX (Pitch)**: Range -16.7 to +15.6 deg/s, σ=1.4
- **GY (Roll)**: Range -2.2 to +0.2 deg/s, σ=0.045
- **GZ (Yaw)**: Range -0.7 to +1.0 deg/s, σ=0.045

## References

- [Arduino Nano 33 IoT IMU Tutorial](https://docs.arduino.cc/tutorials/nano-33-iot/imu-gyroscope)
- [Firebase Realtime Database REST API](https://firebase.google.com/docs/database/rest/start)
- [SIT225 Data Capture Technologies](https://www.deakin.edu.au/study/course/sit225)

## License

This project is part of SIT225 Data Capture Technologies coursework at Deakin University.
