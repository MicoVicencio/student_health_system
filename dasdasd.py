import serial
import time

# Change this to your Arduino COM port
COM_PORT = "COM10"      # e.g., "COM9" on Windows or "/dev/ttyUSB0" on Linux
BAUD_RATE = 9600       # Must match Serial.begin(9600) in Arduino code

try:
    # Open serial connection
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # wait for Arduino to reset
    print(f"Connected to {COM_PORT} at {BAUD_RATE} baud")
    
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)

except serial.SerialException:
    print(f"Could not open serial port {COM_PORT}. Check your connection.")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()