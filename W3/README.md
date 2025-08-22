# 🌡️ Week 3 IoT Assessment – ESP32 + DHT11 + Arduino IoT Cloud  

This project demonstrates **live environmental data capture** using a **Keyestudio ESP32 Dev Module** with a **DHT11 temperature & humidity sensor**.  
Data is streamed to **Arduino IoT Cloud**, visualized with gauges and charts, and exported as CSV for optional Python analysis.  

---

## ⚙️ Hardware Setup
- **ESP32 Dev Module (Keyestudio)**
- **DHT11 Sensor (3-pin)**
  - VCC → 3.3V  
  - GND → GND  
  - DATA → GPIO 4  

---

## 💻 Software Setup
- **Arduino IDE** with:
  - [Adafruit DHT Sensor Library](https://github.com/adafruit/DHT-sensor-library)  
  - [Adafruit Unified Sensor Library](https://github.com/adafruit/Adafruit_Sensor)  
- **Arduino IoT Cloud** (for live monitoring & dashboards)  
- **Python (optional)** for CSV analysis with Pandas & Matplotlib  

---

## ☁️ Cloud Configuration
In **Arduino IoT Cloud**, a *Thing* was created with 3 variables:  
- `Temperature (°C)`  
- `Humidity (%)`  
- `Message (String)`  

### Dashboard Widgets  
- 2️⃣ Gauges → Real-time Temperature & Humidity  
- 2️⃣ Charts → Track values over time  
- 1️⃣ Message box → Simple text communication  

---

## 📊 Results
- The ESP32 successfully streamed **live sensor readings** to Arduino IoT Cloud.  
- Gauges showed **real-time values**, while charts tracked **trends over 10+ minutes**.  
- Data was also **exported as CSV** for offline use.  

---

## 📝 Discussion & Conclusion
I successfully captured and visualized environmental data using the ESP32 and DHT11.  
The system demonstrated a **full IoT workflow**:  

- Data capture with hardware  
- Live monitoring in Arduino IoT Cloud  
- Historical data export (CSV)  
- Optional offline analysis with Python  

Some technical challenges (e.g., serial port access & SSL issues) were resolved, showing the importance of debugging both hardware and software in IoT projects.  

✅ This setup met the assessment requirements and proved the usefulness of IoT platforms for real-time monitoring and deeper analysis.  

---

## 📂 Repository Contents
