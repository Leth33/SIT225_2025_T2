#include <Arduino_LSM6DS3.h>

// Target sampling period in milliseconds (e.g., 20 ms -> ~50 Hz)
const unsigned long SAMPLE_PERIOD_MS = 20; 

void setup() {
  Serial.begin(115200);
  while (!Serial) { ; } // Wait for Serial

  if (!IMU.begin()) {
    Serial.println("ERROR: Failed to initialize IMU (LSM6DS3).");
    while (true) { delay(1000); }
  }

  Serial.println("# nano33_gyro_logger started");
  Serial.print("# Gyro sample rate (Hz): ");
  Serial.println(IMU.gyroscopeSampleRate());

  // Optional: stabilize
  delay(500);
}

void loop() {
  static unsigned long last = 0;
  unsigned long now = millis();
  if (now - last < SAMPLE_PERIOD_MS) return;
  last = now;

  float gx, gy, gz;
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(gx, gy, gz);
    Serial.print(",");
    Serial.print(gx, 6); Serial.print(",");
    Serial.print(gy, 6); Serial.print(",");
    Serial.println(gz, 6);
  }
}