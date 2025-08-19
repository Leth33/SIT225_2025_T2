import serial, time, sys
from datetime import datetime

PORT = "/dev/cu.usbmodem11301"
BAUD = 9600

def send_and_time(ser, n):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] Sending: {n}")
    ser.reset_input_buffer()
    ser.write(f"{n}\n".encode())

    t0 = time.time()
    line = ser.readline().decode(errors="ignore").strip()  # waits for Arduino reply
    t1 = time.time()

    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] Received: {line}")
    elapsed = t1 - t0
    print(f"Elapsed: {elapsed:.2f} seconds\n")
    return line, elapsed

def expect_delay_seconds(measured, n, multiplier=2.0, tol=0.8):

    expected = multiplier * n
    lower = expected - tol
    upper = expected + tol
    assert lower <= measured <= upper, f"Expected ~{expected:.0f}s delay, measured {measured:.2f}s"

def main():
    try:
        
        with serial.Serial(PORT, BAUD, timeout=150) as ser:
            time.sleep(2)  # let Arduino reset

            # Test 1: 48 -> 49 (~96 s delay)
            line, dt = send_and_time(ser, 48)
            assert line == "49", f"Expected 49, got {line}"
            expect_delay_seconds(dt, 48)

            # Test 2: 3 -> 4 (~6 s delay)
            line, dt = send_and_time(ser, 3)
            assert line == "4", f"Expected 4, got {line}"
            expect_delay_seconds(dt, 3)

            print("✅ Tests passed (2N delay version).")
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
