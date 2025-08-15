// ESP32 + DHT11 CSV logger
// Hardware: ESP32 + DHT11 (or DHT22 if you have it)
// Library: Adafruit Unified Sensor + Adafruit DHT sensor library

#include <Arduino.h>
#include "DHT.h"

#define DHTPIN 4      // change to your data pin
#define DHTTYPE DHT11 // use DHT22 if you have it

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  
  Serial.println("timestamp,temperature_C,humidity_pct");
}

void loop() {
  float h = dht.readHumidity();
  float t = dht.readTemperature(); // Celsius

  
  if (isnan(h) || isnan(t)) {
    delay(2000);
    return;
  }

  // ISO timestamp
  time_t now = time(nullptr);
  struct tm *tm_info = localtime(&now);
  char ts[25];
  if (tm_info) {
    strftime(ts, sizeof(ts), "%Y-%m-%dT%H:%M:%S", tm_info);
  } else {
    // Fallback if RTC not set; leave empty to let logger add timestamp
    strcpy(ts, "");
  }

  if (strlen(ts) > 0) {
    Serial.print(ts);
    Serial.print(",");
  }

  Serial.print(t, 2);
  Serial.print(",");
  Serial.println(h, 2);

  delay(2000); // every 2 seconds
}
