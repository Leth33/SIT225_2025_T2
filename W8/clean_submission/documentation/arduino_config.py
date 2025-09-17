"""
Arduino IoT Cloud Configuration
Replace these values with your actual Arduino IoT Cloud credentials
"""

# Arduino IoT Cloud Credentials
# Get these from: https://create.arduino.cc/iot/
ARDUINO_CLIENT_ID = "jkY0G7r38gpcbzQojvQN7ufpe5FIJCzA"  # You'll need to get this from Arduino IoT Cloud
ARDUINO_CLIENT_SECRET = "dHt2wsy1YDk1gE5KmFtDmyzi9jgmugicUt3zjphmergzvO0lWD8tkzuE4tJulsB4"  # You'll need to get this from Arduino IoT Cloud
ARDUINO_DEVICE_ID = "157c1247-9b93-4244-9783-b4d033ad401a"  # From your Arduino code
ARDUINO_THING_ID = "6e6c3bdf-e3c6-48ba-badc-82c378d3ca23"  # You'll need to get this from Arduino IoT Cloud

# Network credentials (from your Arduino setup)
WIFI_SSID = "WiFi-6C16"
WIFI_PASSWORD = "09249851"
DEVICE_KEY = "M!fFYXQKwAtXjT3H0c0eI0gQa"

# Variable names in your Arduino IoT Cloud thing
# These should match the variable names you created in your thing
ACCEL_X_VARIABLE = "accelerometer_x"
ACCEL_Y_VARIABLE = "accelerometer_y" 
ACCEL_Z_VARIABLE = "accelerometer_z"

# Alternative: Use environment variables (more secure)
import os

# Uncomment these lines if you want to use environment variables instead:
# ARDUINO_CLIENT_ID = os.getenv("ARDUINO_CLIENT_ID", "your_client_id_here")
# ARDUINO_CLIENT_SECRET = os.getenv("ARDUINO_CLIENT_SECRET", "your_client_secret_here")
# ARDUINO_DEVICE_ID = os.getenv("ARDUINO_DEVICE_ID", "your_device_id_here")
# ARDUINO_THING_ID = os.getenv("ARDUINO_THING_ID", "your_thing_id_here")
