# SIT225 Week 7 — Data Analysis & Interpretation

This folder contains all code, data, and outputs for SIT225 7.1P.

## Overview
The goal of this task was to:
1. Collect real-world temperature and humidity data from a sensor.
2. Train a Linear Regression model to predict humidity from temperature.
3. Compare three scenarios:
   - All data
   - Quantile-filtered extremes (5%–95%)
   - Outlier-removed (|z| > 2)
4. Analyse and comment on changes in slope, R², and RMSE.

---

## Contents

### **Data**
- `sensor_data.csv` — Raw dataset logged from an ESP32 + DHT11 sensor over ~3 hours.

### **Arduino Code**
- `esp32_dht11_logger.ino` — Arduino sketch for ESP32 + DHT11.  
  Reads temperature and humidity and prints CSV-formatted lines to Serial.

### **Python Logger**
- `esp32_dht11_logger.py` — Python script to capture serial output from the ESP32 and save to `sensor_data.csv`.

### **Analysis Notebook**
- `SIT225_week7_linear_regression.ipynb` — Jupyter Notebook performing:
  - Data loading and cleaning
  - Basic EDA
  - Linear Regression (all data)
  - Quantile-filtered scenario
  - Outlier-removed scenario
  - Plot generation for each scenario
  - Calculation of slope, R², and RMSE for each case

### **Figures**
- `scenario1_full_dataset.png` — Scatter plot + trend line for all data.
- `scenario2_quantile_filtered.png` — Full vs filtered comparison plot.
- `scenario3_outlier_removed.png` — All vs quantile-filtered vs outlier-removed comparison plot.

---

## How to Run

### **1. Arduino**
1. Install the ESP32 board package in Arduino IDE.
2. Install the "Adafruit DHT Sensor" and "Adafruit Unified Sensor" libraries.
3. Open `esp32_dht11_logger.ino` and upload to the ESP32.
4. Confirm temperature/humidity readings appear in Serial Monitor at 115200 baud.

### **2. Python Logger**
```bash
pip install pyserial
python esp32_dht11_logger.py --port <your-port> --baud 115200 --out sensor_data.csv
