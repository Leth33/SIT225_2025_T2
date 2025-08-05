#include <dht.h>

dht DHT;
#define DHT11_PIN 5

void setup() {
  Serial.begin(115200);
  Serial.println("=== DHT11 Temperature & Humidity Monitor ===");
  Serial.println("Status     | Humidity (%) | Temperature (°C)");
  Serial.println("-------------------------------------------");
}

void loop() {
  int chk = DHT.read11(DHT11_PIN);

  // Interpret sensor status
  String status;
  switch (chk) {
    case DHTLIB_OK: status = "OK        "; break;
    case DHTLIB_ERROR_CHECKSUM: status = "Checksum Err"; break;
    case DHTLIB_ERROR_TIMEOUT:  status = "Timeout     "; break;
    case DHTLIB_ERROR_CONNECT:  status = "Connect Err "; break;
    case DHTLIB_ERROR_ACK_L:    status = "Ack Low Err "; break;
    case DHTLIB_ERROR_ACK_H:    status = "Ack High Err"; break;
    default:                    status = "Unknown Err "; break;
  }

  // Print formatted output
  Serial.print(status);
  Serial.print(" | ");
  Serial.print(DHT.humidity, 1);
  Serial.print("         | ");
  Serial.println(DHT.temperature, 1);

  delay(2000);
}