const int LED_PIN = LED_BUILTIN;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(9600);
  Serial.setTimeout(2000); // 2s read timeout
}

void loop() {
  if (Serial.available() > 0) {
    long n = Serial.parseInt();          
    if (n <= 0) return;                  

    // Blink N times for visual confirmation (1/2 s on + 1/2 s off)
    for (long i = 0; i < n; i++) {
      digitalWrite(LED_PIN, HIGH);
      delay(500);
      digitalWrite(LED_PIN, LOW);
      delay(500);
    }

    // Wait N seconds BEFORE responding
    delay(n * 1000);

    // Respond with N+1 (this fixes “48 -> 49”)
    Serial.println(n + 1);
  }
}
