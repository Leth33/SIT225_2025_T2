import serial
import time
import random
from datetime import datetime

arduino = serial.Serial('COM10', 9600)
time.sleep(2)

while True:
    num = random.randint(1, 5)
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] Sending: {num}")
    arduino.write(f"{num}\n".encode())

    while arduino.in_waiting == 0:
        pass

    received = arduino.readline().decode().strip()
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] Received: {received}")
    time.sleep(int(received))
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Sleeping done\n")
